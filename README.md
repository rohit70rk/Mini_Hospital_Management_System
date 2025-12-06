# Mini Hospital Management System (HMS)

A web-based hospital management application focused on doctor availability management and patient appointment booking. This system features real-time slot blocking to prevent double-booking, Google Calendar integration, and a separate serverless microservice for email notifications.

## 📋 Table of Contents
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Installation & Setup](#-installation--setup)

## ✨ Features

### 👨‍⚕️ Doctor Portal
* **Dashboard:** Manage appointments and personal availability.
* **Slot Management:** Create availability time slots (e.g., 10:00-10:30).
* **Privacy:** View and manage only their own bookings.

### 🏥 Patient Portal
* **Search:** View doctors and their specific available time slots.
* **Booking:** Book available slots. The system handles concurrency to ensure a slot cannot be double-booked.

### ⚙️ System Integrations
* **Authentication:** Secure Role-Based Access Control (RBAC) for Doctors and Patients with hashed passwords.
* **Google Calendar Sync:** Automatically creates calendar events for both the Doctor and Patient upon confirmed booking.
* **Notification Service:** A decoupled Python Serverless function (AWS Lambda) that handles:
    * `SIGNUP_WELCOME`: Sent upon user registration.
    * `BOOKING_CONFIRMATION`: Sent upon successful appointment booking.

## 🛠 Tech Stack
* **Backend:** Django Framework
* **Database:** SQLite
* **ORM:** Django ORM
* **Email Service:** Serverless Framework (Python, AWS Lambda) using `serverless-offline` for local dev.
* **External APIs:** Google Calendar API (OAuth2).

## 💾 Installation & Setup

### 1. Mini Hospital Management System

#### 1. Clone GitHub Repo

    git clone https://github.com/rohit70rk/Mini_Hospital_Management_System.git

#### 2. Create and activate a virtual environment:

    ### Mac/Linux:
    python3 -m venv venv
    source venv/bin/activate

    ### Windows (PowerShell):    
    python -m venv venv
    venv\Scripts\activate

#### 3. Install dependencies:

    cd mini_Hospital_Management_System/

    pip install -r requirements.txt

#### 4. Google Calender Integration

    Rename:
    Client_secret_9028xxxxxxxxxxxxxxxxxxxxxxxxxxxxx.apps.googleusercontent.com.json
    to
    client_secret.json
    and 
    Add it to Project root Folder (Pointed):

    # Project Structure:

    /myprojects/mini_Hospital_Management_System/
        ├── LICENSE
        ├── README.md
        ├── email-service
        │   ├── handler.py
        │   ├── package-lock.json
        │   ├── package.json
        │   └── serverless.yml
        ├── mini_HMS
        │   ├── appointments
        │   ├── calendar_integration
        │   ├── client_secret.json
        │   ├── manage.py
        │   ├── mini_HMS
        │   ├── client_secret.json  <<========
        │   ├── static
        │   ├── templates
        │   └── users
        └── requirements.txt


#### 5. Make Migrations

    cd Mini_Hospital_Management_System/mini_HMS/

    python manage.py makemigrations
    python manage.py migrate

### 2. Email Notification via Serverless Function

#### 1. Install Dependencies

    cd Mini_Hospital_Management_System/email-service/         

    npm install

#### 2. Configure Credentials

    cd Mini_Hospital_Management_System/email-service/         

    ###Mac/Linux:
    touch .env

    ###Windows (PowerShell):
    New-Item .env -ItemType File

    ###Add the following content to .env: (Replace with your actual Gmail address and App Password)

    SENDER_EMAIL=your.email@gmail.com
    SENDER_PASSWORD=xvfrtgbnhyujmkiol

### 3. Run the Project

    cd Mini_Hospital_Management_System/email-service/         
    sls offline

    New TERMINAL:-

    cd Mini_Hospital_Management_System/

    ### Mac/Linux:
    source venv/bin/activate
    
    ### Windows (PowerShell):    
    venv\Scripts\activate

    cd Mini_Hospital_Management_System/mini_HMS/
    python manage.py runserver
