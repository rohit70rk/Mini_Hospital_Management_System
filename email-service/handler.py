import json
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- TEMPLATE DISPATCHER ---
# This separates the 'Data' from the 'Logic'
TEMPLATES = {
    "SIGNUP_WELCOME": {
        "subject": "Welcome to Mini HMS!",
        "body": lambda d: (
            f"Hello {d.get('name')},\n\n"
            f"Welcome to Mini HMS! \nYour Account has been Successfully Created.\n\n"
            f"Best Regards,\nMini HMS Team"
        )
    },
    "BOOKING_CONFIRMATION": {
        "subject": "Appointment Confirmed",
        "body": lambda d: (
            f"Hello {d.get('patient_name')},\n\n"
            f"Your Appointment with Dr. {d.get('doctor_name')} is Confirmed.\n\n"
            f"Date: {d.get('date')}\n"
            f"Time: {d.get('time')}\n\n"
            f"Please arrive 10 minutes early.\n"
            f"Mini HMS Team"
        )
    },
    "BOOKING_CANCELLATION": {
        "subject": "Appointment Cancelled",
        "body": lambda d: (
            f"Hello {d.get('name')},\n\n"
            f"The following Appointment has been Cancelled:\n\n"
            f"Date: {d.get('date')}\n"
            f"Time: {d.get('time')}\n\n"
            f"If this was a Mistake, Please book a New slot.\n"
            f"Mini HMS Team"
        )
    },
    "DOCTOR_NEW_BOOKING": {
        "subject": "New Patient Appointment",
        "body": lambda d: (
            f"Hello Dr. {d.get('doctor_name')},\n\n"
            f"You have a new Appointment booking.\n\n"
            f"Patient: {d.get('patient_name')}\n"
            f"Date: {d.get('date')}\n"
            f"Time: {d.get('time')}\n"
        )
    },
    "DOCTOR_SLOT_CANCELLED": {
        "subject": "Appointment Cancelled",
        "body": lambda d: (
            f"Hello Dr. {d.get('doctor_name')},\n\n"
            f"The Appointment with {d.get('patient_name')} has been Cancelled.\n\n"
            f"Date: {d.get('date')}\n"
            f"Time: {d.get('time')}\n\n"
            f"The slot is now Open for other Patients."
        )
    }
}

def send_email(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        action = body.get('action')
        recipient_email = body.get('recipient_email')
        data = body.get('data', {})

        if not recipient_email or not action:
            return response(400, "Missing email or action")

        # --- OPTIMIZED LOGIC ---
        template = TEMPLATES.get(action)
        
        if not template:
            return response(400, f"Invalid Action: {action}")

        subject = template["subject"]
        # Call the lambda function to generate the body string
        message_body = template["body"](data)

        _send_via_smtp(recipient_email, subject, message_body)
        return response(200, f"Email sent successfully for {action}")

    except Exception as e:
        print(f"Error sending email: {e}")
        return response(500, str(e))

def _send_via_smtp(to_email, subject, body_text):
    smtp_server = os.environ.get('SMTP_SERVER')
    smtp_port = int(os.environ.get('SMTP_PORT', 587))
    sender_email = os.environ.get('SENDER_EMAIL')
    sender_password = os.environ.get('SENDER_PASSWORD')

    if not sender_email or "your-email" in sender_email:
        print(f"[MOCK EMAIL] To: {to_email} | Subject: {subject}")
        print(f"[MOCK BODY] {body_text}")
        return

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body_text, 'plain'))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"SMTP Error: {e}")
        raise e

def response(status, message):
    return {
        "statusCode": status,
        "body": json.dumps({"message": message})
    }