from django.db import models
from django.contrib.auth.models import User

# Define the roles
ROLE_CHOICES = (
    ('doctor', 'Doctor'),
    ('patient', 'Patient'),
)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')
    mobile = models.CharField(max_length=15, unique=True, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"

# This adds .is_doctor and .is_patient properties to the standard User model dynamically.
# This allows your templates to use {% if user.is_doctor %} without errors.

@property
def is_doctor(self):
    if hasattr(self, 'profile'):
        return self.profile.role == 'doctor'
    return False

@property
def is_patient(self):
    if hasattr(self, 'profile'):
        return self.profile.role == 'patient'
    return False

# Inject these properties into the User model
User.add_to_class("is_doctor", is_doctor)
User.add_to_class("is_patient", is_patient)