# RaktSetu | Build and run guide

RaktSetu is a responsive blood donor finder and request board. The project is based on the supplied `RaktSetu-FINAL.zip` source and is packaged here as a ready-to-run Flask project.

## Technology used

- **Python 3.9+** — application and server-side validation.
- **Flask** — web framework and URL routing.
- **SQLite** — local database created automatically as `raktsetu.db`.
- **PostgreSQL (optional)** — supported when `DATABASE_URL` is configured; `psycopg2-binary` is used on supported non-Windows deployments.
- **HTML5 + Jinja2** — page markup and server-rendered templates.
- **CSS3** — responsive layout, color theme, and custom components.
- **JavaScript** — Bootstrap form validation and the donor-contact dialog.
- **Bootstrap 5.3.3** — responsive components and carousel, loaded from CDN.
- **Gunicorn** — production WSGI server (deployment).

## Pages and features

- Home page with an image-free hero carousel, quick search, blood-group cards, statistics, and donation information.
- Donor search by blood group and city; available donors are listed first.
- Donor registration and donor profiles.
- Blood request submission and a priority-sorted request board.
- Statistics, About page, and custom 404 page.
- Contact confirmation dialog; a donor's phone number is revealed only after the visitor confirms they need blood.
- Availability requires both the donor's opt-in and a 90-day interval since their last donation.

## Project layout

```text
RaktSetu/
├── app.py                 Flask routes, validation, database access, seed data
├── requirements.txt       Python dependencies
├── README.md              Project overview and deployment notes
├── README_PROCESS.md      This setup and implementation guide
├── templates/             Jinja2 pages
│   ├── base.html           Shared navigation, footer, contact dialog
│   ├── home.html           Landing page
│   ├── find.html           Donor search and results
│   ├── register.html       Donor registration form
│   ├── donor.html          Donor profile
│   ├── request.html        Blood request form
│   ├── requests.html       Request board
│   ├── stats.html          Statistics page
│   ├── about.html          About and how it works
│   ├── _stats.html         Reusable statistics component
│   └── 404.html            Not-found page
└── static/
    ├── style.css           Theme and responsive styling
    └── app.js              Form validation and contact flow
```

## Run on Windows

1. Install Python 3.9 or newer. During installation, enable **Add Python to PATH**.
2. Extract this folder or open it in a terminal.
3. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal and activate again. Alternatively, skip activation and use `.venv\Scripts\python.exe` in the commands below.

4. Install dependencies:

   ```powershell
   py -m pip install -r requirements.txt
   ```

5. Start the development server:

   ```powershell
   py app.py
   ```

6. Open [http://127.0.0.1:5000](http://127.0.0.1:5000).

The first startup creates the local SQLite tables and adds sample donor/request records. To reset this demo database, stop the server and delete `raktsetu.db`; it will be recreated at the next startup.

## Run on macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000`.

## How the project works

1. A browser requests a URL such as `/find`.
2. Flask in `app.py` handles the route, reads query parameters or submitted form fields, and applies server-side validation.
3. The `Conn` wrapper runs parameterized SQL against SQLite by default or PostgreSQL when `DATABASE_URL` is configured.
4. Flask passes the results to a Jinja2 template under `templates/`.
5. The browser renders the HTML and styles from `static/style.css`; `static/app.js` handles client-side validation and contact-modal behavior.
6. Donor contact is a POST request to `/contact/<id>`. The server returns contact details only after the visitor presses the confirmation button.

## Database tables

- `donors`: donor details, donation date, and availability preference.
- `requests`: patient blood requests, urgency, and fulfilled status.
- `connections`: successful contact/fulfillment counts used by statistics.

For an external PostgreSQL database, set `DATABASE_URL` to its connection URL before starting the app. Set a strong `SECRET_KEY` for deployment. The included README has Render deployment notes. Bootstrap and Google Fonts are loaded from external CDNs, so an internet connection is needed for those assets; the locally stored app pages and styles remain in this project.

## Important project note

This is an educational demonstration with seeded sample data. Do not use the sample phone numbers or rely on this app for emergency medical coordination. In a real emergency, contact a hospital or blood bank. Before a public production launch, add authentication and authorization for actions such as marking a request fulfilled, configure HTTPS, review privacy and data-retention requirements, and use real consented data.
