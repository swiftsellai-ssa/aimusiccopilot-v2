import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Preluăm URL-ul din Render. Dacă nu există, folosim sqlite local.
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

# FIX CRITIC: Render dă URL cu 'postgres://' dar SQLAlchemy vrea 'postgresql://'
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Configurare Engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    # Configurare pentru Postgres (fără check_same_thread)
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Funcție helper pentru a obține o sesiune DB în endpoint-uri
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()