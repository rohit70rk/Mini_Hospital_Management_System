from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from google_auth_oauthlib.flow import Flow
from .models import GoogleCalendarToken

CLIENT_SECRETS_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def oauth_init(request):
    """Step 1: Send user to Google"""
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=request.build_absolute_uri(reverse('google_callback_legacy'))
    )
    auth_url, state = flow.authorization_url(access_type='offline', include_granted_scopes='true', prompt='consent')
    request.session['google_auth_state'] = state
    return redirect(auth_url)

def oauth_callback(request):
    """Step 2: Receive token from Google"""
    state = request.session.get('google_auth_state')
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        state=state,
        redirect_uri=request.build_absolute_uri(reverse('google_callback_legacy'))
    )
    
    flow.fetch_token(authorization_response=request.build_absolute_uri())
    credentials = flow.credentials

    # Save to our new model
    GoogleCalendarToken.objects.update_or_create(
        user=request.user,
        defaults={'token_data': credentials.to_json()}
    )

    messages.success(request, "Google Calendar Connected!")
    
    # Redirect back to the correct dashboard
    if hasattr(request.user, 'profile') and request.user.profile.role == 'doctor':
        return redirect('my_schedule')
    return redirect('patient_dashboard')