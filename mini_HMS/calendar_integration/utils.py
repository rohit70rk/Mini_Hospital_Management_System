import json
import logging
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from django.conf import settings
from .models import GoogleCalendarToken

logger = logging.getLogger(__name__)
SCOPES = ['https://www.googleapis.com/auth/calendar.events']

def get_credentials(user):

    """Retrieve and auto-refresh credentials for a user."""

    # Check if the user has a token
    if not hasattr(user, 'calendar_token'):
        return None

    token_entry = user.calendar_token
    creds_data = json.loads(token_entry.token_data)
    creds = Credentials.from_authorized_user_info(creds_data, SCOPES)

    # Refresh if expired
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            # Save the fresh token back to DB
            token_entry.token_data = creds.to_json()
            token_entry.save()
        except Exception as e:
            logger.error(f"Failed to refresh token for {user.username}: {e}")
            return None

    return creds

def create_event(user, summary, description, start_dt, end_dt):
    """Creates a Google Calendar event and returns the Event ID."""
    creds = get_credentials(user)
    if not creds:
        return None

    try:
        service = build('calendar', 'v3', credentials=creds)
        event = {
            'summary': summary,
            'description': description,
            'start': {'dateTime': start_dt.isoformat(), 'timeZone': settings.TIME_ZONE},
            'end': {'dateTime': end_dt.isoformat(), 'timeZone': settings.TIME_ZONE},
        }
        result = service.events().insert(calendarId='primary', body=event).execute()
        return result.get('id')
    except Exception as e:
        logger.error(f"Error creating event: {e}")
        return None

def delete_event(user, event_id):
    """Deletes an event by ID."""
    if not event_id: return
    
    creds = get_credentials(user)
    if not creds: return

    try:
        service = build('calendar', 'v3', credentials=creds)
        service.events().delete(calendarId='primary', eventId=event_id).execute()
    except Exception as e:
        logger.error(f"Error deleting event: {e}")