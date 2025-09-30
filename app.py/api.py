import os
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import flask_cors
from models import init_db, SessionLocal, EmissionFactor, Entry, Summary, ensure_demo_user
from auth import require_user
from sqs_client import publish_recalc

APP_DIR os.path.dirname(_file_)

app = Flask(_name_, static_folder="web/static", template_folder="web")
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

if __name__ == "__main__":
    ensure_demo_user()
    app.run(host="0.0.0.0", port=8000)


