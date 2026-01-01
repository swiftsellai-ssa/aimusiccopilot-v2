# backend/models/analytics.py
"""
Analytics tracking models for AI Music Copilot
Tracks user behavior, preferences, and usage patterns
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class GenerationEvent(Base):
    """Track each MIDI generation event"""
    __tablename__ = "generation_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Generation details
    mode = Column(String, nullable=False)  # 'simple' or 'advanced'
    generation_type = Column(String, nullable=False)  # 'drums', 'bass', 'melody', 'full'
    style = Column(String, nullable=False)  # 'techno', 'house', etc.
    bpm = Column(Integer, nullable=False)
    musical_key = Column(String, nullable=True)
    musical_scale = Column(String, nullable=True)

    # DNA parameters (null for simple mode)
    density = Column(Float, nullable=True)
    complexity = Column(Float, nullable=True)
    groove = Column(Float, nullable=True)
    evolution = Column(Float, nullable=True)
    bars = Column(Integer, nullable=True)

    # Outcome tracking
    success = Column(Boolean, default=True)
    error_message = Column(String, nullable=True)
    generation_time_ms = Column(Integer, nullable=True)  # Time to generate

    # User interaction
    was_downloaded = Column(Boolean, default=False)
    was_played = Column(Boolean, default=False)
    play_duration_seconds = Column(Float, nullable=True)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

    # Relationships
    user = relationship("User", back_populates="generation_events")


class UserSession(Base):
    """Track user sessions for engagement metrics"""
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    session_start = Column(DateTime, default=datetime.utcnow)
    session_end = Column(DateTime, nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    # Session activity
    generations_count = Column(Integer, default=0)
    downloads_count = Column(Integer, default=0)
    plays_count = Column(Integer, default=0)

    # Metadata
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

    # Relationships
    user = relationship("User", back_populates="sessions")


class AnalyticsSummary(Base):
    """Aggregated analytics for dashboard (updated periodically)"""
    __tablename__ = "analytics_summary"

    id = Column(Integer, primary_key=True, index=True)

    # Time period
    period_type = Column(String, nullable=False)  # 'daily', 'weekly', 'monthly'
    period_date = Column(DateTime, nullable=False)

    # Generation stats
    total_generations = Column(Integer, default=0)
    successful_generations = Column(Integer, default=0)
    failed_generations = Column(Integer, default=0)

    # Mode breakdown
    simple_mode_count = Column(Integer, default=0)
    advanced_mode_count = Column(Integer, default=0)

    # Type breakdown
    drums_count = Column(Integer, default=0)
    bass_count = Column(Integer, default=0)
    melody_count = Column(Integer, default=0)
    full_track_count = Column(Integer, default=0)

    # Style preferences
    techno_count = Column(Integer, default=0)
    house_count = Column(Integer, default=0)
    trap_count = Column(Integer, default=0)
    dnb_count = Column(Integer, default=0)
    lofi_count = Column(Integer, default=0)

    # BPM statistics
    avg_bpm = Column(Float, nullable=True)
    min_bpm = Column(Integer, nullable=True)
    max_bpm = Column(Integer, nullable=True)

    # Musical key preferences
    most_popular_key = Column(String, nullable=True)
    most_popular_scale = Column(String, nullable=True)

    # DNA parameters (averages for advanced mode)
    avg_density = Column(Float, nullable=True)
    avg_complexity = Column(Float, nullable=True)
    avg_groove = Column(Float, nullable=True)
    avg_evolution = Column(Float, nullable=True)
    avg_bars = Column(Float, nullable=True)

    # User engagement
    total_downloads = Column(Integer, default=0)
    total_plays = Column(Integer, default=0)
    download_rate = Column(Float, nullable=True)  # downloads / generations
    play_rate = Column(Float, nullable=True)  # plays / generations
    avg_play_duration = Column(Float, nullable=True)

    # Performance metrics
    avg_generation_time_ms = Column(Float, nullable=True)

    # User metrics
    active_users = Column(Integer, default=0)
    new_users = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
