import re
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from zoneinfo import ZoneInfo

from .services import SERVICE_DEFINITIONS

MANILA = ZoneInfo("Asia/Manila")
TIME_SLOTS = {
    "morning": "Morning · 9 am–12 pm",
    "afternoon": "Afternoon · 12–3 pm",
    "late-afternoon": "Late afternoon · 3–6 pm",
}


def today_in_manila():
    return datetime.now(MANILA).date()


def date_limits():
    today = today_in_manila()
    return today + timedelta(days=1), today + timedelta(days=30)


def validate_booking(data):
    errors = {}
    cleaned = {}

    def value(key):
        raw = data.get(key, "")
        return raw.strip() if isinstance(raw, str) else ""

    for field, label, minimum, maximum in (
        ("name", "your full name", 2, 100),
        ("address", "your complete pickup address", 10, 500),
    ):
        text = value(field)
        if not minimum <= len(text) <= maximum or any(ord(c) < 32 and c not in "\n\r\t" for c in text):
            errors[field] = f"Enter {label} ({minimum}–{maximum} characters)."
        cleaned[field] = text

    phone = re.sub(r"[\s()\-]", "", value("phone"))
    if not re.fullmatch(r"(?:09\d{9}|\+639\d{9}|639\d{9})", phone):
        errors["phone"] = "Enter a Philippine mobile number, such as 0917 123 4567 or +63 917 123 4567."
    cleaned["phone"] = "+63" + phone[1:] if phone.startswith("09") else ("+" + phone if phone.startswith("63") else phone)

    service = value("service")
    if service not in SERVICE_DEFINITIONS:
        errors["service"] = "Choose one of the listed laundry services."
    cleaned["service"] = service

    try:
        raw_weight = value("weight")
        if not re.fullmatch(r"\d{1,3}(?:\.\d)?", raw_weight):
            raise ValueError()
        weight = Decimal(raw_weight)
        if not weight.is_finite() or not Decimal("0.5") <= weight <= Decimal("100"):
            raise ValueError()
        cleaned["weight"] = weight
    except (InvalidOperation, ValueError):
        errors["weight"] = "Enter a weight from 0.5 to 100 kg, using at most one decimal place."

    minimum, maximum = date_limits()
    try:
        raw_date = value("date")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw_date):
            raise ValueError()
        preferred_date = datetime.strptime(raw_date, "%Y-%m-%d").date()
        if not minimum <= preferred_date <= maximum:
            raise ValueError()
        cleaned["date"] = preferred_date
    except ValueError:
        errors["date"] = "Choose a date from tomorrow through the next 30 days (Philippine time)."

    time_slot = value("time")
    if time_slot not in TIME_SLOTS:
        errors["time"] = "Choose a preferred pickup time."
    cleaned["time"] = time_slot

    instructions = value("instructions")
    if len(instructions) > 1000 or any(ord(c) < 32 and c not in "\n\r\t" for c in instructions):
        errors["instructions"] = "Keep instructions within 1,000 characters and use ordinary text."
    cleaned["instructions"] = instructions
    return cleaned, errors
