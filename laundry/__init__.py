import os
from decimal import Decimal, InvalidOperation

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_wtf.csrf import CSRFError, CSRFProtect

csrf = CSRFProtect()


def create_app(test_config=None):
    load_dotenv()
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY=os.getenv("SECRET_KEY"),
        APP_MODE=os.getenv("APP_MODE", "demo"),
        MYSQL_HOST=os.getenv("MYSQL_HOST", "127.0.0.1"),
        MYSQL_PORT=int(os.getenv("MYSQL_PORT", "3306")),
        MYSQL_DATABASE=os.getenv("MYSQL_DATABASE", "dinas_laundry"),
        MYSQL_USER=os.getenv("MYSQL_USER", "dinas_app"),
        MYSQL_PASSWORD=os.getenv("MYSQL_PASSWORD", ""),
        MYSQL_SSL_CA=os.getenv("MYSQL_SSL_CA") or None,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.getenv("SESSION_COOKIE_SECURE", "false").lower() == "true",
        WTF_CSRF_TIME_LIMIT=7200,
        MAX_CONTENT_LENGTH=16 * 1024,
        MAX_FORM_PARTS=20,
        RATE_WASH_FOLD=os.getenv("RATE_WASH_FOLD", "65.00"),
        RATE_IRONING=os.getenv("RATE_IRONING", "80.00"),
        RATE_BEDDING=os.getenv("RATE_BEDDING", "100.00"),
    )
    if test_config:
        app.config.update(test_config)
    secret = app.config.get("SECRET_KEY")
    if not secret or len(secret) < 32 or secret.startswith("replace-"):
        raise RuntimeError("Set SECRET_KEY to a randomly generated value of at least 32 characters in .env.")
    if app.config["APP_MODE"] not in {"demo", "live"}:
        raise RuntimeError("APP_MODE must be demo or live.")
    for key in ("RATE_WASH_FOLD", "RATE_IRONING", "RATE_BEDDING"):
        try:
            rate = Decimal(str(app.config[key]))
            if not rate.is_finite() or rate <= 0 or rate > 10000 or rate.as_tuple().exponent < -2:
                raise ValueError()
        except (InvalidOperation, ValueError):
            raise RuntimeError(f"{key} must be a positive peso rate with at most two decimal places.") from None
        app.config[key] = rate
    csrf.init_app(app)

    from .routes import bp
    from .db import register_commands
    app.register_blueprint(bp)
    register_commands(app)

    def error_response(message, status):
        if request.accept_mimetypes.best == "application/json":
            return jsonify(ok=False, message=message), status
        return render_template("error.html", message=message), status

    @app.errorhandler(CSRFError)
    def csrf_error(_error):
        return error_response("Your form has expired. Reload this page and submit again.", 400)

    @app.errorhandler(413)
    def too_large(_error):
        return error_response("This request is too large. Shorten your address or instructions and try again.", 413)

    @app.errorhandler(404)
    def not_found(_error):
        return error_response("That page could not be found. Return to the home page to request a pickup.", 404)

    @app.after_request
    def security_headers(response):
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; font-src 'self'; connect-src 'self'; "
            "form-action 'self'; frame-ancestors 'none'; base-uri 'self'; object-src 'none'"
        )
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        if request.endpoint != "static":
            response.headers["Cache-Control"] = "no-store"
        if app.config["SESSION_COOKIE_SECURE"]:
            response.headers["Strict-Transport-Security"] = "max-age=31536000"
        return response

    return app
