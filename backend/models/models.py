from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Relație cu generările
    generations = relationship("Generation", back_populates="owner")

    # Analytics relationships
    generation_events = relationship("GenerationEvent", back_populates="user")
    sessions = relationship("UserSession", back_populates="user")

    # Social/sharing relationships
    shared_generations = relationship("SharedGeneration", back_populates="user")
    shared_presets = relationship("SharedPreset", back_populates="user")
    generation_votes = relationship("GenerationVote", back_populates="user")
    preset_votes = relationship("PresetVote", back_populates="user")

    # Multi-track projects
    projects = relationship("Project", back_populates="user")

class Generation(Base):
    __tablename__ = "generations"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String)
    file_path = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Legătura cu User (Foreign Key)
    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="generations")