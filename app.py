from functools import wraps
from pathlib import Path
import sqlite3

from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash


BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "medassist.db"

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-secret-key-on-pythonanywhere"


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query(sql, params=(), one=False):
    cur = get_db().execute(sql, params)
    rows = cur.fetchall()
    cur.close()
    return (rows[0] if rows else None) if one else rows


def execute(sql, params=()):
    db = get_db()
    cur = db.execute(sql, params)
    db.commit()
    return cur.lastrowid


def current_user():
    if "user_id" not in session:
        return None
    return query("SELECT * FROM users WHERE id = ?", (session["user_id"],), one=True)


@app.context_processor
def inject_user():
    return {"current_user": current_user()}


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = current_user()
        if not user:
            return redirect(url_for("login"))
        if not user["is_active"]:
            session.clear()
            flash("Your account is inactive. Please contact an admin.", "error")
            return redirect(url_for("login"))
        return view(*args, **kwargs)

    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user = current_user()
        if not user or user["role"] != "admin":
            flash("Admin access is required.", "error")
            return redirect(url_for("dashboard"))
        return view(*args, **kwargs)

    return wrapped


@app.route("/")
def home():
    if current_user():
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        form = request.form
        required = ["name", "email", "password", "profession"]
        if not all(form.get(field, "").strip() for field in required):
            flash("Please fill in name, email, password, and profession.", "error")
            return render_template("register.html")
        try:
            execute(
                """
                INSERT INTO users
                (name, email, password_hash, profession, specialization, workplace, registration_number, role)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    form["name"].strip(),
                    form["email"].strip().lower(),
                    generate_password_hash(form["password"]),
                    form["profession"].strip(),
                    form.get("specialization", "").strip(),
                    form.get("workplace", "").strip(),
                    form.get("registration_number", "").strip(),
                    "staff",
                ),
            )
            flash("Account created. Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("That email is already registered.", "error")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        user = query("SELECT * FROM users WHERE email = ?", (email,), one=True)
        if user and user["is_active"] and check_password_hash(user["password_hash"], password):
            session.clear()
            session["user_id"] = user["id"]
            return redirect(url_for("dashboard"))
        flash("Invalid login or inactive account.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out safely.", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    user = current_user()
    stats = {
        "patients": query("SELECT COUNT(*) AS total FROM patients", one=True)["total"],
        "appointments": query("SELECT COUNT(*) AS total FROM appointments WHERE status != 'cancelled'", one=True)["total"],
        "tasks": query("SELECT COUNT(*) AS total FROM tasks WHERE assigned_to = ? AND is_completed = 0", (user["id"],), one=True)["total"],
        "messages": query("SELECT COUNT(*) AS total FROM messages WHERE receiver_id = ? AND status = 'unread'", (user["id"],), one=True)["total"],
    }
    appointments = query(
        """
        SELECT a.*, p.full_name AS patient_name
        FROM appointments a JOIN patients p ON p.id = a.patient_id
        ORDER BY a.appointment_date, a.appointment_time LIMIT 6
        """
    )
    tasks = query("SELECT * FROM tasks WHERE assigned_to = ? ORDER BY due_date LIMIT 6", (user["id"],))
    return render_template("dashboard.html", stats=stats, appointments=appointments, tasks=tasks)


@app.route("/patients", methods=["GET", "POST"])
@login_required
def patients():
    user = current_user()
    if request.method == "POST":
        form = request.form
        execute(
            """
            INSERT INTO patients
            (full_name, age, phone, medical_history, allergies, notes, created_by, updated_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                form.get("full_name", "").strip(),
                form.get("age") or None,
                form.get("phone", "").strip(),
                form.get("medical_history", "").strip(),
                form.get("allergies", "").strip(),
                form.get("notes", "").strip(),
                user["id"],
                user["id"],
            ),
        )
        flash("Patient added.", "success")
        return redirect(url_for("patients"))
    search = request.args.get("q", "").strip()
    if search:
        rows = query(
            """
            SELECT p.*, u.name AS creator_name
            FROM patients p LEFT JOIN users u ON u.id = p.created_by
            WHERE p.full_name LIKE ? OR p.phone LIKE ?
            ORDER BY p.updated_at DESC
            """,
            (f"%{search}%", f"%{search}%"),
        )
    else:
        rows = query(
            """
            SELECT p.*, u.name AS creator_name
            FROM patients p LEFT JOIN users u ON u.id = p.created_by
            ORDER BY p.updated_at DESC
            """
        )
    return render_template("patients.html", patients=rows, search=search)


@app.route("/appointments", methods=["GET", "POST"])
@login_required
def appointments():
    user = current_user()
    if request.method == "POST":
        form = request.form
        execute(
            """
            INSERT INTO appointments
            (patient_id, professional_id, appointment_date, appointment_time, reason, status, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                form["patient_id"],
                form["professional_id"],
                form["appointment_date"],
                form["appointment_time"],
                form.get("reason", "").strip(),
                form.get("status", "scheduled"),
                user["id"],
            ),
        )
        flash("Appointment saved.", "success")
        return redirect(url_for("appointments"))
    rows = query(
        """
        SELECT a.*, p.full_name AS patient_name, u.name AS professional_name
        FROM appointments a
        JOIN patients p ON p.id = a.patient_id
        JOIN users u ON u.id = a.professional_id
        ORDER BY a.appointment_date, a.appointment_time
        """
    )
    patients_list = query("SELECT id, full_name FROM patients ORDER BY full_name")
    staff = query("SELECT id, name, profession FROM users WHERE is_active = 1 ORDER BY name")
    return render_template("appointments.html", appointments=rows, patients=patients_list, staff=staff)


@app.route("/appointment/<int:item_id>/<status>")
@login_required
def appointment_status(item_id, status):
    if status not in {"scheduled", "completed", "cancelled", "waiting"}:
        flash("Invalid appointment status.", "error")
    else:
        execute("UPDATE appointments SET status = ? WHERE id = ?", (status, item_id))
        flash("Appointment updated.", "success")
    return redirect(url_for("appointments"))


@app.route("/tasks", methods=["GET", "POST"])
@login_required
def tasks():
    user = current_user()
    if request.method == "POST":
        form = request.form
        execute(
            "INSERT INTO tasks (title, category, due_date, assigned_to, created_by) VALUES (?, ?, ?, ?, ?)",
            (form["title"].strip(), form.get("category", "follow-up"), form.get("due_date"), form["assigned_to"], user["id"]),
        )
        flash("Task created.", "success")
        return redirect(url_for("tasks"))
    rows = query(
        """
        SELECT t.*, u.name AS assigned_name
        FROM tasks t JOIN users u ON u.id = t.assigned_to
        ORDER BY t.is_completed, t.due_date
        """
    )
    staff = query("SELECT id, name, profession FROM users WHERE is_active = 1 ORDER BY name")
    return render_template("tasks.html", tasks=rows, staff=staff)


@app.route("/task/<int:item_id>/complete")
@login_required
def complete_task(item_id):
    execute("UPDATE tasks SET is_completed = 1 WHERE id = ?", (item_id,))
    flash("Task completed.", "success")
    return redirect(url_for("tasks"))


@app.route("/messages", methods=["GET", "POST"])
@login_required
def messages():
    user = current_user()
    if request.method == "POST":
        form = request.form
        execute(
            "INSERT INTO messages (sender_id, receiver_id, body, status) VALUES (?, ?, ?, 'unread')",
            (user["id"], form["receiver_id"], form["body"].strip()),
        )
        flash("Message sent.", "success")
        return redirect(url_for("messages"))
    execute("UPDATE messages SET status = 'read' WHERE receiver_id = ?", (user["id"],))
    rows = query(
        """
        SELECT m.*, s.name AS sender_name, r.name AS receiver_name
        FROM messages m
        JOIN users s ON s.id = m.sender_id
        JOIN users r ON r.id = m.receiver_id
        WHERE m.sender_id = ? OR m.receiver_id = ?
        ORDER BY m.created_at DESC
        """,
        (user["id"], user["id"]),
    )
    staff = query("SELECT id, name, profession FROM users WHERE is_active = 1 AND id != ? ORDER BY name", (user["id"],))
    return render_template("messages.html", messages=rows, staff=staff)


@app.route("/feedback", methods=["GET", "POST"])
@login_required
def feedback():
    user = current_user()
    if request.method == "POST":
        form = request.form
        execute(
            "INSERT INTO feedback (user_id, profession, category, description, feature_suggestion) VALUES (?, ?, ?, ?, ?)",
            (user["id"], user["profession"], form["category"], form["description"].strip(), form.get("feature_suggestion", "").strip()),
        )
        flash("Feedback submitted.", "success")
        return redirect(url_for("feedback"))
    rows = query(
        "SELECT f.*, u.name FROM feedback f JOIN users u ON u.id = f.user_id ORDER BY f.created_at DESC"
    )
    return render_template("feedback.html", feedback=rows)


@app.route("/admin")
@login_required
@admin_required
def admin():
    stats = {
        "users": query("SELECT COUNT(*) AS total FROM users", one=True)["total"],
        "doctors": query("SELECT COUNT(*) AS total FROM users WHERE profession LIKE '%doctor%'", one=True)["total"],
        "nurses": query("SELECT COUNT(*) AS total FROM users WHERE profession LIKE '%nurse%'", one=True)["total"],
        "appointments": query("SELECT COUNT(*) AS total FROM appointments", one=True)["total"],
        "problems": query("SELECT COUNT(*) AS total FROM feedback", one=True)["total"],
        "completed_tasks": query("SELECT COUNT(*) AS total FROM tasks WHERE is_completed = 1", one=True)["total"],
    }
    users = query("SELECT * FROM users ORDER BY profession, name")
    grouped_feedback = query("SELECT profession, COUNT(*) AS total FROM feedback GROUP BY profession ORDER BY total DESC")
    return render_template("admin.html", users=users, stats=stats, grouped_feedback=grouped_feedback)


@app.route("/admin/user/<int:user_id>/toggle")
@login_required
@admin_required
def toggle_user(user_id):
    if user_id == current_user()["id"]:
        flash("You cannot deactivate your own admin account.", "error")
    else:
        execute("UPDATE users SET is_active = CASE WHEN is_active = 1 THEN 0 ELSE 1 END WHERE id = ?", (user_id,))
        flash("User status changed.", "success")
    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(debug=True)
