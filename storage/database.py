# storage/database.py
# Handles database connection and session management.
# Uses SQLite for local development — easy to switch to
# PostgreSQL in production by changing the POSTGRES_URL in .env

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base
import os


# --- Use SQLite locally, PostgreSQL in production ---
DATABASE_URL = os.getenv('POSTGRES_URL', '')

if not DATABASE_URL or 'postgresql' not in DATABASE_URL:
    # Default to SQLite for local development
    DATABASE_URL = 'sqlite:///data/supply_chain.db'
    print(f"[database] Using SQLite: {DATABASE_URL}")
else:
    print(f"[database] Using PostgreSQL")

# --- Create engine ---
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if 'sqlite' in DATABASE_URL else {},
    echo=False,   # set True to see raw SQL queries
)

# --- Create session factory ---
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def init_db():
    """
    Creates all tables if they don't exist yet.
    Safe to call multiple times.
    """
    Base.metadata.create_all(bind=engine)
    print("[database] Tables created successfully")


def get_session():
    """
    Returns a new database session.
    Always close the session after use.
    """
    return SessionLocal()