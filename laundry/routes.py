import re
import secrets

import pymysql
from flask import Blueprint, current_app, jsonify, render_template, request, session

from .db import save_booking
from .services import estimate, get_services
from .validation import TIME_SLOTS, date_limits, validate_booking

bp = Blueprint("main", __name__)


def page_context():
    minimum, maximum = date_limits()
    return dict(services=get_services(), time_slots=TIME_SLOTS, min_date=minimum.isoformat(),
                max_date=maximum.isoformat(), demo=current_app.config["APP_MODE"] == "demo")


@bp.get("/")
def index():
    if session.get("last_booking_nonce") == session.get("booking_nonce"):
        session["booking_nonce"] = secrets.token_hex(16)
        session.pop("last_booking_nonce", None)
    session.setdefault("booking_nonce", secrets.token_hex(16))
    return render_template("index.html", values={}, errors={}, **page_context())


@bp.post("/pickup-requests")
def pickup_request():
    wants_json = request.accept_mimetypes.best == "application/json"

    def respond(message, status, errors=None):
        if wants_json:
            return jsonify(ok=False, message=message, errors=errors or {}), status
        # Never put customer details in a redirect URL or a cookie.
        return render_template("index.html", values=request.form, errors=errors or {},
                               form_message=message, **page_context()), status

    nonce = request.form.get("request_key", "")
    expected = session.get("booking_nonce", "")
    if not re.fullmatch(r"[a-f0-9]{32}", nonce) or not expected or not secrets.compare_digest(nonce, expected):
        return respond("Your form has expired. Reload this page and try again.", 400)

    booking, errors = validate_booking(request.form)
    if errors:
        return respond("Please check the highlighted fields and submit again.", 422, errors)
    if current_app.config["APP_MODE"] != "live":
        return respond("This is a preview. Pickup requests are not being saved. The shop must enable bookings before you can request a pickup.", 503)

    services = get_services()
    try:
        reference = save_booking(booking, nonce, estimate(booking["service"], booking["weight"]),
                                 services[booking["service"]]["rate"])
    except pymysql.MySQLError:
        # Do not log exceptions: driver messages can contain submitted customer data.
        current_app.logger.error("Pickup request database operation failed; customer data omitted.")
        return respond("We couldn’t confirm your request. Your details are still in the form. Please try again; retrying will not create a second request.", 503)

    # Keep this nonce for safe retries if the response is lost. Reloading the
    # page after a successful response starts a fresh request with a new nonce.
    session["last_booking_nonce"] = nonce
    if wants_json:
        return jsonify(ok=True, reference=reference, message="Your pickup request has been saved."), 201
    return render_template("confirmation.html", reference=reference), 201


@bp.get("/new-request")
def new_request():
    from flask import redirect, url_for
    session["booking_nonce"] = secrets.token_hex(16)
    return redirect(url_for("main.index", _anchor="pickup"))
