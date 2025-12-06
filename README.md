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

    ###Mac/Linux:
    python3 -m venv venv
    source venv/bin/activate

    ###Windows (PowerShell):    
    python -m venv venv
    venv\Scripts\activate

#### 3. Install dependencies:

    cd Mini_Hospital_Management_System

    pip install -r requirements.txt

#### 4. Google Calender Integration

    Rename:
    client_secret_9028xxxxxxxxxxxxxxxxxxxxxxxxxxxxx.apps.googleusercontent.com.json
    to
    client_secret.json
    and 
    add it to Project root Folder:

    myprojects/HMS
                ├── LICENSE
                ├── mini_HMS
                │   ├── mini_HMS
                │   ├── appointments
                │   ├── client_secret.json  <<==========
                │   ├── manage.py
                │   ├── static
                │   │   └── style.css
                │   ├── etc.

#### 5. Command to run Project

    cd Mini_Hospital_Management_System

    python manage.py makemigrations
    python manage.py migrate

    python manage.py runserver

### 2. Email Notification via Serverless Function

#### 1. Install Dependencies

    cd email-service

    npm install

#### 2. Configure Credentials

    ###Mac/Linux:
    touch .env

    ###Windows (PowerShell):
    New-Item .env -ItemType File

    ###Add the following content to .env: (Replace with your actual Gmail address and App Password)

    SENDER_EMAIL=your.email@gmail.com
    SENDER_PASSWORD=xvfr tgbn hyuj mkiol  # Your 16-char App Password

#### 3. Start the Service

    sls offline