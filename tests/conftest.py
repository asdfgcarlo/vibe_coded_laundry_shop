import html
import re

import pytest

from laundry import create_app
from laundry.validation import date_limits


@pytest.fixture
def app():
    return create_app({"TESTING": True, "SECRET_KEY": "test-only-secret-" * 4, "APP_MODE": "live"})


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def valid_data():
    return {"name": "Test Customer", "phone": "0917 123 4567", "address": "12 Test Street, Test Barangay, Test City",
            "service": "wash-fold", "weight": "5.5", "date": date_limits()[0].isoformat(),
            "time": "morning", "instructions": "Test record only."}


def form_tokens(client):
    response = client.get("/")
    assert response.status_code == 200
    page = response.get_data(as_text=True)
    return {name: html.unescape(re.search(fr'name="{name}" value="([^"]+)"', page).group(1))
            for name in ("csrf_token", "request_key")}
