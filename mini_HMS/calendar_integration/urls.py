from django.urls import path
from . import views

urlpatterns = [
    path('connect/', views.oauth_init, name='connect_calendar'),
    path('callback/', views.oauth_callback, name='calendar_callback'),
]