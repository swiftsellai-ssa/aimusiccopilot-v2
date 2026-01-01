# backend/models/social.py
"""
Database models for social/sharing features
- Shared Generations (public MIDI files with upvotes)
- Shared Presets (community preset marketplace)
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
import datetime as dt
from database import Base


class SharedGeneration(Base):
    """
    Publicly shared MIDI generation
    Users can share their best patterns with the community
    """
    __tablename__ = "shared_generations"

    id = Column(Integer, primary_key=True, index=True)
    share_id = Column(String, unique=True, index=True)  # Unique shareable link ID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Generation metadata
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    mode = Column(String, nullable=False)  # 'simple' or 'advanced'
    type = Column(String, nullable=False)  # 'drums', 'bass', 'melody', 'full'
    style = Column(String, nullable=False)
    bpm = Column(Integer, nullable=False)
    key = Column(String, nullable=False)
    scale = Column(String, nullable=False)

    # DNA parameters (if advanced mode)
    density = Column(Float, nullable=True)
    complexity = Column(Float, nullable=True)
    groove = Column(Float, nullable=True)
    evolution = Column(Float, nullable=True)
    bars = Column(Integer, nullable=True)

    # File info
    midi_url = Column(String, nullable=False)  # Path to MIDI file

    # Engagement metrics
    view_count = Column(Integer, default=0)
    play_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="shared_generations")
    votes = relationship("GenerationVote", back_populates="generation", cascade="all, delete-orphan")

    @property
    def score(self):
        """Calculate score for trending sorting"""
        return self.upvotes - self.downvotes

    @property
    def engagement_score(self):
        """Calculate total engagement for ranking"""
        return self.view_count + (self.play_count * 2) + (self.download_count * 3) + (self.upvotes * 5)


class GenerationVote(Base):
    """
    Track upvotes/downvotes on shared generations
    One vote per user per generation
    """
    __tablename__ = "generation_votes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    generation_id = Column(Integer, ForeignKey("shared_generations.id"), nullable=False)
    vote_type = Column(String, nullable=False)  # 'upvote' or 'downvote'
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="generation_votes")
    generation = relationship("SharedGeneration", back_populates="votes")


class SharedPreset(Base):
    """
    Community-shared custom presets
    Users share their favorite parameter combinations
    """
    __tablename__ = "shared_presets"

    id = Column(Integer, primary_key=True, index=True)
    share_id = Column(String, unique=True, index=True)  # Unique shareable link ID
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Preset metadata
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    mode = Column(String, nullable=False)  # 'simple' or 'advanced'
    type = Column(String, nullable=False)  # 'drums', 'bass', 'melody', 'full'
    style = Column(String, nullable=False)
    bpm = Column(Integer, nullable=False)
    key = Column(String, nullable=False)
    scale = Column(String, nullable=False)

    # DNA parameters
    density = Column(Float, nullable=False)
    complexity = Column(Float, nullable=False)
    groove = Column(Float, nullable=False)
    evolution = Column(Float, nullable=False)
    bars = Column(Integer, nullable=False)

    # Tags for categorization
    tags = Column(String, nullable=True)  # Comma-separated tags
    genre = Column(String, nullable=True)  # Primary genre

    # Engagement metrics
    view_count = Column(Integer, default=0)
    use_count = Column(Integer, default=0)  # How many times it's been loaded
    upvotes = Column(Integer, default=0)
    downvotes = Column(Integer, default=0)

    # Visibility
    is_public = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="shared_presets")
    votes = relationship("PresetVote", back_populates="preset", cascade="all, delete-orphan")

    @property
    def score(self):
        """Calculate score for trending sorting"""
        return self.upvotes - self.downvotes

    @property
    def trending_score(self):
        """Calculate trending score based on recent activity"""
        # Weight recent usage more heavily
        days_old = (dt.datetime.utcnow() - self.created_at).days + 1
        return (self.use_count + self.upvotes * 5) / days_old


class PresetVote(Base):
    """
    Track upvotes/downvotes on shared presets
    One vote per user per preset
    """
    __tablename__ = "preset_votes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    preset_id = Column(Integer, ForeignKey("shared_presets.id"), nullable=False)
    vote_type = Column(String, nullable=False)  # 'upvote' or 'downvote'
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="preset_votes")
    preset = relationship("SharedPreset", back_populates="votes")
