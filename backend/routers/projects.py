# backend/routers/projects.py
"""
Project Management API
Multi-track project CRUD operations and export
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime as dt
import logging

from database import get_db
from models.models import User
from models.projects import Project, Track, TrackVersion
from services.midi_merger import MidiMerger
from services.variation_engine import VariationEngine, DNAParameters
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from utils.security import SECRET_KEY, ALGORITHM

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects", tags=["projects"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# ==================== Authentication ====================

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Get current authenticated user from JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


# ==================== Pydantic Schemas ====================

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    bpm: int = 120
    key: str = 'C'
    scale: str = 'minor'
    total_bars: int = 8

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    bpm: Optional[int] = None
    key: Optional[str] = None
    scale: Optional[str] = None
    total_bars: Optional[int] = None
    is_public: Optional[bool] = None

class TrackCreate(BaseModel):
    name: str
    type: str  # 'drums', 'bass', 'melody', 'chords', 'fx'
    midi_url: str
    mode: str = 'advanced'
    style: str = 'techno'
    density: float = 0.5
    complexity: float = 0.5
    groove: float = 0.5
    evolution: float = 0.3
    bars: int = 4
    volume: float = 0.8
    pan: float = 0.5
    muted: bool = False
    solo: bool = False

class TrackUpdate(BaseModel):
    name: Optional[str] = None
    volume: Optional[float] = None
    pan: Optional[float] = None
    muted: Optional[bool] = None
    solo: Optional[bool] = None
    order: Optional[int] = None

class VariationCreate(BaseModel):
    name: Optional[str] = None
    strategy: str = 'moderate'  # 'subtle', 'moderate', or 'extreme'
    preserve_feel: bool = True

class TrackResponse(BaseModel):
    id: int
    project_id: int
    name: str
    type: str
    midi_url: str
    density: float
    complexity: float
    groove: float
    evolution: float
    bars: int
    volume: float
    pan: float
    muted: bool
    solo: bool
    order: int
    created_at: dt
    updated_at: dt

    class Config:
        from_attributes = True
        json_encoders = {
            dt: lambda v: v.isoformat()
        }

class ProjectResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    bpm: int
    key: str
    scale: str
    total_bars: int
    is_public: bool
    created_at: dt
    updated_at: dt
    tracks: List[TrackResponse] = []

    class Config:
        from_attributes = True
        json_encoders = {
            dt: lambda v: v.isoformat()
        }


# ==================== Project Endpoints ====================

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new multi-track project"""
    logger.info(f"User {current_user.email} creating project: {project_data.name}")

    project = Project(
        user_id=current_user.id,
        name=project_data.name,
        description=project_data.description,
        bpm=project_data.bpm,
        key=project_data.key,
        scale=project_data.scale,
        total_bars=project_data.total_bars
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    logger.info(f"Project created: {project.id}")
    return project


@router.get("", response_model=List[ProjectResponse])
def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """List all projects for current user"""
    projects = db.query(Project).filter(
        Project.user_id == current_user.id
    ).order_by(
        Project.updated_at.desc()
    ).offset(offset).limit(limit).all()

    return projects


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get project details with all tracks"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    project_data: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update project settings"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Update fields if provided
    update_data = project_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(project, field, value)

    db.commit()
    db.refresh(project)

    logger.info(f"Project {project_id} updated by {current_user.email}")
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a project and all its tracks"""
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(project)
    db.commit()

    logger.info(f"Project {project_id} deleted by {current_user.email}")
    return None


# ==================== Track Endpoints ====================

@router.post("/{project_id}/tracks", response_model=TrackResponse, status_code=status.HTTP_201_CREATED)
def add_track_to_project(
    project_id: int,
    track_data: TrackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a new track to a project"""
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get next order index
    max_order = db.query(Track).filter(Track.project_id == project_id).count()

    track = Track(
        project_id=project_id,
        name=track_data.name,
        type=track_data.type,
        midi_url=track_data.midi_url,
        mode=track_data.mode,
        style=track_data.style,
        density=track_data.density,
        complexity=track_data.complexity,
        groove=track_data.groove,
        evolution=track_data.evolution,
        bars=track_data.bars,
        volume=track_data.volume,
        pan=track_data.pan,
        muted=track_data.muted,
        solo=track_data.solo,
        order=max_order
    )

    db.add(track)
    db.commit()
    db.refresh(track)

    logger.info(f"Track {track.id} added to project {project_id}")
    return track


@router.put("/{project_id}/tracks/{track_id}", response_model=TrackResponse)
def update_track(
    project_id: int,
    track_id: int,
    track_data: TrackUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update track settings (mixer controls, name, etc.)"""
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get track
    track = db.query(Track).filter(
        Track.id == track_id,
        Track.project_id == project_id
    ).first()

    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    # Update fields
    update_data = track_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(track, field, value)

    db.commit()
    db.refresh(track)

    logger.info(f"Track {track_id} updated in project {project_id}")
    return track


@router.delete("/{project_id}/tracks/{track_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_track(
    project_id: int,
    track_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a track from a project"""
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get track
    track = db.query(Track).filter(
        Track.id == track_id,
        Track.project_id == project_id
    ).first()

    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    db.delete(track)
    db.commit()

    logger.info(f"Track {track_id} deleted from project {project_id}")
    return None


# ==================== Export Endpoint ====================

@router.get("/{project_id}/export")
def export_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export project as multi-track MIDI file"""
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get all tracks ordered
    tracks = db.query(Track).filter(
        Track.project_id == project_id
    ).order_by(Track.order).all()

    if not tracks:
        raise HTTPException(status_code=400, detail="Project has no tracks to export")

    # Prepare track files for merger
    track_files = []
    for track in tracks:
        # Build absolute path to MIDI file
        midi_path = Path("storage") / track.midi_url.lstrip("/storage/")

        if not midi_path.exists():
            logger.warning(f"MIDI file not found: {midi_path}")
            continue

        track_files.append({
            'path': str(midi_path),
            'name': track.name,
            'volume': track.volume,
            'pan': track.pan,
            'muted': track.muted
        })

    if not track_files:
        raise HTTPException(status_code=400, detail="No valid MIDI files found in project")

    # Generate output path
    output_filename = f"project_{project.id}_{project.name.replace(' ', '_')}.mid"
    output_path = Path("storage/exports") / output_filename

    # Merge tracks using MidiMerger
    try:
        merger = MidiMerger(bpm=project.bpm, time_signature=(4, 4))
        merged_file = merger.merge_tracks(track_files, str(output_path))

        logger.info(f"Project {project_id} exported to {merged_file}")

        return {
            "message": "Project exported successfully",
            "file_url": f"/storage/exports/{output_filename}",
            "track_count": len(track_files)
        }

    except Exception as e:
        logger.error(f"Error exporting project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


# ==================== Variation Endpoint ====================

@router.post("/{project_id}/tracks/{track_id}/variations", response_model=TrackResponse)
def create_track_variation(
    project_id: int,
    track_id: int,
    variation_data: VariationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate a variation of a track with DNA parameter mutations

    This creates a new TrackVersion with mutated DNA parameters.
    The actual MIDI generation will be triggered from the frontend.
    """
    # Verify project ownership
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get original track
    original_track = db.query(Track).filter(
        Track.id == track_id,
        Track.project_id == project_id
    ).first()

    if not original_track:
        raise HTTPException(status_code=404, detail="Track not found")

    # Use variation engine to generate mutated DNA parameters
    engine = VariationEngine()
    original_dna = DNAParameters(
        density=original_track.density,
        complexity=original_track.complexity,
        groove=original_track.groove,
        evolution=original_track.evolution,
        bars=original_track.bars
    )

    new_dna, deltas = engine.generate_variation(
        original_dna,
        strategy=variation_data.strategy,
        preserve_feel=variation_data.preserve_feel
    )

    logger.info(f"Generated variation with deltas: {deltas}")

    # Generate version name
    version_count = db.query(TrackVersion).filter(
        TrackVersion.track_id == track_id
    ).count()
    version_name = variation_data.name or f"Variation {version_count + 1}"

    # Create version record
    version = TrackVersion(
        track_id=track_id,
        name=version_name,
        density=new_dna.density,
        complexity=new_dna.complexity,
        groove=new_dna.groove,
        evolution=new_dna.evolution,
        bars=new_dna.bars,
        midi_url=""  # Will be updated after MIDI generation
    )

    db.add(version)
    db.commit()
    db.refresh(version)

    logger.info(f"Variation {version.id} created for track {track_id}")

    # Return the mutated parameters for frontend to generate MIDI
    return {
        "id": version.id,
        "project_id": project_id,
        "name": version_name,
        "type": original_track.type,
        "midi_url": "",  # Empty until generated
        "density": new_dna.density,
        "complexity": new_dna.complexity,
        "groove": new_dna.groove,
        "evolution": new_dna.evolution,
        "bars": new_dna.bars,
        "volume": original_track.volume,
        "pan": original_track.pan,
        "muted": original_track.muted,
        "solo": original_track.solo,
        "order": original_track.order,
        "created_at": version.created_at.isoformat(),
        "updated_at": version.updated_at.isoformat()
    }
