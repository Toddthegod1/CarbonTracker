import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Index
from sqlalchemy.orm import declarative_base, sessionmaker


DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int(os.environ.get("DB_PORT", "5432"))
DB_NAME = os.environ.get("DB_NAME", "carbon")
DB_USER = os.environ.get("DB_USER", "carbon_user")
DB_PASS = os.environ.get("DB_PASS", "carbon_pass")
DATABASE_URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"


engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


class EmissionFactor(Base):
__tablename__ = "emission_factors"
id = Column(Integer, primary_key=True)
category = Column(String, nullable=False)
unit = Column(String, nullable=False)
kg_co2e_per_unit = Column(Float, nullable=False)
source = Column(String)
updated_at = Column(DateTime, default=datetime.utcnow)
__table_args__ = (Index("ix_factors_cat_unit", "category", "unit", unique=True),)


class Entry(Base):
__tablename__ = "entries"
id = Column(Integer, primary_key=True)
user_id = Column(Integer, index=True, nullable=False)
category = Column(String, nullable=False)
quantity = Column(Float, nullable=False)
unit = Column(String, nullable=False)
occurred_at = Column(DateTime, nullable=False, default=datetime.utcnow)
created_at = Column(DateTime, default=datetime.utcnow)


class Summary(Base):
__tablename__ = "summaries"
id = Column(Integer, primary_key=True)
user_id = Column(Integer, index=True, nullable=False)
period = Column(String, nullable=False) # daily|weekly|monthly
period_start = Column(DateTime, nullable=False)
period_end = Column(DateTime, nullable=False)
kg_co2e = Column(Float, nullable=False, default=0.0)
updated_at = Column(DateTime, default=datetime.utcnow)
__table_args__ = (Index("ix_summary_u_p_s", "user_id", "period", "period_start", unique=True),)


# --- helpers ---


def init_db():
Base.metadata.create_all(bind=engine)




def ensure_demo_user():
# Nothing to do in DB (no user table). Entries are keyed by user_id only.
return True




def period_bounds(dt: datetime, period: str):
if period == "daily":
start = datetime(dt.year, dt.month, dt.day)
end = start + timedelta(days=1)
elif period == "weekly":
# ISO week start (Monday)
start = datetime(dt.year, dt.month, dt.day) - timedelta(days=dt.weekday())
end = start + timedelta(days=7)
elif period == "monthly":
start = datetime(dt.year, dt.month, 1)
if dt.month == 12:
end = datetime(dt.year + 1, 1, 1)
else:
end = datetime(dt.year, dt.month + 1, 1)
else:
raise ValueError("bad period")
return start, end