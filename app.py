import os
import re
import sqlite3
from urllib.parse import quote
from datetime import date, datetime

from flask import (Flask, abort, flash, g, jsonify, redirect,
                   render_template, request, url_for)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "raktsetu-dev-secret")
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "raktsetu.db")

# If DATABASE_URL is set (e.g. a free Neon / Supabase PostgreSQL), data is stored there permanently.
# If not set, the app uses the local SQLite file (good for running on your own computer).
DATABASE_URL = os.environ.get("DATABASE_URL", "").replace("postgres://", "postgresql://", 1)
PG = bool(DATABASE_URL)
if PG:
    import psycopg2
    import psycopg2.extras
BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
URGENCY = ["Normal", "Urgent", "Emergency"]
GAP_DAYS = 90  # minimum gap between two donations

PK = "SERIAL PRIMARY KEY" if PG else "INTEGER PRIMARY KEY AUTOINCREMENT"
SCHEMA = [
    f"""CREATE TABLE IF NOT EXISTS donors(
      id {PK}, name TEXT NOT NULL, age INTEGER NOT NULL,
      gender TEXT NOT NULL, bg TEXT NOT NULL, phone TEXT NOT NULL UNIQUE, city TEXT NOT NULL,
      email TEXT NOT NULL, last_donation TEXT, available INTEGER NOT NULL DEFAULT 1)""",
    f"""CREATE TABLE IF NOT EXISTS requests(
      id {PK}, patient TEXT NOT NULL, bg TEXT NOT NULL,
      hospital TEXT NOT NULL, city TEXT NOT NULL, units INTEGER NOT NULL, phone TEXT NOT NULL,
      urgency TEXT NOT NULL, created TEXT NOT NULL, fulfilled INTEGER NOT NULL DEFAULT 0)""",
    f"""CREATE TABLE IF NOT EXISTS connections(
      id {PK}, kind TEXT NOT NULL, ref_id INTEGER, created TEXT NOT NULL)""",
]


class Conn:
    """Small wrapper so the same code works with SQLite and PostgreSQL."""

    def __init__(self):
        if PG:
            self.c = psycopg2.connect(DATABASE_URL)
        else:
            self.c = sqlite3.connect(DB)
            self.c.row_factory = sqlite3.Row

    def execute(self, sql, args=()):
        if PG:
            cur = self.c.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(sql.replace("?", "%s"), args)
            return cur
        return self.c.execute(sql, args)

    def executemany(self, sql, rows):
        for r in rows:
            self.execute(sql, r)

    def commit(self):
        self.c.commit()

    def close(self):
        self.c.close()


def scalar(cur):
    row = cur.fetchone()
    return next(iter(row.values())) if PG else row[0]


def get_db():
    if "db" not in g:
        g.db = Conn()
    return g.db


@app.teardown_appcontext
def close_db(_):
    conn = g.pop("db", None)
    if conn:
        conn.close()


def days_ago(n):
    return date.fromordinal(date.today().toordinal() - n).isoformat()


def init_db():
    con = Conn()
    for stmt in SCHEMA:
        con.execute(stmt)
    con.commit()
    if scalar(con.execute("SELECT COUNT(*) FROM donors")) == 0:
        donors = [
            ("Rahul Patil", 24, "Male", "O+", "9876500011", "Mumbai", "rahul@mail.com", 200, 1),
            ("Sneha Kulkarni", 27, "Female", "A+", "9876500012", "Pune", "sneha@mail.com", 40, 1),
            ("Amit Shah", 31, "Male", "B+", "9876500013", "Mumbai", "amit@mail.com", 150, 1),
            ("Priya Nair", 22, "Female", "O-", "9876500014", "Thane", "priya@mail.com", 300, 1),
            ("Imran Sheikh", 35, "Male", "AB+", "9876500015", "Pune", "imran@mail.com", 120, 1),
            ("Neha Joshi", 29, "Female", "B-", "9876500016", "Nashik", "neha@mail.com", 95, 1),
            ("Vikas More", 26, "Male", "A-", "9876500017", "Mumbai", "vikas@mail.com", 10, 1),
            ("Pooja Deshmukh", 23, "Female", "O+", "9876500018", "Solapur", "pooja@mail.com", 180, 0),
            ("Sanjay Gupta", 40, "Male", "A+", "9876500019", "Thane", "sanjay@mail.com", 220, 1),
            ("Anita Rao", 33, "Female", "AB-", "9876500020", "Pune", "anita@mail.com", 260, 1),
        ]
        con.executemany(
            "INSERT INTO donors(name,age,gender,bg,phone,city,email,last_donation,available) VALUES(?,?,?,?,?,?,?,?,?)",
            [(n, a, g_, b, p, c, e, days_ago(d), av) for n, a, g_, b, p, c, e, d, av in donors])
        reqs = [
            ("Ramesh Pawar", "O+", "KEM Hospital", "Mumbai", 2, "9123400001", "Emergency", 0),
            ("Sunita Bhosale", "B+", "Sassoon Hospital", "Pune", 1, "9123400002", "Urgent", 1),
            ("Karan Mehta", "A-", "Jupiter Hospital", "Thane", 3, "9123400003", "Normal", 2),
        ]
        con.executemany(
            "INSERT INTO requests(patient,bg,hospital,city,units,phone,urgency,created) VALUES(?,?,?,?,?,?,?,?)",
            [(*r[:7], days_ago(r[7])) for r in reqs])
        con.execute("INSERT INTO connections(kind,ref_id,created) VALUES('seed',0,?)", (days_ago(3),))
    con.commit()
    con.close()


def donor_view(row):
    """Row -> dict with computed availability (needs 'yes' + 90 day gap) and masked phone."""
    d = dict(row)
    since = 999
    if d["last_donation"]:
        since = (date.today() - datetime.strptime(d["last_donation"], "%Y-%m-%d").date()).days
    d["is_available"] = bool(d["available"]) and since >= GAP_DAYS
    d["masked_phone"] = d["phone"][:2] + "XXXXX" + d["phone"][-3:]
    return d


def all_cities():
    rows = get_db().execute("SELECT DISTINCT city FROM donors ORDER BY city").fetchall()
    base = ["Mumbai", "Pune", "Thane", "Nashik", "Solapur", "Nagpur"]
    return sorted(set(base) | {r["city"] for r in rows})


def get_stats():
    db = get_db()
    donors = [donor_view(r) for r in db.execute("SELECT * FROM donors")]
    return {
        "donors": len(donors),
        "requests": scalar(db.execute("SELECT COUNT(*) FROM requests")),
        "connections": scalar(db.execute("SELECT COUNT(*) FROM connections")),
        "groups_available": len({d["bg"] for d in donors if d["is_available"]}),
        "per_group": {b: sum(1 for d in donors if d["bg"] == b) for b in BLOOD_GROUPS},
    }


@app.context_processor
def inject():
    return {"BLOOD_GROUPS": BLOOD_GROUPS, "URGENCY": URGENCY, "cities": all_cities()}


@app.route("/")
def home():
    return render_template("home.html", stats=get_stats())


@app.route("/find")
def find():
    bg = request.args.get("bg", "")
    city = request.args.get("city", "").strip()
    sql, args = "SELECT * FROM donors WHERE 1=1", []
    if bg in BLOOD_GROUPS:
        sql += " AND bg=?"
        args.append(bg)
    if city:
        sql += " AND LOWER(city) LIKE ?"
        args.append(f"%{city.lower()}%")
    donors = [donor_view(r) for r in get_db().execute(sql, args)]
    donors.sort(key=lambda d: not d["is_available"])
    return render_template("find.html", donors=donors, bg=bg, city=city)


def validate_donor(f):
    errors = []
    if len(f.get("name", "").strip()) < 3:
        errors.append("Enter your full name.")
    if not f.get("age", "").isdigit() or not 18 <= int(f["age"]) <= 65:
        errors.append("Age must be between 18 and 65.")
    if f.get("gender") not in ("Male", "Female", "Other"):
        errors.append("Select a gender.")
    if f.get("bg") not in BLOOD_GROUPS:
        errors.append("Select a blood group.")
    if not re.fullmatch(r"[0-9]{10}", f.get("phone", "")):
        errors.append("Phone number must be 10 digits.")
    if not f.get("city", "").strip():
        errors.append("Enter your city.")
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", f.get("email", "")):
        errors.append("Enter a valid email.")
    last = f.get("last_donation", "")
    if last:
        try:
            if datetime.strptime(last, "%Y-%m-%d").date() > date.today():
                errors.append("Last donation date cannot be in the future.")
        except ValueError:
            errors.append("Last donation date is not valid.")
    return errors


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        f = request.form
        errors = validate_donor(f)
        db = get_db()
        if not errors and db.execute("SELECT 1 FROM donors WHERE phone=?", (f["phone"],)).fetchone():
            errors.append("This phone number is already registered.")
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("register.html", f=f)
        db.execute(
            "INSERT INTO donors(name,age,gender,bg,phone,city,email,last_donation,available) VALUES(?,?,?,?,?,?,?,?,?)",
            (f["name"].strip(), int(f["age"]), f["gender"], f["bg"], f["phone"], f["city"].strip().title(),
             f["email"].strip(), f.get("last_donation") or None, 1 if f.get("available") == "1" else 0))
        db.commit()
        flash("Registered successfully. Thank you for being a donor!", "success")
        return redirect(url_for("find", bg=f["bg"]))
    return render_template("register.html", f={})


@app.route("/request", methods=["GET", "POST"])
def request_blood():
    if request.method == "POST":
        f = request.form
        errors = []
        if len(f.get("patient", "").strip()) < 3:
            errors.append("Enter the patient name.")
        if f.get("bg") not in BLOOD_GROUPS:
            errors.append("Select the required blood group.")
        if not f.get("hospital", "").strip() or not f.get("city", "").strip():
            errors.append("Hospital and city are required.")
        if not f.get("units", "").isdigit() or not 1 <= int(f["units"]) <= 20:
            errors.append("Units must be between 1 and 20.")
        if not re.fullmatch(r"[0-9]{10}", f.get("phone", "")):
            errors.append("Contact number must be 10 digits.")
        if f.get("urgency") not in URGENCY:
            errors.append("Select the urgency.")
        if errors:
            for e in errors:
                flash(e, "danger")
            return render_template("request.html", f=f)
        db = get_db()
        db.execute(
            "INSERT INTO requests(patient,bg,hospital,city,units,phone,urgency,created) VALUES(?,?,?,?,?,?,?,?)",
            (f["patient"].strip(), f["bg"], f["hospital"].strip(), f["city"].strip().title(),
             int(f["units"]), f["phone"], f["urgency"], date.today().isoformat()))
        db.commit()
        flash("Blood request submitted.", "success")
        return redirect(url_for("requests_page"))
    return render_template("request.html", f={})


@app.route("/requests")
def requests_page():
    rows = get_db().execute(
        "SELECT * FROM requests WHERE fulfilled=0 ORDER BY CASE urgency "
        "WHEN 'Emergency' THEN 0 WHEN 'Urgent' THEN 1 ELSE 2 END, id DESC").fetchall()
    return render_template("requests.html", reqs=rows)


@app.route("/fulfill/<int:rid>", methods=["POST"])
def fulfill(rid):
    db = get_db()
    db.execute("UPDATE requests SET fulfilled=1 WHERE id=?", (rid,))
    db.execute("INSERT INTO connections(kind,ref_id,created) VALUES('request',?,?)", (rid, date.today().isoformat()))
    db.commit()
    flash("Request marked as fulfilled. Thank you!", "success")
    return redirect(url_for("requests_page"))


@app.route("/stats")
def stats_page():
    return render_template("stats.html", stats=get_stats())


@app.route("/donor/<int:did>")
def donor_profile(did):
    row = get_db().execute("SELECT * FROM donors WHERE id=?", (did,)).fetchone()
    if not row:
        abort(404)
    return render_template("donor.html", d=donor_view(row))


@app.route("/contact/<int:did>", methods=["POST"])
def contact(did):
    """Reveals the phone number only after the person confirms they need blood."""
    db = get_db()
    row = db.execute("SELECT name,bg,phone FROM donors WHERE id=?", (did,)).fetchone()
    if not row:
        return jsonify(error="Donor not found"), 404
    db.execute("INSERT INTO connections(kind,ref_id,created) VALUES('donor',?,?)", (did, date.today().isoformat()))
    db.commit()
    msg = f"Hello {row['name']}, I found you on RaktSetu. I need {row['bg']} blood. Can you help?"
    return jsonify(phone=row["phone"], whatsapp=f"https://wa.me/91{row['phone']}?text=" + quote(msg))


@app.route("/about")
def about():
    return render_template("about.html")


@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"), 404


init_db()

if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
