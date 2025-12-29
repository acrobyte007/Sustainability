import os
from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse, parse_qs
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, relationship, declarative_base
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, func
from contextlib import asynccontextmanager

CURRENT = Path(__file__).resolve()
PROJECT_ROOT = CURRENT.parents[1]
load_dotenv(PROJECT_ROOT / ".env")

url = os.getenv("CONNECTION_STRING")
result = urlparse(url)
query_params = parse_qs(result.query)
sslmode = query_params.get("sslmode", ["require"])[0]

ASYNC_DB_URL = f"postgresql+asyncpg://{result.username}:{result.password}@{result.hostname}:{result.port or 5432}/{result.path[1:]}?sslmode={sslmode}"

Base = declarative_base()

class Organization(Base):
    __tablename__ = "organization"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    country = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    esg_metrics = relationship("ESGMetric", back_populates="organization", cascade="all, delete-orphan")


class ESGMetric(Base):
    __tablename__ = "esg_metric"

    id = Column(Integer, primary_key=True, autoincrement=True)
    organization_id = Column(Integer, ForeignKey("organization.id", ondelete="CASCADE"))
    category = Column(String(50))
    indicator_name = Column(String(255))
    value = Column(Numeric)
    unit = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    organization = relationship("Organization", back_populates="esg_metrics")


engine = create_async_engine(
    ASYNC_DB_URL,
    echo=False,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)

@asynccontextmanager
async def get_async_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def insert_esg_metrics_async(organization_id, esg_data):
    async with get_async_session() as session:
        metrics = []
        for category, indicators in esg_data.items():
            for name, data in indicators.items():
                metrics.append(ESGMetric(
                    organization_id=organization_id,
                    category=category,
                    indicator_name=name,
                    value=data.get("value"),
                    unit=data.get("unit")
                ))
        session.add_all(metrics)
        await session.flush()

async def onboard_organization(name: str, country: str | None = None):
    async with get_async_session() as session:
        org = Organization(
            name=name,
            country=country
        )

        session.add(org)
        await session.flush() 

        return org.id
