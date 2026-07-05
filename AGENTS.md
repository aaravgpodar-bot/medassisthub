# MedAssist Hub Notes

## Commands

- Install: `pip install -r requirements.txt`
- Reset demo database: `python seed_data.py`
- Run locally: `python app.py`
- Quick syntax check: `python -m compileall app.py seed_data.py pythonanywhere_wsgi.py`

## Structure

- `app.py` contains Flask routes, authentication, role checks, and dashboard queries.
- `schema.sql` defines SQLite tables for users, patients, appointments, tasks, messages, and feedback.
- `seed_data.py` resets the database with fictional sample users and patients.
- `templates/` contains Jinja HTML pages.
- `static/` contains CSS and JavaScript.
- `pythonanywhere_wsgi.py` is a helper for a new PythonAnywhere web app.

## Safety

Use fictional data only. This is not a certified medical-record system and should not be used for real clinical care.
