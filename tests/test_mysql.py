"""Opt-in real MySQL tests. A dedicated *_test database is mandatory."""
import os
import secrets
from decimal import Decimal
from pathlib import Path

import pytest

from conftest import form_tokens
from laundry import create_app
from laundry.db import connect

pytestmark = pytest.mark.skipif(os.getenv("RUN_MYSQL_TESTS") != "1", reason="Set RUN_MYSQL_TESTS=1 and TEST_MYSQL_* for a dedicated MySQL test database.")


@pytest.fixture
def mysql_app():
    database = os.getenv("TEST_MYSQL_DATABASE", "dinas_laundry_test")
    assert database.endswith("_test"), "Use a dedicated database ending in _test."
    app = create_app({"TESTING": True, "SECRET_KEY": "mysql-test-secret-" * 4, "APP_MODE": "live",
                      "MYSQL_HOST": os.getenv("TEST_MYSQL_HOST", "127.0.0.1"),
                      "MYSQL_PORT": int(os.getenv("TEST_MYSQL_PORT", "3306")),
                      "MYSQL_DATABASE": database, "MYSQL_USER": os.getenv("TEST_MYSQL_USER", "dinas_test"),
                      "MYSQL_PASSWORD": os.getenv("TEST_MYSQL_PASSWORD", "")})
    with app.app_context():
        connection = connect()
        with connection.cursor() as cursor:
            cursor.execute((Path(__file__).parent.parent / "schema.sql").read_text())
        connection.commit()
        connection.close()
    return app


def test_persistence_retry_and_parameterized_data(mysql_app, valid_data):
    client = mysql_app.test_client()
    tokens = form_tokens(client)
    # Intentionally SQL-shaped customer text must be stored as literal data.
    name = "Test O'Neil '); DROP TABLE pickup_requests; --"
    data = valid_data | tokens | {"name": name, "instructions": "Test-only " + secrets.token_hex(5)}
    try:
        first = client.post("/pickup-requests", data=data, headers={"Accept": "application/json"})
        assert first.status_code == 201
        second = client.post("/pickup-requests", data=data, headers={"Accept": "application/json"})
        assert second.status_code == 201 and first.json["reference"] == second.json["reference"]
        # A separate connection proves the insert was committed and survives reconnect.
        with mysql_app.app_context():
            connection = connect()
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM pickup_requests WHERE request_key = %s", (tokens["request_key"],))
                rows = cursor.fetchall()
            connection.close()
        assert len(rows) == 1 and rows[0]["customer_name"] == name
        assert rows[0]["estimated_total"] == Decimal("357.50")
        assert rows[0]["phone"] == "+639171234567" and rows[0]["status"] == "requested"
        assert rows[0]["reference"] == first.json["reference"]
    finally:
        # Delete only the test row created by this test's unguessable nonce.
        with mysql_app.app_context():
            connection = connect()
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM pickup_requests WHERE request_key = %s", (tokens["request_key"],))
            connection.commit()
            connection.close()
