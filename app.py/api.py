# app/api.py
import os
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from auth import require_user
from sqs_client import publish_recalc
from storage_svc import append_entry, list_entries, read_summaries

APP_DIR = os.path.dirname(__file__)
app = Flask(__name__, static_folder="web/static", template_folder="web")
CORS(app, supports_credentials=True)

@app.route("/")
def index():
    return send_from_directory(os.path.join(APP_DIR, "web"), "index.html")

@app.get("/api/health")
def health():
    return {"ok": True}

@app.get("/api/factors")
@require_user
def factors(user):
    rows = [
        {"category":"electricity","unit":"kWh","kg_co2e_per_unit":0.10,"source":"Example"},
        {"category":"petrol","unit":"L","kg_co2e_per_unit":2.31,"source":"Approx"},
        {"category":"diesel","unit":"L","kg_co2e_per_unit":2.68,"source":"Approx"},
        {"category":"beef","unit":"serving","kg_co2e_per_unit":5.0,"source":"Avg"},
        {"category":"chicken","unit":"serving","kg_co2e_per_unit":1.5,"source":"Avg"},
        {"category":"flight_shorthaul","unit":"km","kg_co2e_per_unit":0.15,"source":"Rough"},
    ]
    return jsonify(rows)

@app.post("/api/entries")
@require_user
def add_entry(user):
    data = request.get_json(force=True)
    entry = {
        "id": int(datetime.utcnow().timestamp() * 1e6),
        "user_id": user["id"],
        "category": data["category"],
        "quantity": float(data["quantity"]),
        "unit": data["unit"],
        "occurred_at": data.get("occurred_at") or datetime.utcnow().isoformat()
    }
    append_entry(user["id"], entry)
    publish_recalc(user["id"])
    return {"ok": True, "entry_id": entry["id"]}

@app.get("/api/entries")
@require_user
def get_entries(user):
    return jsonify(list_entries(user["id"], limit=100))

@app.get("/api/summaries")
@require_user
def get_summaries(user):
    period = request.args.get("period", "weekly")
    return jsonify(read_summaries(user["id"], period))


