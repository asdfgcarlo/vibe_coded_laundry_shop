# Verification record

Verified locally on November 1, 2026. Python 3.14, Flask 3.1.3, MySQL Community Server 8.4.13, and isolated headless Google Chrome were used. No real customer data was used.

- **32 Python tests passed**, including real MySQL persistence read through a fresh connection, duplicate-safe retries, bound SQL-shaped values, validation, CSRF, session-owned request tokens, failed commit rollback, demo refusal, safe HTML escaping, no-JavaScript responses, privacy, and estimate rounding.
- **2 JavaScript calculator tests passed**, covering the three services, decimal arithmetic, formatting, invalid input, and weight limits.
- **Demo and live browser suites passed** at 320, 390, 768, and 1440 px. No horizontal overflow was found. Checked mobile menu/Escape, estimate transfer, error focus, demo submission refusal, successful MySQL-backed submission and reference display, reduced motion, and no-JavaScript server validation.
- **Automated axe WCAG A/AA checks found zero violations** in the tested state. These checks supplement visual and keyboard checks; they are not an accessibility certification.
- **pip check passed** and Python compilation completed without errors.
- **Independent Impeccable finish review: ship**, with no material design fixes. The detector’s Fraunces frequency warning was assessed against the actual rendering and was not considered a material defect. The Jinja stylesheet URL could not be resolved by the detector; the CSS was also supplied directly.
- The hero asset provenance scan found **1 raster, 0 missing**.

Evidence is in `.impeccable/review/`, including `browser-demo-report.json`, `browser-live-report.json`, desktop/tablet/phone captures, section crops, and a synthetic live booking confirmation. Final general screenshots show demo mode; the successful booking capture came from the separate disposable live test instance.

The temporary preview processes were shut down after the initial verification and the synthetic browser booking was removed from the test database. Local bookings were subsequently enabled in a separate persistent `dinas_laundry` database on loopback port 3307. A real HTTP pickup POST to the running app returned 201, and its reference matched a committed row read through a fresh MySQL connection. Only that synthetic verification row was removed afterward.

The current ignored `.env` uses `APP_MODE=live`; the local MySQL server and Flask app are running for actual local use. `scripts/start-local.ps1` starts the existing local database and app after a restart. The initial visual screenshots remain evidence of the explicitly labeled demo state; the current live page omits the preview notice. See `README.md` for the current local configuration.

Not tested: physical iOS/Android devices, Safari, Firefox, a public production deployment, real shop rates or hours, SMS/email delivery, or a staff dashboard. The latter integrations are not implemented or claimed by this site.
