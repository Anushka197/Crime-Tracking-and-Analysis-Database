import os

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base, sessionmaker


database_url = os.getenv("DATABASE_URL")

if database_url:
    engine = create_engine(database_url, pool_pre_ping=True)
else:
    engine = create_engine(
        URL.create(
            drivername="postgresql",
            username=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", "Ma314DBS@"),
            host=os.getenv("DB_HOST", "localhost"),
            port=int(os.getenv("DB_PORT", "5432")),
            database=os.getenv("DB_NAME", "crimedb"),
        ),
        pool_pre_ping=True,
    )

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()
