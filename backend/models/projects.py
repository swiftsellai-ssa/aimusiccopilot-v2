# backend/models/projects.py
"""
Database models for multi-track projects
- Projects: Container for multiple tracks
- Tracks: Individual MIDI patterns within a project
- TrackVersions: Variations of tracks for A/B testing
"""

from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
import datetime as dt
from database import Base


class Project(Base):
    """
    Multi-track music project
    Contains multiple tracks (drums, bass, melody, etc.)
    """
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Project metadata
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)

    # Global settings (apply to all tracks)
    bpm = Column(Integer, nullable=False, default=120)
    key = Column(String, nullable=False, default='C')
    scale = Column(String, nullable=False, default='minor')
    total_bars = Column(Integer, nullable=False, default=8)

    # Project state
    is_public = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="projects")
    tracks = relationship("Track", back_populates="project", cascade="all, delete-orphan")

    @property
    def track_count(self):
        """Number of tracks in this project"""
        return len(self.tracks)


class Track(Base):
    """
    Individual track within a project
    Can be drums, bass, melody, etc.
    """
    __tablename__ = "tracks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)

    # Track metadata
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  # 'drums', 'bass', 'melody', 'chords', 'fx'
    order = Column(Integer, nullable=False, default=0)  # Display order in timeline

    # Generation parameters (DNA)
    mode = Column(String, nullable=False, default='advanced')
    style = Column(String, nullable=False)
    density = Column(Float, nullable=False, default=0.5)
    complexity = Column(Float, nullable=False, default=0.5)
    groove = Column(Float, nullable=False, default=0.5)
    evolution = Column(Float, nullable=False, default=0.3)
    bars = Column(Integer, nullable=False, default=4)

    # MIDI data
    midi_url = Column(String, nullable=False)  # Path to MIDI file

    # Mixer settings
    volume = Column(Float, nullable=False, default=0.8)  # 0.0 to 1.0
    pan = Column(Float, nullable=False, default=0.5)     # 0.0 (left) to 1.0 (right)
    muted = Column(Boolean, default=False)
    solo = Column(Boolean, default=False)

    # Active version (for A/B testing)
    active_version_id = Column(Integer, ForeignKey("track_versions.id"), nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=dt.datetime.utcnow)
    updated_at = Column(DateTime, default=dt.datetime.utcnow, onupdate=dt.datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="tracks")
    versions = relationship("TrackVersion", back_populates="track",
                          foreign_keys="TrackVersion.track_id",
                          cascade="all, delete-orphan")


class TrackVersion(Base):
    """
    Variation/version of a track for A/B testing
    Stores different DNA parameter combinations
    """
    __tablename__ = "track_versions"

    id = Column(Integer, primary_key=True, index=True)
    track_id = Column(Integer, ForeignKey("tracks.id"), nullable=False)

    # Version metadata
    name = Column(String, nullable=False)  # e.g., "Original", "Variation 1", "More Dense"
    is_original = Column(Boolean, default=False)

    # DNA parameters (can differ from parent track)
    density = Column(Float, nullable=False)
    complexity = Column(Float, nullable=False)
    groove = Column(Float, nullable=False)
    evolution = Column(Float, nullable=False)
    bars = Column(Integer, nullable=False)

    # MIDI data
    midi_url = Column(String, nullable=False)

    # User feedback
    rating = Column(Integer, nullable=True)  # 1-5 stars
    notes = Column(Text, nullable=True)      # User notes about this version

    # Timestamps
    created_at = Column(DateTime, default=dt.datetime.utcnow)

    # Relationships
    track = relationship("Track", back_populates="versions", foreign_keys=[track_id])

    @property
    def dna_diff(self):
        """Calculate DNA parameter differences from original track"""
        if not self.track:
            return {}

        return {
            'density': self.density - self.track.density,
            'complexity': self.complexity - self.track.complexity,
            'groove': self.groove - self.track.groove,
            'evolution': self.evolution - self.track.evolution,
            'bars': self.bars - self.track.bars
        }
