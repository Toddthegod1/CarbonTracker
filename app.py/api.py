import os
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from models import init_db, SessionLocal, EmissionFactor, Entry, Summary, ensure_demo_user
from auth import require_user
from sqs_client import publish_recalc


APP_DIR = os.path.dirname(__file__)


app = Flask(__name__, static_folder="web/static", template_folder="web")
CORS(app, supports_credentials=True)


init_db()


@app.route("/")
def index():
return send_from_directory(os.path.join(APP_DIR, "web"), "index.html")


@app.get("/api/health")
def health():
return {"ok": True, "time": datetime.utcnow().isoformat()}


@app.get("/api/factors")
@require_user
def factors(user):
db = SessionLocal()
try:
rows = db.query(EmissionFactor).all()
return jsonify([{
"category": r.category,
"unit": r.unit,
"kg_co2e_per_unit": r.kg_co2e_per_unit,
"source": r.source
} for r in rows])
finally:
db.close()


@app.post("/api/entries")
@require_user
def add_entry(user):
data = request.get_json(force=True)
db = SessionLocal()
try:
e = Entry(
user_id=user["id"],
category=data["category"],
quantity=float(data["quantity"]),
unit=data["unit"],
occurred_at=datetime.fromisoformat(data.get("occurred_at")) if data.get("occurred_at") else datetime.utcnow(),
)
db.add(e)
db.commit()
app.run(host="0.0.0.0", port=8000)


