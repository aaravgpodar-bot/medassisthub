import sqlite3
from pathlib import Path

from werkzeug.security import generate_password_hash


BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "medassist.db"


def run():
    schema = (BASE_DIR / "schema.sql").read_text(encoding="utf-8")
    db = sqlite3.connect(DATABASE)
    db.executescript(schema)

    db.execute(
        """
        INSERT INTO users
        (name, email, password_hash, profession, specialization, workplace, registration_number, role)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "Admin User",
            "admin@medassist.test",
            generate_password_hash("Password123!"),
            "Clinic Manager",
            "Operations",
            "ClinicFlow Workspace",
            "ADMIN-001",
            "admin",
        ),
    )

    db.commit()
    db.close()
    print("Clean database created with one admin account and no sample appointments, patients, tasks, messages, or feedback.")


if __name__ == "__main__":
    run()
