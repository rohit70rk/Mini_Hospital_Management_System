from django.db import models
from django.contrib.auth.models import User

class GoogleCalendarToken(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='calendar_token')
    token_data = models.TextField()  # Stores the JSON credentials
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Calendar Token for {self.user.username}"