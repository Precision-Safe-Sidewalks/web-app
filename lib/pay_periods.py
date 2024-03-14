import math
from datetime import date, timedelta


REFERENCE_START = date(2024, 3, 9)


def get_pay_periods(min_date, max_date, days=14):
    """Get all the pay periods in the date range"""
    assert max_date >= min_date

    min_period = math.floor((min_date - REFERENCE_START).days / days)
    max_period = math.ceil(((max_date - REFERENCE_START).days + 1) / days)
    periods = []

    for n in range(min_period, max_period):
        offset = timedelta(days=days * n)
        start = REFERENCE_START + offset
        end = start + timedelta(days=days - 1)
        periods.append([start, end])

    return periods
