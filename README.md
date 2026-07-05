# ClinicFlow

ClinicFlow is a Flask and SQLite web app for healthcare workplace coordination. It brings staff accounts, patient workflows, appointments, reminders, messages, feedback, and admin tools into one clean workspace.

## Features

- User registration, secure login, logout, profiles, professions, and account status
- First registered user automatically becomes the admin
- Role-aware dashboard for appointments, tasks, messages, and quick actions
- Patient records with history, allergies, notes, and creator attribution
- Appointment list with scheduled, waiting, completed, and cancelled states
- Tasks and reminders for follow-ups, reports, and medication reviews
- Internal staff messaging
- Issue reporting and feature feedback grouped by profession
- Admin panel for users, account activation, statistics, and feedback summaries

## Local Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python seed_data.py
python app.py
```

`python seed_data.py` creates a clean empty database. Open the website and sign up; the first account created becomes the admin.

## PythonAnywhere Setup

Use a dedicated folder so this app does not replace another project.

```bash
cd ~
git clone https://github.com/aaravgpodar-bot/medassisthub.git medassist-hub
cd ~/medassist-hub
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python seed_data.py
```

Then in the PythonAnywhere **Web** tab:

1. Add a new web app for the account.
2. Choose manual configuration and a Python 3 version.
3. Set source code to `/home/YOUR_USERNAME/medassist-hub`.
4. Open the WSGI file.
5. Paste the contents of `pythonanywhere_wsgi.py`.
6. Replace `YOUR_USERNAME` with your PythonAnywhere username.
7. Reload the web app.

For username `medassisthub`, the likely URL is:

```text
https://medassisthub.pythonanywhere.com
```

## Project Structure

```text
app.py                    Flask routes and app logic
schema.sql                SQLite table definitions
seed_data.py              Clean database reset script
requirements.txt          Python dependencies
pythonanywhere_wsgi.py    PythonAnywhere WSGI helper
templates/                HTML pages
static/css/styles.css     Responsive styling
static/js/app.js          Small browser helpers
AGENTS.md                 Notes for future Codex work
```

## Safety Notes

Use fictional records only. ClinicFlow is not a certified medical-record system and should not be used for real clinical care.
