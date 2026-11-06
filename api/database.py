import os
import urllib.parse
from sqlalchemy.engine import URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Example Format: "mssql+pyodbc://username:password@server/dbname?driver=ODBC+Driver+17+for+SQL+Server"
connection_url = URL.create(
    "mssql+pyodbc",
    host="DESKTOP-CK7HVDE",
    database="MAS_Pedagogic",
    query={
        "driver": "ODBC Driver 17 for SQL Server",
        "Trusted_Connection": "yes"
    }
)

# 2. Pass the safely constructed URL object directly to the engine
engine = create_engine(
    connection_url,
    fast_executemany=True,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency to inject DB sessions into your routers
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()