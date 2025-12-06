from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Profile

def sign_up(request):
    if request.method == 'POST':
        # Get data
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        full_name = request.POST.get('fullname')
        role = request.POST.get('role')
        mobile = request.POST.get('mobile')

        # --- VALIDATION ---
        if len(mobile) != 10:
            messages.error(request, "Mobile number must be exactly 10 digits.")
            return redirect('home')
            
        if not mobile.isdigit():
            messages.error(request, "Mobile number must contain numbers only.")
            return redirect('home')

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('home')
        
        # We check 'username' because that's where we will store the mobile number
        if User.objects.filter(username=mobile).exists():
            messages.error(request, "This mobile number is already registered! Please Login.")
            return redirect('home')

        # Check email uniqueness
        if User.objects.filter(email=email).exists():
            messages.error(request, "This email is already taken.")
            return redirect('home')

        # --- CREATION ---
        try:
            # We treat the mobile number as the system's "username"
            user = User.objects.create_user(username=mobile, email=email, password=password)
            user.first_name = full_name
            user.save()

            # Update Profile
            if hasattr(user, 'profile'):
                user.profile.role = role
                user.profile.mobile = mobile
                user.profile.save()

            messages.success(request, "Account created! Please login with your Mobile Number.")
            
            return redirect('home')
            
        except Exception as e:
            messages.error(request, f"Error creating account: {e}")
            return redirect('home')

    return redirect('home')

def sign_in(request):
    if request.method == 'POST':
        mobile = request.POST.get('mobile') 
        password = request.POST.get('password')
        user = authenticate(request, username=mobile, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name}!")
            return redirect('home')
        else:
            messages.error(request, "Invalid Mobile Number or Password.")
            return redirect('home')

    return redirect('home')

def sign_out(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('home')