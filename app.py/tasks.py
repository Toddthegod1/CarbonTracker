import json
from datetime import datetime
from sqlalchemy import func
from celery_app import celery
from models import SessionLocal, Entry, EmissionFactor, Summary, period_bounds


@celery.task()
def recalc_summaries_task(message: str):
payload = json.loads(message) if isinstance(message, str) else message
if payload.get("type") != "recalc":
return
user_id = int(payload["user_id"]) # required
db = SessionLocal()
try:
# Join entries to factors and compute kg_co2e per entry
rows = db.query(
Entry.occurred_at.label("t"),
(Entry.quantity * EmissionFactor.kg_co2e_per_unit).label("kg")
).join(EmissionFactor, (Entry.category == EmissionFactor.category) & (Entry.unit == EmissionFactor.unit))\
.filter(Entry.user_id == user_id).all()


# Aggregate into three periods
periods = ["daily", "weekly", "monthly"]
acc = {p: {} for p in periods}
for t, kg in rows:
for p in periods:
start, end = period_bounds(t, p)
key = start
acc[p][key] = acc[p].get(key, 0.0) + float(kg)


# Upsert summaries
for p, buckets in acc.items():
for start, total in buckets.items():
s = db.query(Summary).filter_by(user_id=user_id, period=p, period_start=start).one_or_none()
if not s:
_, end = period_bounds(start, p)
s = Summary(user_id=user_id, period=p, period_start=start, period_end=end, kg_co2e=0.0)
db.add(s)
s.kg_co2e = round(total, 6)
db.commit()
finally:
db.close()