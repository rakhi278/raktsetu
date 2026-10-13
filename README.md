# 🩸 RaktSetu - Blood Donor Finder

RaktSetu (Setu means bridge) is a web application that connects people who need blood with people willing to donate it. Users can search donors by blood group and city, register as a donor, post blood requests with urgency, and contact donors while keeping phone numbers private.

This is a college mini project.

## Features

- **Home page** with hero slider, quick donor search, blood group cards, live statistics and blood donation awareness
- **Find Donor**: search by blood group and city, available donors are listed first
- **Donor Registration**: name, age, gender, blood group, phone, city, email, last donation date, availability
- **Request Blood**: patient, blood group, hospital, location, units, contact number, urgency (Normal / Urgent / Emergency)
- **Blood Requests**: active requests sorted by urgency, with a "Mark fulfilled" option
- **Statistics**: total donors, total requests, successful connections, blood groups available, donors per blood group
- **Donor Profile**: basic details, location and availability status
- **Contact Donor**: phone number stays masked until the person confirms they need blood, then Call and WhatsApp buttons appear
- **About Us**: purpose, how it works and blood donation basics
- **Responsive design** for mobile, tablet and desktop

## Smart rules

- A donor is shown as **Available** only if they marked themselves available **and** their last donation was at least **90 days** ago
- Duplicate phone numbers are not allowed
- All forms are validated in the browser (Bootstrap) and again on the server (Flask)

## Tech stack

| Part | Technology |
|------|------------|
| Backend | Python, Flask |
| Database | SQLite (local) / PostgreSQL (deployment) |
| Frontend | HTML, CSS, JavaScript, Bootstrap 5 |
| Templates | Jinja2 |
| Production server | Gunicorn |

## Project structure

```
rs-flask/
├── app.py               # Flask routes, SQLite queries, validation
├── requirements.txt     # Python packages
├── templates/           # HTML pages (Jinja2)
│   ├── base.html        # navbar, footer, contact modal
│   ├── home.html
│   ├── find.html
│   ├── register.html
│   ├── request.html
│   ├── requests.html
│   ├── stats.html
│   ├── donor.html
│   ├── about.html
│   └── 404.html
└── static/
    ├── style.css        # dark theme and custom styles
    └── app.js           # form validation, contact modal
```

## Database

The tables are created automatically on first run with sample data (SQLite file `raktsetu.db` locally, PostgreSQL when `DATABASE_URL` is set).

| Table | Purpose |
|-------|---------|
| `donors` | id, name, age, gender, bg, phone, city, email, last_donation, available |
| `requests` | id, patient, bg, hospital, city, units, phone, urgency, created, fulfilled |
| `connections` | id, kind, ref_id, created (counts successful connections) |

## Run locally

1. Install Python 3.9 or newer.
2. Clone the repository and open the project folder in a terminal:
   ```
   git clone https://github.com/YOUR-USERNAME/raktsetu-blood-donor-finder.git
   cd raktsetu-blood-donor-finder
   ```
3. (Optional) create a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # Mac / Linux
   ```
4. Install the packages:
   ```
   pip install -r requirements.txt
   ```
5. Start the app:
   ```
   python app.py
   ```
6. Open http://127.0.0.1:5000 in your browser.

To reset the data, delete `raktsetu.db` and run the app again.

## Deploy on Render with a permanent database

Render's free web service has a temporary file system, so SQLite data would be lost on every restart. To keep data permanently, use a free PostgreSQL database (for example [Neon](https://neon.tech)). The app switches to PostgreSQL automatically when the `DATABASE_URL` environment variable is set. Without it, the app uses the local SQLite file.

1. Create a free project on [neon.tech](https://neon.tech) and copy the connection string.
2. Push this project to GitHub.
3. On [render.com](https://render.com) create a **New > Web Service** and connect the repository.
4. Use these settings:
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn app:app`
   - Environment variables:
     - `DATABASE_URL` = the Neon connection string
     - `SECRET_KEY` = any long random string
5. Deploy. Tables and sample data are created automatically on the first start.

Note: free web services on Render sleep after a period of inactivity, so the first page load can take around a minute. Your data stays safe in the database.

## Privacy note

Donor phone numbers and emails are never placed in the page HTML. The phone number is fetched only after the user confirms they need blood.

## Disclaimer

This is an educational project. In a real emergency, please contact your nearest hospital or blood bank as well.

## Author

Your Name - BSc Computer Science mini project
