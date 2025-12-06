from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from datetime import datetime, timedelta, date
from .models import AppointmentSlot, DoctorPost
from django.contrib.auth.models import User
from calendar_integration.utils import create_event, delete_event
from mini_HMS.utils import trigger_email

# --- HELPER FUNCTIONS ---

def cleanup_stale_slots():
    """Rule 1: Delete older slots if no one booked."""
    now = datetime.now()
    current_date = now.date()
    current_time = now.time()

    AppointmentSlot.objects.filter(is_booked=False, date__lt=current_date).delete()
    AppointmentSlot.objects.filter(
        is_booked=False, 
        date=current_date, 
        start_time__lt=current_time
    ).delete()

def is_slot_too_soon(slot_date, slot_start_time):
    """Rule 2 Helper: Checks if slot is < 1 hour from now."""
    now_naive = datetime.now()
    slot_naive = datetime.combine(slot_date, slot_start_time)
    # Check if slot is within the next hour
    return slot_naive < (now_naive + timedelta(hours=1))


# --- DOCTOR VIEWS ---

@login_required
def doctor_dashboard(request):
    if request.method == "POST":
        content = request.POST.get('content')
        if content:
            DoctorPost.objects.create(author=request.user, content=content)
            messages.success(request, "Post shared with the community!")
            return redirect('doctor_dashboard')

    posts = DoctorPost.objects.all()
    return render(request, 'appointments/doctor_dashboard.html', {'posts': posts})


@login_required
def my_schedule(request):
    # Only doctors need to trigger cleanup when managing their schedule
    cleanup_stale_slots()

    if request.method == 'POST':
        date_str = request.POST.get('date')
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')

        try:
            slot_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            slot_start = datetime.strptime(start_time_str, "%H:%M").time()
            
            if is_slot_too_soon(slot_date, slot_start):
                messages.error(request, "Invalid Slot: You must schedule at least 1 hour in advance.")
                return redirect('my_schedule')

            AppointmentSlot.objects.create(
                doctor=request.user,
                date=date_str,
                start_time=start_time_str,
                end_time=end_time_str
            )
            messages.success(request, "Availability slot added successfully!")
            
        except ValueError:
            messages.error(request, "Invalid date or time format.")
        except Exception:
            messages.error(request, "Error adding slot. It might already exist.")
        
        return redirect('my_schedule')

    slots = AppointmentSlot.objects.filter(doctor=request.user).order_by('date', 'start_time')
    return render(request, 'appointments/my_schedule.html', {'slots': slots})

@login_required
def delete_slot(request, slot_id):
    slot = get_object_or_404(AppointmentSlot, id=slot_id)
    if slot.doctor == request.user:
        slot.delete()
        messages.success(request, "Slot removed.")
    else:
        messages.error(request, "Unauthorized.")
    return redirect('my_schedule') 

@login_required
def cancel_appointment(request, slot_id):
    slot = get_object_or_404(AppointmentSlot, id=slot_id)
    
    if request.user == slot.doctor:
        actor = 'doctor'
        redirect_url = 'my_schedule'
    elif request.user == slot.patient:
        actor = 'patient'
        redirect_url = 'patient_dashboard'
    else:
        messages.error(request, "Unauthorized action.")
        return redirect('home')

    if not slot.cancel_request_by:
        slot.cancel_request_by = actor
        slot.save()
        messages.info(request, "Cancellation requested. Waiting for approval.")
    
    elif slot.cancel_request_by == actor:
        messages.warning(request, "You have already requested cancellation.")
        
    else:
        # --- APPROVED CANCELLATION --- 
           
        # 1. Capture details BEFORE clearing data
        # Optimization: Use the new model method
        email_data = {
            "name": slot.patient.first_name if slot.patient else "Patient",
            "doctor_name": slot.doctor.first_name,
            "patient_name": slot.patient.first_name if slot.patient else "Patient",
            "date": str(slot.date),
            "time": slot.get_time_range() # <--- Cleaner call
        }
        
        patient_email = slot.patient.email if slot.patient else None
        doctor_email = slot.doctor.email

        # 2. Delete Calendar Events
        if slot.doctor_google_event_id:
            delete_event(slot.doctor, slot.doctor_google_event_id)
        if slot.patient_google_event_id:
            delete_event(slot.patient, slot.patient_google_event_id)

        # 3. Clear Database
        slot.patient = None
        slot.is_booked = False
        slot.cancel_request_by = None
        slot.doctor_google_event_id = None
        slot.patient_google_event_id = None
        slot.save()

        # 4. Trigger Cancellation Emails
        if patient_email:
            trigger_email(
                action="BOOKING_CANCELLATION",
                recipient_email=patient_email,
                data=email_data
            )

        trigger_email(
            action="DOCTOR_SLOT_CANCELLED",
            recipient_email=doctor_email,
            data=email_data
        )

        messages.success(request, "Cancellation approved. Appointment removed from Calendar.")

    return redirect(redirect_url)


# --- PATIENT VIEWS ---
@login_required
def patient_dashboard(request):
    # Optimization: Removed cleanup_stale_slots() call here for performance.
    
    today = datetime.now().date()
    
    raw_slots = AppointmentSlot.objects.filter(
        is_booked=False, 
        date__gte=today
    ).order_by('date', 'start_time')

    # Filter out slots less than 1 hour away
    available_slots = [slot for slot in raw_slots if not is_slot_too_soon(slot.date, slot.start_time)]

    my_bookings = AppointmentSlot.objects.filter(patient=request.user).order_by('date')
    return render(request, 'appointments/patient_dashboard.html', {'available_slots': available_slots, 'my_bookings': my_bookings})

@login_required
def book_slot(request, slot_id):
    with transaction.atomic():
        try:
            slot = AppointmentSlot.objects.select_for_update().get(id=slot_id)
            
            # 1. Concurrency Check
            if slot.is_booked:
                messages.error(request, "Sorry, this slot was just booked by someone else.")
                return redirect('patient_dashboard')

            # 2. Rule Check
            if is_slot_too_soon(slot.date, slot.start_time):
                 messages.error(request, "This slot is no longer available (must be booked 1 hour in advance).")
                 return redirect('patient_dashboard')

            # 3. Conflict Check
            has_conflict = AppointmentSlot.objects.filter(
                patient=request.user,
                date=slot.date,
                start_time__lt=slot.end_time,
                end_time__gt=slot.start_time
            ).exists()

            if has_conflict:
                messages.error(request, "You already have a booking overlapping this time.")
                return redirect('patient_dashboard')

            # 4. Book
            slot.is_booked = True
            slot.patient = request.user
            
            # --- GOOGLE CALENDAR INTEGRATION ---
            start_dt = datetime.combine(slot.date, slot.start_time)
            end_dt = datetime.combine(slot.date, slot.end_time)

            # Doctor Event
            doc_id = create_event(
                user=slot.doctor,
                summary=f"Appointment with {slot.patient.first_name}",
                description=f"Patient Mobile: {slot.patient.profile.mobile}",
                start_dt=start_dt, end_dt=end_dt
            )
            slot.doctor_google_event_id = doc_id

            # Patient Event
            pat_id = create_event(
                user=slot.patient,
                summary=f"Appointment with Dr. {slot.doctor.first_name}",
                description=f"Doctor Mobile: {slot.doctor.profile.mobile}",
                start_dt=start_dt, end_dt=end_dt
            )
            slot.patient_google_event_id = pat_id

            slot.save()

            # --- TRIGGER CONFIRMATION EMAIL ---
            
            # Optimization: Use new model method
            email_data = {
                "patient_name": slot.patient.first_name,
                "doctor_name": slot.doctor.first_name,
                "date": str(slot.date),
                "time": slot.get_time_range() # <--- Cleaner call
            }

            # 1. Email to PATIENT
            trigger_email(
                action="BOOKING_CONFIRMATION",
                recipient_email=slot.patient.email,
                data=email_data
            )

            # 2. Email to DOCTOR
            trigger_email(
                action="DOCTOR_NEW_BOOKING",
                recipient_email=slot.doctor.email,
                data=email_data
            )

            messages.success(request, f"Appointment confirmed with Dr. {slot.doctor.first_name}. Appointment added to Calendar.")
                
        except AppointmentSlot.DoesNotExist:
            messages.error(request, "Slot does not exist.")
            
    return redirect('patient_dashboard')

@login_required
def find_doctor(request):
    doctors = User.objects.filter(profile__role='doctor')
    return render(request, 'appointments/find_doctor.html', {'doctors': doctors})