from django.db import models
from django.contrib.auth.models import User

class AppointmentSlot(models.Model):
    doctor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_slots')
    patient = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='patient_bookings')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_booked = models.BooleanField(default=False)
    doctor_google_event_id = models.CharField(max_length=255, blank=True, null=True)
    patient_google_event_id = models.CharField(max_length=255, blank=True, null=True)
    
    # --- FIELD FOR MUTUAL CANCELLATION ---
    cancel_request_by = models.CharField(
        max_length=10, 
        blank=True, 
        null=True, 
        choices=[('doctor', 'Doctor'), ('patient', 'Patient')]
    )

    class Meta:
        unique_together = ('doctor', 'date', 'start_time')
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.doctor.username} - {self.date}"

    # --- OPTIMIZATION: Centralized Time Formatting ---
    def get_time_range(self):
        """Returns formatted string: '10:00 - 10:30'"""
        return f"{self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"

# --- MODEL FOR COLLABORATION ---
class DoctorPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='doctor_posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Post by {self.author.first_name} at {self.created_at}"