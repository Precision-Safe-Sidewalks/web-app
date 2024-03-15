import math
from datetime import date, timedelta

REFERENCE_START = date(2024, 3, 9)


def get_pay_periods(min_date, max_date, days=14):
    """Get all the pay periods in the date range"""
    assert max_date >= min_date

    min_period = math.floor((min_date - REFERENCE_START).days / days)
    max_period = math.ceil(((max_date - REFERENCE_START).days + 1) / days)
    periods = []

    for period in range(min_period, max_period):
        d0, d1 = get_pay_period_dates(period, days=days)
        label = d0.strftime("%-m/%-d/%y") + " - " + d1.strftime("%-m/%-d/%y")
        periods.append({"key": period, "value": label})

    return periods


def get_pay_period_dates(period, days=14):
    """Get the dates for a pay period"""
    offset = timedelta(days=days * period)
    d0 = REFERENCE_START + offset
    d1 = d0 + timedelta(days=days - 1)
    return (d0, d1)
