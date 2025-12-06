from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
# We import standard datetime to get local 'System Time' instead of UTC
from datetime import datetime, timedelta, date
from .models import AppointmentSlot, DoctorPost
from django.contrib.auth.models import User

# --- HELPER FUNCTIONS ---

def cleanup_stale_slots():
    """
    Rule 1: Delete older slots if no one booked.
    Uses local system time to ensure accurate cleanup relative to the user's clock.
    """
    # Get current local system time (Naive)
    now = datetime.now()
    current_date = now.date()
    current_time = now.time()

    # 1. Delete slots from previous dates
    AppointmentSlot.objects.filter(is_booked=False, date__lt=current_date).delete()

    # 2. Delete slots from today that have already passed
    AppointmentSlot.objects.filter(
        is_booked=False, 
        date=current_date, 
        start_time__lt=current_time
    ).delete()

def is_slot_too_soon(slot_date, slot_start_time):
    """
    Rule 2 Helper: Checks if a slot is within the restricted 'Current Time + 1 Hour' window.
    Uses Naive comparisons (Local System Time) to avoid UTC timezone offsets issues.
    """
    # 1. Get current local time (Naive - matching your computer clock)
    now_naive = datetime.now()
    
    # 2. Create the slot datetime (Naive)
    slot_naive = datetime.combine(slot_date, slot_start_time)
    
    # 3. Calculate minimum allowed time (Now + 1 Hour)
    minimum_allowed_time = now_naive + timedelta(hours=1)

    # Return True if the slot is BEFORE the allowed time (Too Soon)
    return slot_naive < minimum_allowed_time


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
    # Rule 1: Cleanup old slots on load
    cleanup_stale_slots()

    if request.method == 'POST':
        date_str = request.POST.get('date')
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')

        try:
            # Convert inputs to Python objects
            slot_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            slot_start = datetime.strptime(start_time_str, "%H:%M").time()
            
            # Rule 2: Validation - Block slots less than 1 hour away
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
        slot.patient = None
        slot.is_booked = False
        slot.cancel_request_by = None
        slot.save()
        messages.success(request, "Cancellation approved. Appointment cancelled.")

    return redirect(redirect_url)


# --- PATIENT VIEWS ---
@login_required
def patient_dashboard(request):
    # Rule 1: Cleanup old slots before showing
    cleanup_stale_slots()

    # We use local date for filtering
    today = datetime.now().date()
    
    # Get all potential future slots
    raw_slots = AppointmentSlot.objects.filter(
        is_booked=False, 
        date__gte=today
    ).order_by('date', 'start_time')

    # Rule 2: Filter Logic
    # We manually filter the list to hide slots that are < 1 hour away
    available_slots = []
    for slot in raw_slots:
        if not is_slot_too_soon(slot.date, slot.start_time):
            available_slots.append(slot)

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

            # Rule 2: Security Check (Backend Enforcement)
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
            slot.save()
            messages.success(request, f"Confirmed with Dr. {slot.doctor.first_name}!")
                
        except AppointmentSlot.DoesNotExist:
            messages.error(request, "Slot does not exist.")
            
    return redirect('patient_dashboard')

@login_required
def find_doctor(request):
    doctors = User.objects.filter(profile__role='doctor')
    return render(request, 'appointments/find_doctor.html', {'doctors': doctors})