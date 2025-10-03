#!/usr/bin/env python3
from models import SessionLocal, EmissionFactor, init_db


seed = [
{"category": "electricity", "unit": "kWh", "kg_co2e_per_unit": 0.10, "source": "Example NZ avg"},
{"category": "petrol", "unit": "L", "kg_co2e_per_unit": 2.31, "source": "IPCC/DEFRA approx"},
{"category": "diesel", "unit": "L", "kg_co2e_per_unit": 2.68, "source": "IPCC/DEFRA approx"},
{"category": "beef", "unit": "serving", "kg_co2e_per_unit": 5.0, "source": "Literature avg"},
{"category": "chicken", "unit": "serving", "kg_co2e_per_unit": 1.5, "source": "Literature avg"},
{"category": "flight_shorthaul", "unit": "km", "kg_co2e_per_unit": 0.15, "source": "Rough calc"},
]


if __name__ == "__main__":
    init_db()
    db = SessionLocal()
try:
    for row in seed:
        exists = db.query(EmissionFactor).filter_by(category=row["category"], unit=row["unit"]).one_or_none()
    if not exists:
        db.add(EmissionFactor(**row))
        db.commit()
    print("Seeded emission factors.")
finally:
    db.close()