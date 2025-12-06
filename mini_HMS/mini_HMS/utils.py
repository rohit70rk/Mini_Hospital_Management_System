import requests
import json
import logging

logger = logging.getLogger(__name__)

# URL of your Serverless Offline function
EMAIL_SERVICE_URL = "http://localhost:3000/dev/send-email"

def trigger_email(action, recipient_email, data):
    """
    Sends a payload to the Serverless Email Microservice.
    """
    payload = {
        "action": action,
        "recipient_email": recipient_email,
        "data": data
    }
    
    try:
        # Use a short timeout to prevent hanging the Django view if Email service is down
        response = requests.post(EMAIL_SERVICE_URL, json=payload, timeout=5)
        if response.status_code == 200:
            logger.info(f"Email triggered successfully: {action}")
        else:
            logger.error(f"Email service failed: {response.text}")
    except requests.exceptions.RequestException as e:
        # We log the error but don't stop the user's flow (Fail Silently)
        logger.error(f"Could not connect to Email Service: {e}")