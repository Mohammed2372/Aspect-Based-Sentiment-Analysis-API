import uuid
from datetime import datetime

from . import Column, String, Integer, ForeignKey, DateTime, Text, Float, relationship
from app.db.base import Base


class AnalysisSession(Base):
    __tablename__ = "analysis_sessions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    user_id = Column(Integer, ForeignKey("users.id"))
    session_type = Column(String)
    status = Column(String, default="Pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    total_items = Column(Integer, default=0)

    # optional fields
    csv_file_path = Column(String, nullable=True)
    raw_text = Column(Text, nullable=True)

    # relationships
    user = relationship("app.models.user.User", back_populates="sessions")
    records = relationship("AnalysisRecord", back_populates="session")


class AnalysisRecord(Base):
    __tablename__ = "analysis_records"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))

    session_id = Column(String, ForeignKey("analysis_sessions.id"))
    original_text = Column(Text)

    # relationships
    session = relationship("AnalysisSession", back_populates="records")
    results = relationship("AspectResult", back_populates="record")


class AspectResult(Base):
    __tablename__ = "aspect_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    record_id = Column(String, ForeignKey("analysis_records.id"))
    aspect = Column(String)
    sentiment = Column(String)
    confidence = Column(Float)

    # relationships
    record = relationship("AnalysisRecord", back_populates="results")
