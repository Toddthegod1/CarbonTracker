from models import SessionLocal, EmissionFactor, init_db


def test_factor_seed_present():
    init_db()
    db = SessionLocal()
try:
    row = db.query(EmissionFactor).filter_by(category='electricity', unit='kWh').one_or_none()
    assert row is None or row.kg_co2e_per_unit >= 0.05
finally:
    db.close()