# Dina’s Laundry Shop

A complete responsive laundry service website using **HTML, CSS, vanilla JavaScript, Flask/Jinja, and MySQL**. No replacement frontend framework or database is used.

The site includes an original SVG brand, locally hosted fonts, a generated linen still life, service and sample pricing information, an estimate calculator, pickup requests, FAQs, contact placeholders, and business hour placeholders. The visual system was developed with the Impeccable skill; see `DESIGN.md` and `PRODUCT.md`.

## Requirements

- Python 3.11 or newer, with pip and venv
- MySQL Community Server 8.0.16+ (8.4 LTS recommended); **MySQL Shell by itself is not a database server**
- Node.js 20.19+ and Google Chrome only if running the optional JavaScript/browser checks

## This workspace: live local bookings are enabled

The current `.env` is configured with `APP_MODE=live` and a dedicated `dinas_laundry` MySQL database on **127.0.0.1:3307**. The app runs at **http://127.0.0.1:5000**. Valid pickup requests are saved to MySQL and receive a reference after a successful commit.

To start or restart the local setup after closing it or restarting Windows, run:

```powershell
.\scripts\start-local.ps1
```

The helper starts the existing portable MySQL instance if needed, checks the configured database, and starts Flask if port 5000 is free. Both run in the background with logs in `.runtime/`. It preserves existing database contents and does not reinstall MySQL or create a Windows service. If you already have Flask running when you change `.env`, restart that Flask process to load the new settings.

Local booking data lives in **`.runtime/mysql-data`**. Preserve and back up that directory; `.runtime` and `.env` are ignored by Git. This is a functioning local installation, with no public deployment or customer notifications. The fresh-install instructions below still default to demo mode until MySQL is configured.

## 1. Install and preview locally

In PowerShell, from this folder:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_hex(32))"
```

Put the generated value in `SECRET_KEY` in `.env`. Leave `APP_MODE=demo` for the preview, then run:

```powershell
.\.venv\Scripts\python.exe -m flask --app app run --host 127.0.0.1 --port 5000
```

Open **http://127.0.0.1:5000**. If the Windows `py` launcher cannot find Python, use the full path to your installed Python executable to create `.venv`. On the development machine it was found at `%LOCALAPPDATA%\Programs\Python\Python314\python.exe`.

macOS/Linux equivalents:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
.venv/bin/python -c 'import secrets; print(secrets.token_hex(32))'
# Set SECRET_KEY in .env, then:
.venv/bin/python -m flask --app app run --host 127.0.0.1 --port 5000
```

An ignored `.env` may already exist from local verification. Preserve its generated secret, or generate a new one yourself; replacing it expires existing form sessions.

## 2. Enable real MySQL booking saves

Start MySQL Server. Sign in to its SQL client as a database administrator:

```text
mysql -u root -p
```

Create an empty database and a dedicated local application user. Replace the password with a strong unique value:

```sql
CREATE DATABASE dinas_laundry
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'dinas_app'@'127.0.0.1' IDENTIFIED BY 'replace-with-a-strong-password';
GRANT SELECT, INSERT, CREATE ON dinas_laundry.* TO 'dinas_app'@'127.0.0.1';
```

Set these values in `.env`:

```dotenv
APP_MODE=live
MYSQL_HOST=127.0.0.1
MYSQL_PORT=3306
MYSQL_DATABASE=dinas_laundry
MYSQL_USER=dinas_app
MYSQL_PASSWORD=your-strong-password
```

Keep the secret key generated earlier. Initialize the table and check the connection:

```powershell
.\.venv\Scripts\python.exe -m flask --app app init-db
.\.venv\Scripts\python.exe -m flask --app app check-db
```

`init-db` applies the initial `schema.sql` using `CREATE TABLE IF NOT EXISTS`; it does not drop data or migrate an existing different table. After initialization, remove the DDL privilege in the administrator’s SQL session:

```sql
REVOKE CREATE ON dinas_laundry.* FROM 'dinas_app'@'127.0.0.1';
```

The runtime only needs **SELECT and INSERT**. Restart Flask after changing environment settings. Submit a request: a `DINA-` reference appears only after a successful MySQL commit. A missing database, table, or connection produces a recoverable error and retains form contents in the browser.

## Demo and working functionality

| Mode | Calculator and forms | Database behavior |
| --- | --- | --- |
| `APP_MODE=demo` | Real calculator, input validation, and visible preview notice | Submission returns HTTP 503 with an explicit preview message; **nothing is saved**, and no success is simulated. |
| `APP_MODE=live` | Same interface, with working pickup submission | Valid requests are inserted into MySQL; a reference is returned after commit. |

There is no browser-only or in-memory substitute for persistence. The real MySQL integration test was run against an isolated local MySQL 8.4 instance during development. The ignored `.runtime` directory contains the portable local MySQL installation, its durable data, and separate developer test infrastructure. This workspace now uses the dedicated `dinas_laundry` database in live mode; `.env.example` retains demo mode for new installations.

A saved request has status `requested`; it **does not confirm an appointment**. There is no SMS, email, online payment, staff dashboard, automatic scheduling, or notification integration. Staff must monitor the database through an appropriately secured internal workflow and contact customers themselves. This website never exposes a public booking list or a reference lookup endpoint.

## Rates and business information

Initial **illustrative** rates are ₱65/kg for wash/dry/fold, ₱80/kg for ironing, and ₱100/kg for bedding. They are not claims about the shop’s actual prices. `.env` can adjust the three rates; all are still labeled sample rates until the shop confirms and the copy is deliberately updated.

The calculator and backend share the same configured rate data. Estimates use service × estimated weight, rounded to centavos with half-up rounding. Weight must be 0.5–100 kg with at most one decimal place. Final cost depends on measured weight, item requirements, confirmed rates, and separately confirmed pickup/delivery charges. Each saved request stores its sample rate and estimate for context.

Update the visibly labeled placeholders in `laundry/templates/index.html` for the real address, phone, email, opening days/hours, service area, and turnaround information. The three time windows are explicitly sample preferences. Dates are validated in **Asia/Manila**, from tomorrow through 30 days ahead. No opening schedule or slot availability has been invented.

## Validation, privacy, and security

- Flask-WTF CSRF protection covers all POSTs; form tokens expire after two hours.
- Both JavaScript and Flask validate every customer field. Flask is authoritative.
- MySQL writes use bound parameters and explicit commit/rollback. Database uniqueness protects references and request tokens.
- Session-owned random request tokens make double clicks and network retries return the same saved reference. Reload after a saved request or use “Request another pickup” to start a new one. A database commit with a lost response can be recovered by retrying the same form.
- Customer details stay out of URLs, cookies, browser storage, and database-error logs. Session cookies contain only signed CSRF and random request identifiers.
- Jinja escapes submitted content. CSP, no framing, no content sniffing, SameSite/HttpOnly cookies, request-size limits, and no-store page responses are configured.
- For HTTPS deployment, set `SESSION_COOKIE_SECURE=true`. A remote MySQL connection can use `MYSQL_SSL_CA` to enable CA and hostname verification. Use a trusted MySQL certificate; leave this empty for loopback development.
- The site uses no analytics, external font requests, or third-party browser assets at runtime.

Before accepting real customers, configure HTTPS, confirmed shop details, a monitored staff workflow, appropriate backup/access/retention practices, and application or proxy rate limits. Do not expose the Flask development server, use root as the runtime database user, commit `.env`, or enable debug mode in production. These operational settings are not simulated by the demo.

## Run with a production WSGI server locally

Waitress is included and works on Windows and Unix:

```powershell
.\.venv\Scripts\waitress-serve.exe --host=127.0.0.1 --port=5000 app:app
```

Put a properly configured HTTPS reverse proxy in front for an actual deployment. No website has been published or exposed publicly by this project.

## Tests

Backend validation, CSRF, failed commits, privacy, no-JavaScript behavior, sample estimates, and failure/success responses:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

The real persistence test is opt-in. Create a separate empty database whose name ends in `_test`, with a dedicated test user allowed to SELECT, INSERT, DELETE, UPDATE, and CREATE. Then set:

```powershell
$env:RUN_MYSQL_TESTS = '1'
$env:TEST_MYSQL_HOST = '127.0.0.1'
$env:TEST_MYSQL_PORT = '3306'
$env:TEST_MYSQL_DATABASE = 'dinas_laundry_test'
$env:TEST_MYSQL_USER = 'dinas_test'
$env:TEST_MYSQL_PASSWORD = 'your-test-database-password'
.\.venv\Scripts\python.exe -m pytest -q
```

The test reads the saved row from a fresh connection, checks normalized values and the reference, retries the same request, and verifies there is exactly one row. It also proves SQL-shaped input is stored literally, then cleans up only its own test record. Ordinary tests skip this one when opt-in credentials are absent.

Optional JavaScript and headless responsive/accessibility checks (Flask must be running in demo mode on port 5000, and Chrome installed):

```powershell
npm.cmd ci
npm.cmd test
npm.cmd run test:ui
```

On Unix use `npm` instead of `npm.cmd`. The browser suite uses isolated headless Chrome, checks 320/390/768/1440 px widths, mobile navigation/Escape, estimate handoff, validation focus, preview rejection, reduced motion, no-JavaScript server validation, missing assets, and axe WCAG A/AA checks. Screenshots and the report are saved in `.impeccable/review/`. Automated accessibility checks supplement visual and keyboard inspection; they do not certify accessibility.

For a disposable **live test instance** only, set `BASE_URL` to its URL and `EXPECT_LIVE=1` before `npm run test:ui`. That path intentionally creates one synthetic pickup request in its database. Never point browser tests at a customer-facing instance. The live and demo browser reports from development are retained separately in `.impeccable/review/`.

## Project structure

```text
app.py                       Flask entry point
laundry/
  __init__.py                App factory, environment, CSRF, security headers
  routes.py                  Page and pickup POST handling
  validation.py              Server validation and Philippine date rules
  services.py                Shared sample rates and Decimal estimates
  db.py                      Parameterized MySQL repository and CLI commands
  templates/                 Jinja page, confirmation, and error templates
  static/css/style.css       Responsive design and reduced-motion rules
  static/js/                 Vanilla JS and independently testable calculator
  static/images/             Original SVG logo/favicon and hero asset
  static/fonts/              Self-hosted fonts with OFL licenses
schema.sql                   Initial MySQL schema
requirements*.txt            Runtime and test dependencies
tests/                       Python, calculator, and browser tests
.env.example                 Configuration example without secrets
PRODUCT.md / DESIGN.md       Product truth and implemented design system
```

## Assets and references

`laundry/static/images/logo.svg` is the original standalone logo; `favicon.svg` uses its drop-and-wave mark. The hero is an original generated image made with the built-in imagegen tool, optimized as `laundry/static/images/laundry-hero.webp`; its exact generation prompt is retained in the adjacent provenance JSON file. It is illustrative brand imagery, not a photograph of the shop. DM Sans and Fraunces are self-hosted under their included SIL Open Font Licenses, sourced from [Google Fonts](https://fonts.google.com/).

Implementation references: [Flask security guidance](https://flask.palletsprojects.com/en/stable/web-security/), [Flask-WTF CSRF](https://flask-wtf.readthedocs.io/en/1.2.x/csrf/), [PyMySQL parameterized query and commit examples](https://pymysql.readthedocs.io/en/latest/user/examples.html), and [MySQL Community Server](https://dev.mysql.com/downloads/mysql/8.4.html).
#   v i b e _ c o d e d _ l a u n d r y _ s h o p  
 