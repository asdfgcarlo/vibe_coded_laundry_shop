from decimal import Decimal, ROUND_HALF_UP

from flask import current_app

SERVICE_DEFINITIONS = {
    "wash-fold": ("Wash, dry & fold", "RATE_WASH_FOLD"),
    "ironing": ("Ironing", "RATE_IRONING"),
    "bedding": ("Bedding", "RATE_BEDDING"),
}


def get_services():
    return {
        key: {"name": name, "rate": current_app.config[rate_key]}
        for key, (name, rate_key) in SERVICE_DEFINITIONS.items()
    }


def estimate(service, weight):
    return (get_services()[service]["rate"] * weight).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
