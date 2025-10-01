# app/tasks.py
import json
from datetime import datetime
from celery_app import celery
from models import period_bounds
from storage_svc import list_entries, write_summaries

# Factors inline (match /api/factors)
FACTORS = {
    ("electricity","kWh"): 0.10,
    ("petrol","L"): 2.31,
    ("diesel","L"): 2.68,
    ("beef","serving"): 5.0,
    ("chicken","serving"): 1.5,
    ("flight_shorthaul","km"): 0.15,
}

@celery.task()
def recalc_summaries_task(message):
    payload = json.loads(message) if isinstance(message, str) else message
    if payload.get("type") != "recalc":
        return
    user_id = int(payload["user_id"])

    entries = list_entries(user_id, limit=10000)
    buckets = {"daily":{}, "weekly":{}, "monthly":{}}

    for e in entries:
        try:
            t = datetime.fromisoformat(e["occurred_at"])
        except Exception:
            continue
        f = FACTORS.get((e["category"], e["unit"]))
        if f is None:
            continue
        kg = float(e["quantity"]) * f
        for p in buckets.keys():
            s, e_ = period_bounds(t, p)
            key = (s.isoformat(), e_.isoformat())
            buckets[p][key] = buckets[p].get(key, 0.0) + kg

    for p, m in buckets.items():
        rows = [
            {"period": p, "start": s, "end": e, "kg_co2e": round(v, 6)}
            for (s, e), v in sorted(m.items(), key=lambda x: x[0], reverse=True)
        ]
        write_summaries(user_id, p, rows)