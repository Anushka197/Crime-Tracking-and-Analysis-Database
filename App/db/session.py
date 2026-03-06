from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy.engine import URL

engine = create_engine(
    URL.create(
        drivername="postgresql",
        username="postgres",
        password="Ma314DBS@",
        host="localhost",
        port=5432,
        database="Demo"          # ← actual database name
    ),
    connect_args={"options": "-csearch_path=crimetrack"}  # ← set schema
)
Session = sessionmaker(bind=engine)
session = Session()


Base = declarative_base()
