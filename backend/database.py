from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Folosim SQLite pentru simplitate și viteză acum.
# Va crea un fișier 'aimusiccopilot.db' în folderul backend.
SQLALCHEMY_DATABASE_URL = "sqlite:///./aimusiccopilot.db"

# connect_args este necesar doar pentru SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Funcție helper pentru a obține o sesiune DB în endpoint-uri
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()