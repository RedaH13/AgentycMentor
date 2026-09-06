import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Example Format: "mssql+pyodbc://username:password@server/dbname?driver=ODBC+Driver+17+for+SQL+Server"
SQLALCHEMY_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mssql+pyodbc://@DESKTOP-CK7HVDE/MAS_Pedagogic?driver=ODBC+Driver+17+for+SQL+Server;Trusted_Connection=yes"
)


engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
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