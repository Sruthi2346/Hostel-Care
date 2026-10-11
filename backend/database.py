import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker, DeclarativeBase

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is missing in environment variables.")

# Remove the URL option that PyMySQL does not recognize.
url = make_url(DATABASE_URL)
query = dict(url.query)
query.pop("ssl-mode", None)
query.pop("ssl_mode", None)
url = url.set(query=query)

# Aiven CA certificate stored beside this file.
CA_CERT_PATH = Path(__file__).resolve().parent / "ca.pem"

if not CA_CERT_PATH.is_file():
    raise RuntimeError(f"Aiven CA certificate not found: {CA_CERT_PATH}")

engine = create_engine(
    url,
    pool_pre_ping=True,
    connect_args={
        "ssl": {
            "ca": str(CA_CERT_PATH)
        }
    },
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()