from datetime import timedelta
from decimal import Decimal
from unittest.mock import Mock

import pymysql
import pytest

from conftest import form_tokens
from laundry.services import estimate
from laundry.validation import date_limits, validate_booking


def test_home_has_csrf_sample_prices_and_security_headers(client):
    response = client.get("/")
    page = response.get_data(as_text=True)
    assert "csrf_token" in page and "Sample rate" in page and "[Phone number to be confirmed]" in page
    assert "frame-ancestors 'none'" in response.headers["Content-Security-Policy"]
    assert response.headers["Cache-Control"] == "no-store"
    assert "HttpOnly" in response.headers["Set-Cookie"]


def test_missing_and_invalid_csrf_never_reaches_save(client, valid_data, monkeypatch):
    save = Mock()
    monkeypatch.setattr("laundry.routes.save_booking", save)
    assert client.post("/pickup-requests", data=valid_data).status_code == 400
    tokens = form_tokens(client)
    tokens["csrf_token"] = "tampered"
    assert client.post("/pickup-requests", data=valid_data | tokens).status_code == 400
    save.assert_not_called()


@pytest.mark.parametrize("field,value", [
    ("name", " "), ("name", "x" * 101), ("phone", "123"), ("address", "short"),
    ("service", "unknown"), ("weight", "0"), ("weight", "100.1"),
    ("weight", "NaN"), ("weight", "Infinity"), ("weight", "1e1"), ("weight", "1.25"),
    ("date", "2020-01-01"), ("date", "2099-01-01"), ("date", "2026-02-30"),
    ("time", "midnight"), ("instructions", "x" * 1001),
])
def test_invalid_fields_rejected_before_database(client, valid_data, monkeypatch, field, value):
    save = Mock()
    monkeypatch.setattr("laundry.routes.save_booking", save)
    response = client.post("/pickup-requests", data=valid_data | form_tokens(client) | {field: value}, headers={"Accept": "application/json"})
    assert response.status_code == 422
    assert field in response.json["errors"]
    save.assert_not_called()


def test_date_boundaries_and_phone_normalization(valid_data):
    minimum, maximum = date_limits()
    for date in (minimum, maximum):
        data, errors = validate_booking(valid_data | {"date": date.isoformat(), "phone": "+63 (917) 123-4567"})
        assert not errors and data["phone"] == "+639171234567"
    for date in (minimum - timedelta(days=1), maximum + timedelta(days=1)):
        assert "date" in validate_booking(valid_data | {"date": date.isoformat()})[1]


def test_json_success_only_after_repository_returns(client, valid_data, monkeypatch):
    save = Mock(return_value="DINA-123456ABCDEF")
    monkeypatch.setattr("laundry.routes.save_booking", save)
    response = client.post("/pickup-requests", data=valid_data | form_tokens(client) | {"estimated_total": "1", "rate": "1"}, headers={"Accept": "application/json"})
    assert response.status_code == 201 and response.json["reference"] == "DINA-123456ABCDEF"
    assert save.call_args.args[2] == Decimal("357.50")
    assert save.call_args.args[3] == Decimal("65.00")
    assert "Test Customer" not in response.get_data(as_text=True)


def test_database_failure_has_no_confirmation_or_driver_data(client, valid_data, monkeypatch, caplog):
    monkeypatch.setattr("laundry.routes.save_booking", Mock(side_effect=pymysql.OperationalError(2003, "Test Customer secret failure")))
    response = client.post("/pickup-requests", data=valid_data | form_tokens(client), headers={"Accept": "application/json"})
    assert response.status_code == 503 and not response.json["ok"]
    assert "reference" not in response.json
    assert "Test Customer" not in response.get_data(as_text=True) + caplog.text


def test_demo_never_saves(app, client, valid_data, monkeypatch):
    app.config["APP_MODE"] = "demo"
    save = Mock()
    monkeypatch.setattr("laundry.routes.save_booking", save)
    response = client.post("/pickup-requests", data=valid_data | form_tokens(client), headers={"Accept": "application/json"})
    assert response.status_code == 503 and "preview" in response.json["message"]
    save.assert_not_called()


def test_nonce_belongs_to_session(client, app, valid_data, monkeypatch):
    save = Mock()
    monkeypatch.setattr("laundry.routes.save_booking", save)
    tokens = form_tokens(client)
    other = app.test_client()
    other_tokens = form_tokens(other)
    response = other.post("/pickup-requests", data=valid_data | other_tokens | {"request_key": tokens["request_key"]})
    assert response.status_code == 400
    save.assert_not_called()


def test_no_javascript_errors_preserve_and_escape_input(client, valid_data):
    response = client.post("/pickup-requests", data=valid_data | form_tokens(client) | {"phone": "bad", "name": '<script>alert("x")</script>'})
    page = response.get_data(as_text=True)
    assert response.status_code == 422 and "&lt;script&gt;" in page and '<script>alert("x")</script>' not in page
    assert "bad" in page and "phone-error" in page


def test_no_javascript_confirmation(client, valid_data, monkeypatch):
    monkeypatch.setattr("laundry.routes.save_booking", Mock(return_value="DINA-123456ABCDEF"))
    response = client.post("/pickup-requests", data=valid_data | form_tokens(client))
    assert response.status_code == 201 and "DINA-123456ABCDEF" in response.get_data(as_text=True)


def test_estimates_are_decimal_and_service_specific(app):
    with app.app_context():
        assert estimate("wash-fold", Decimal("5.5")) == Decimal("357.50")
        assert estimate("ironing", Decimal("0.5")) == Decimal("40.00")
        assert estimate("bedding", Decimal("100")) == Decimal("10000.00")


def test_customer_data_not_publicly_retrievable(client):
    assert client.get("/pickup-requests").status_code == 405
    assert client.get("/bookings").status_code == 404


def test_commit_failure_rolls_back_and_closes(app, valid_data, monkeypatch):
    from laundry.db import save_booking
    booking, errors = validate_booking(valid_data)
    assert not errors
    connection = Mock()
    connection.cursor.return_value.__enter__ = Mock(return_value=Mock())
    connection.cursor.return_value.__exit__ = Mock(return_value=False)
    connection.commit.side_effect = pymysql.OperationalError(2013, "Lost connection")
    monkeypatch.setattr("laundry.db.connect", Mock(return_value=connection))
    with app.app_context(), pytest.raises(pymysql.OperationalError):
        save_booking(booking, "a" * 32, Decimal("357.50"), Decimal("65.00"))
    connection.rollback.assert_called_once()
    connection.close.assert_called_once()


def test_oversized_request_is_rejected(client):
    assert client.post("/pickup-requests", data={"instructions": "x" * 20000}).status_code == 413


def test_malformed_nonce_is_a_validation_error(client, valid_data):
    tokens = form_tokens(client)
    response = client.post("/pickup-requests", data=valid_data | tokens | {"request_key": "é" * 32})
    assert response.status_code == 400


def test_half_cent_estimates_match_javascript(app):
    with app.app_context():
        app.config["RATE_WASH_FOLD"] = Decimal("65.55")
        assert estimate("wash-fold", Decimal("0.7")) == Decimal("45.89")
