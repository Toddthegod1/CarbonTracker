# Carbon Output Tracker (COSC349 A2)


A tiny cloud app to log resource usage and view CO₂e summaries.


## Quick Start (local dev)
1. Create Postgres and export environment vars (see `.env.example`).
2. `python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`
3. `python scripts/seed_factors.py`
4. `python app/api.py` → open http://localhost:8000


## Cloud (AWS)
- 2× EC2 (App + Worker), 1× RDS (Postgres), 1× SQS queue.
- Attach instance profiles allowing SQS access.
- Use `deploy/*.service` and `deploy/nginx.conf`.


## Tests
`pytest -q`