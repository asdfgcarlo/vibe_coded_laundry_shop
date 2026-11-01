import secrets
from pathlib import Path

import click
import pymysql
from flask import current_app
from pymysql.cursors import DictCursor


def connect():
    config = current_app.config
    options = {
        "host": config["MYSQL_HOST"], "port": config["MYSQL_PORT"],
        "user": config["MYSQL_USER"], "password": config["MYSQL_PASSWORD"],
        "database": config["MYSQL_DATABASE"], "charset": "utf8mb4",
        "cursorclass": DictCursor, "autocommit": False,
        "connect_timeout": 5, "read_timeout": 10, "write_timeout": 10,
    }
    if config["MYSQL_SSL_CA"]:
        options.update(ssl_ca=config["MYSQL_SSL_CA"], ssl_verify_cert=True, ssl_verify_identity=True)
    return pymysql.connect(**options)


def save_booking(booking, request_key, total, rate):
    """Return only a reference, after commit. A nonce makes network retries safe."""
    reference = "DINA-" + secrets.token_hex(6).upper()
    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """INSERT INTO pickup_requests
                (reference, request_key, customer_name, phone, pickup_address, service,
                 estimated_weight, preferred_date, preferred_time, instructions,
                 sample_rate, estimated_total)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (reference, request_key, booking["name"], booking["phone"], booking["address"],
                 booking["service"], booking["weight"], booking["date"], booking["time"],
                 booking["instructions"], rate, total),
            )
        connection.commit()
        return reference
    except pymysql.IntegrityError as error:
        connection.rollback()
        if error.args[0] != 1062:
            raise
        # The key is a signed session-owned nonce; never search by customer data.
        with connection.cursor() as cursor:
            cursor.execute("SELECT reference FROM pickup_requests WHERE request_key = %s", (request_key,))
            existing = cursor.fetchone()
        if existing:
            return existing["reference"]
        raise
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def register_commands(app):
    @app.cli.command("init-db")
    def init_db():
        """Create the request table in the configured, existing MySQL database."""
        schema = (Path(__file__).parent.parent / "schema.sql").read_text(encoding="utf-8")
        connection = connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute(schema)
            connection.commit()
        finally:
            connection.close()
        click.echo("MySQL pickup_requests table is ready.")

    @app.cli.command("check-db")
    def check_db():
        """Check the database and table without printing customer data."""
        connection = connect()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM pickup_requests LIMIT 0")
        finally:
            connection.close()
        click.echo("MySQL connection and pickup_requests table are ready.")
