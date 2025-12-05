from django.urls import path
from . import views

urlpatterns = [
    # Doctor URLs
    path('dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('schedule/', views.my_schedule, name='my_schedule'),
    path('delete-slot/<int:slot_id>/', views.delete_slot, name='delete_slot'),
    
    # Patient URLs
    path('find-doctors/', views.find_doctor, name='find_doctor'),
    path('my-appointments/', views.patient_dashboard, name='patient_dashboard'),
    path('book-slot/<int:slot_id>/', views.book_slot, name='book_slot'),

    # Shared URL
    path('cancel-appointment/<int:slot_id>/', views.cancel_appointment, name='cancel_appointment'),
]