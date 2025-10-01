# app/models.py
from datetime import datetime, timedelta

def period_bounds(dt: datetime, period: str):
    if period == "daily":
        start = datetime(dt.year, dt.month, dt.day)
        end = start + timedelta(days=1)
    elif period == "weekly":
        start = datetime(dt.year, dt.month, dt.day) - timedelta(days=dt.weekday())
        end = start + timedelta(days=7)
    elif period == "monthly":
        start = datetime(dt.year, dt.month, 1)
        end = datetime(dt.year + (dt.month == 12), (dt.month % 12) + 1, 1)
    else:
        raise ValueError("invalid period")
    return start, end