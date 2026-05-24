# storage/models.py
# Defines the database table structure using SQLAlchemy ORM.
# Each article becomes one row in the 'disruption_events' table.

from sqlalchemy import (
    Column, String, Float, Integer,
    DateTime, Boolean, Text, JSON,
    create_engine
)
from sqlalchemy.orm import declarative_base
from datetime import datetime, timezone

Base = declarative_base()


class DisruptionEvent(Base):
    """
    Represents a single supply chain disruption event
    detected from a news article.
    """
    __tablename__ = 'disruption_events'

    # --- Identity ---
    id           = Column(Integer, primary_key=True, autoincrement=True)
    url          = Column(String(2048), unique=True, nullable=False)

    # --- Article content ---
    title        = Column(String(512),  nullable=False)
    title_clean  = Column(String(512),  nullable=True)
    body         = Column(Text,         nullable=True)
    body_clean   = Column(Text,         nullable=True)
    source       = Column(String(256),  nullable=True)
    published    = Column(String(128),  nullable=True)

    # --- Classification ---
    domain_hint  = Column(String(64),   nullable=True)
    domains      = Column(JSON,         nullable=True)   # list of matched domains
    domain_scores= Column(JSON,         nullable=True)   # dict of domain → score

    # --- Risk ---
    risk_score   = Column(Float,        nullable=True)
    risk_level   = Column(String(16),   nullable=True)   # critical/high/medium/low

    # --- Quality ---
    quality_score= Column(Float,        nullable=True)
    is_trusted   = Column(Boolean,      default=False)

    # --- Metadata ---
    created_at   = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return (
            f"<DisruptionEvent id={self.id} "
            f"risk={self.risk_level} "
            f"domains={self.domains} "
            f"title='{self.title[:50]}...'>"
        )