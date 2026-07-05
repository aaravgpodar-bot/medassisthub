import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "medassist.db"


def run():
    schema = (BASE_DIR / "schema.sql").read_text(encoding="utf-8")
    db = sqlite3.connect(DATABASE)
    db.executescript(schema)
    db.commit()
    db.close()
    print("Clean database created with no users, patients, appointments, tasks, messages, or feedback.")
    print("Open the website and sign up. The first account created will become the admin.")


if __name__ == "__main__":
    run()
