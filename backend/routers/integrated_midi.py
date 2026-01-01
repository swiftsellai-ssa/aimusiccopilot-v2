"""
Router for IntegratedMidiGenerator endpoints
Provides advanced MIDI generation with DNA-based patterns
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict
from sqlalchemy.orm import Session
import os
import datetime
from pathlib import Path
import logging

from services.integrated_midi_generator import IntegratedMidiGenerator
from routers.auth import get_db
from models import models
from utils.security import ALGORITHM, SECRET_KEY
from fastapi.security import OAuth2PasswordBearer
from jose import jwt

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Auth helper (copied from main.py for modularity)
def get_current_user_email(token: str = Depends(oauth2_scheme)):
    """Get current user email from JWT token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid auth")
        return email
    except:
        raise HTTPException(status_code=401, detail="Invalid auth")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/integrated-midi", tags=["Integrated MIDI"])

# Storage directory - MUST match main.py's STORAGE_DIR
STORAGE_DIR = Path("storage/midi_files")
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# Initialize generator (singleton pattern)
midi_generator = IntegratedMidiGenerator(enable_humanization=True)


# Request/Response Models
class IntegratedMidiRequest(BaseModel):
    """Request model for integrated MIDI generation"""
    description: str = Field(..., description="Text description of pattern", example="dark techno kick")
    style: Optional[str] = Field(None, description="Music style", example="techno")
    instrument: Optional[str] = Field(None, description="Instrument type", example="kick")
    bpm: int = Field(120, ge=40, le=300, description="Tempo in BPM")
    bars: int = Field(4, ge=1, le=32, description="Number of bars")

    # DNA parameters
    seed: Optional[int] = Field(None, description="Random seed for deterministic generation")
    use_dna: Optional[bool] = Field(None, description="Force DNA generation (None=auto)")
    humanize: Optional[bool] = Field(None, description="Apply humanization (None=default)")
    density: float = Field(0.7, ge=0.0, le=1.0, description="Note density")
    complexity: float = Field(0.5, ge=0.0, le=1.0, description="Pattern complexity")
    groove: float = Field(0.2, ge=0.0, le=1.0, description="Swing/groove amount")
    evolution: float = Field(0.3, ge=0.0, le=1.0, description="Pattern evolution")
    velocity_curve: str = Field("natural", description="Velocity pattern")

    # Musical parameters
    musical_key: str = Field("C", description="Musical key")
    musical_scale: str = Field("minor", description="Musical scale")

    class Config:
        json_schema_extra = {
            "example": {
                "description": "dark techno kick pattern",
                "style": "techno",
                "instrument": "kick",
                "bpm": 130,
                "bars": 4,
                "use_dna": True,
                "humanize": True,
                "density": 0.7,
                "complexity": 0.6,
                "groove": 0.2,
                "evolution": 0.3,
                "velocity_curve": "accent"
            }
        }


class MidiGenerateResponse(BaseModel):
    """Response model for MIDI generation"""
    success: bool
    generation_id: int
    file_path: str
    download_url: str
    message: str
    metadata: dict


# Endpoints
@router.post("/generate", response_model=MidiGenerateResponse)
async def generate_integrated_midi(
    request: IntegratedMidiRequest,
    current_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    """
    Generate MIDI pattern using the IntegratedMidiGenerator.

    This endpoint provides:
    - DNA-based pattern generation
    - Multiple style support (techno, trap, house, dnb, lofi)
    - Humanization engine
    - Proper MIDI channel assignment
    - Complete parameter control
    """
    try:
        # Get user
        user = db.query(models.User).filter(models.User.email == current_email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        logger.info(f"Generating MIDI for user {user.email}: {request.description}")

        # Generate MIDI using IntegratedMidiGenerator
        midi_file, used_seed = midi_generator.generate(
            description=request.description,
            style=request.style,
            instrument=request.instrument,
            bpm=request.bpm,
            bars=request.bars,
            use_dna=request.use_dna,
            humanize=request.humanize,
            seed=request.seed,
            density=request.density,
            complexity=request.complexity,
            groove=request.groove,
            evolution=request.evolution,
            velocity_curve=request.velocity_curve,
            musical_key=request.musical_key,
            musical_scale=request.musical_scale
        )

        # Generate filename
        timestamp = int(datetime.datetime.now().timestamp())
        safe_description = "".join(c for c in request.description if c.isalnum() or c in (' ', '-', '_'))
        safe_description = safe_description.replace(' ', '_')[:50]
        filename = f"{safe_description}_{request.instrument or 'pattern'}_{user.id}_{timestamp}.mid"
        file_path = STORAGE_DIR / filename

        # Save MIDI file
        midi_file.save(str(file_path))
        logger.info(f"Saved MIDI to {file_path}")

        # Create description with metadata
        full_description = (
            f"[{request.instrument.upper() if request.instrument else 'PATTERN'}] "
            f"{request.musical_key} {request.musical_scale} - "
            f"{request.description} "
            f"({request.bpm} BPM, {request.bars} bars)"
        )

        # Save to database
        new_generation = models.Generation(
            description=full_description,
            file_path=str(file_path),
            user_id=user.id
        )
        db.add(new_generation)
        db.commit()
        db.refresh(new_generation)

        logger.info(f"Created generation record ID: {new_generation.id}")

        # Return response with static file URL
        return MidiGenerateResponse(
            success=True,
            generation_id=new_generation.id,
            file_path=str(file_path),
            download_url=f"/storage/midi_files/{filename}",  # Changed to static file URL
            message="MIDI pattern generated successfully",
            metadata={
                "description": request.description,
                "style": request.style,
                "instrument": request.instrument,
                "bpm": request.bpm,
                "bars": request.bars,
                "key": request.musical_key,
                "scale": request.musical_scale,
                "tracks": len(midi_file.tracks),
                "used_dna": request.use_dna,
                "humanized": request.humanize,
                "seed": used_seed
            }
        )

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.error(f"MIDI generation failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate MIDI: {str(e)}")


@router.get("/download/{generation_id}")
async def download_integrated_midi(
    generation_id: int,
    current_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    """Download generated MIDI file"""
    try:
        # Get generation record
        generation = db.query(models.Generation).filter(
            models.Generation.id == generation_id
        ).first()

        if not generation:
            raise HTTPException(status_code=404, detail="Generation not found")

        # Check ownership
        user = db.query(models.User).filter(models.User.email == current_email).first()
        if generation.user_id != user.id:
            raise HTTPException(status_code=403, detail="Not authorized to download this file")

        # Check if file exists
        if not os.path.exists(generation.file_path):
            raise HTTPException(status_code=404, detail="File not found on server")

        # Return file
        return FileResponse(
            generation.file_path,
            media_type='audio/midi',
            filename=os.path.basename(generation.file_path)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to download file")


@router.get("/styles")
async def get_supported_styles():
    """Get list of supported music styles"""
    return {
        "styles": list(midi_generator.SUPPORTED_STYLES),
        "description": "Supported music styles for integrated MIDI generation"
    }


@router.get("/instruments")
async def get_supported_instruments():
    """Get list of supported instruments"""
    return {
        "drum_instruments": list(midi_generator.DRUM_INSTRUMENTS),
        "melodic_instruments": list(midi_generator.MELODIC_INSTRUMENTS),
        "description": "Supported instruments for integrated MIDI generation"
    }


@router.get("/presets")
async def get_presets():
    """Get common DNA presets for different use cases"""
    return {
        "presets": {
            "minimal": {
                "density": 0.3,
                "complexity": 0.2,
                "evolution": 0.1,
                "description": "Sparse, simple patterns"
            },
            "balanced": {
                "density": 0.6,
                "complexity": 0.5,
                "evolution": 0.3,
                "description": "Standard complexity patterns"
            },
            "complex": {
                "density": 0.9,
                "complexity": 0.8,
                "evolution": 0.5,
                "description": "Dense, evolving patterns"
            },
            "groovy": {
                "density": 0.7,
                "complexity": 0.5,
                "groove": 0.4,
                "velocity_curve": "accent",
                "description": "Swung, groovy patterns"
            }
        }
    }


@router.post("/quick-generate")
async def quick_generate(
    description: str,
    style: str = "techno",
    current_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    """
    Quick generate with minimal parameters.
    Uses smart defaults based on style.
    """
    # Map style to common parameters
    style_defaults = {
        "techno": {"bpm": 130, "instrument": "kick", "complexity": 0.6},
        "trap": {"bpm": 140, "instrument": "hat", "complexity": 0.8},
        "house": {"bpm": 125, "instrument": "drums", "complexity": 0.5},
        "dnb": {"bpm": 174, "instrument": "drums", "complexity": 0.7},
        "lofi": {"bpm": 85, "instrument": "drums", "complexity": 0.4},
        "modern_trap": {"bpm": 140, "instrument": "hat", "complexity": 0.8},
        "cinematic": {"bpm": 80, "instrument": "melody", "complexity": 0.3},
        "deep_house": {"bpm": 122, "instrument": "drums", "complexity": 0.6},
        "liquid_dnb": {"bpm": 174, "instrument": "drums", "complexity": 0.6}
    }

    defaults = style_defaults.get(style, style_defaults["techno"])

    request = IntegratedMidiRequest(
        description=description,
        style=style,
        bpm=defaults["bpm"],
        instrument=defaults["instrument"],
        complexity=defaults["complexity"]
    )

    return await generate_integrated_midi(request, current_email, db)
