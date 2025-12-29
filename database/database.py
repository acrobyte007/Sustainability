import os
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs
from sqlalchemy import create_engine, Column, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from datetime import datetime
from contextlib import contextmanager

CURRENT = Path(__file__).resolve()
PROJECT_ROOT = CURRENT.parents[1]
load_dotenv(PROJECT_ROOT / ".env")

url = os.getenv("CONNECTION_STRING")
result = urlparse(url)
query_params = parse_qs(result.query)
sslmode = query_params.get("sslmode", ["require"])[0]

DB_URL = f"postgresql+psycopg2://{result.username}:{result.password}@{result.hostname}:{result.port or 5432}/{result.path[1:]}?sslmode={sslmode}"

Base = declarative_base()

class Organization(Base):
    __tablename__ = "organization"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    country = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    esg_metrics = relationship("ESGMetric", back_populates="organization", cascade="all, delete-orphan")


class ESGMetric(Base):
    __tablename__ = "esg_metric"

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organization.id", ondelete="CASCADE"))

    category = Column(String(50))
    indicator_name = Column(String(255))
    value = Column(Numeric)
    unit = Column(String(50))

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organization = relationship("Organization", back_populates="esg_metrics")


engine = create_engine(DB_URL, echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

@contextmanager
def get_session():
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


