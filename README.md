# Mini Hospital Management System (HMS)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Django](https://img.shields.io/badge/Django-Backend-green)
![Serverless](https://img.shields.io/badge/Serverless-Offline-red)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)

A web-based hospital management application focused on doctor availability management and patient appointment booking. This system features real-time slot blocking to prevent double-booking, Google Calendar integration, and a separate serverless microservice for email notifications.

## 📋 Table of Contents
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)

## ✨ Features

### 👨‍⚕️ Doctor Portal
* **Dashboard:** Manage appointments and personal availability.
* [cite_start]**Slot Management:** Create availability time slots (e.g., 10:00-10:30).
* [cite_start]**Privacy:** View and manage only their own bookings.

### 🏥 Patient Portal
* [cite_start]**Search:** View doctors and their specific available time slots.
* **Booking:** Book available slots. [cite_start]The system handles concurrency to ensure a slot cannot be double-booked.

### ⚙️ System Integrations
* [cite_start]**Authentication:** Secure Role-Based Access Control (RBAC) for Doctors and Patients with hashed passwords.
* [cite_start]**Google Calendar Sync:** Automatically creates calendar events for both the Doctor and Patient upon confirmed booking.
* **Notification Service:** A decoupled Python Serverless function (AWS Lambda) that handles:
    * [cite_start]`SIGNUP_WELCOME`: Sent upon user registration.
    * [cite_start]`BOOKING_CONFIRMATION`: Sent upon successful appointment booking.

## 🛠 Tech Stack
* [cite_start]**Backend:** Django Framework
* [cite_start]**Database:** PostgreSQL
* [cite_start]**ORM:** Django ORM
* [cite_start]**Email Service:** Serverless Framework (Python, AWS Lambda) using `serverless-offline` for local dev.
* [cite_start]**External APIs:** Google Calendar API (OAuth2).

## 🧱 Prerequisites
Before running the project, ensure you have the following installed:
* Python 3.x
* Node.js & NPM (for Serverless Framework)
* PostgreSQL
* Google Cloud Console credentials (`credentials.json`) for Calendar API.

## 💾 Installation & Setup

CREATE DATABASE hms_db;
CREATE USER hms_user WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE hms_db TO hms_user;

### 1. Create and activate a virtual environment:

    #### Mac/Linux

    python3 -m venv venv
    source .venv/bin/activate

    #### Windows
    python -m venv venv
    venv\Scripts\activate

### 2. Install dependencies:

    pip install -r requirements.txt
