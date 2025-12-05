from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.sign_up, name='signup'),
    path('login/', views.sign_in, name='login'),
    path('logout/', views.sign_out, name='logout'),
]