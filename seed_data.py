import sqlite3
from pathlib import Path

from werkzeug.security import generate_password_hash


BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "medassist.db"


def run():
    schema = (BASE_DIR / "schema.sql").read_text(encoding="utf-8")
    db = sqlite3.connect(DATABASE)
    db.executescript(schema)

    users = [
        ("Admin User", "admin@medassist.test", "Doctor", "Internal Medicine", "Demo Clinic", "ADM-100", "admin"),
        ("Dr. Maya Shah", "maya@medassist.test", "Doctor", "Pediatrics", "Demo Clinic", "DOC-201", "staff"),
        ("Nurse Liam Chen", "liam@medassist.test", "Nurse", "Triage", "Demo Clinic", "NUR-301", "staff"),
        ("Priya Nair", "priya@medassist.test", "Receptionist", "Front Desk", "Demo Clinic", "REC-401", "staff"),
        ("Omar Khan", "omar@medassist.test", "Pharmacist", "Medication Review", "Demo Pharmacy", "PHA-501", "staff"),
    ]
    for user in users:
        db.execute(
            """
            INSERT INTO users
            (name, email, password_hash, profession, specialization, workplace, registration_number, role)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user[0], user[1], generate_password_hash("Password123!"), user[2], user[3], user[4], user[5], user[6]),
        )

    patients = [
        ("Aarav Patel", 34, "555-0101", "Fictional history: seasonal asthma.", "Dust", "Prefers morning appointments.", 2, 2),
        ("Neha Rao", 47, "555-0102", "Fictional history: mild hypertension.", "None recorded", "Follow-up due next month.", 3, 3),
        ("Sam Wilson", 29, "555-0103", "Fictional history: sports injury.", "Penicillin", "Needs physiotherapy referral.", 2, 2),
    ]
    db.executemany(
        """
        INSERT INTO patients
        (full_name, age, phone, medical_history, allergies, notes, created_by, updated_by)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        patients,
    )

    db.executemany(
        """
        INSERT INTO appointments
        (patient_id, professional_id, appointment_date, appointment_time, reason, status, created_by)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (1, 2, "2026-07-06", "09:30", "Asthma review", "scheduled", 4),
            (2, 2, "2026-07-06", "10:15", "Blood pressure follow-up", "waiting", 4),
            (3, 3, "2026-07-07", "14:00", "Dressing check", "scheduled", 4),
        ],
    )

    db.executemany(
        "INSERT INTO tasks (title, category, due_date, assigned_to, created_by, is_completed) VALUES (?, ?, ?, ?, ?, ?)",
        [
            ("Call Neha for follow-up reminder", "follow-up", "2026-07-06", 4, 2, 0),
            ("Review fictional medication list", "medication review", "2026-07-07", 5, 2, 0),
            ("Prepare weekly appointment report", "reports", "2026-07-08", 1, 1, 1),
        ],
    )

    db.executemany(
        "INSERT INTO messages (sender_id, receiver_id, body, status) VALUES (?, ?, ?, ?)",
        [
            (4, 2, "Sam Wilson has arrived for the afternoon slot.", "unread"),
            (2, 5, "Please review the fictional medication notes for Neha Rao.", "read"),
        ],
    )

    db.executemany(
        "INSERT INTO feedback (user_id, profession, category, description, feature_suggestion) VALUES (?, ?, ?, ?, ?)",
        [
            (3, "Nurse", "workload", "Too many manual follow-up notes are being tracked separately.", "Add recurring reminders."),
            (4, "Receptionist", "scheduling", "It is hard to see waiting and cancelled appointments together.", "Add color-coded appointment filters."),
        ],
    )

    db.commit()
    db.close()
    print("Database created with fictional demo data.")


if __name__ == "__main__":
    run()
