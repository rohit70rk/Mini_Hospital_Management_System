from django.contrib import admin
from .models import AppointmentSlot

@admin.register(AppointmentSlot)
class AppointmentSlotAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'date', 'start_time', 'end_time', 'is_booked', 'patient')
    list_filter = ('is_booked', 'date')
    search_fields = ('doctor__username', 'patient__username')