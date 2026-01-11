from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from pydantic import BaseModel
import mido
import os
from pathlib import Path
import logging

from routers.auth import get_db, get_current_user_email
from models import models
from services.arrangement_service import ArrangementService

# Config
router = APIRouter(prefix="/api/generate/arrangement", tags=["arrangement"])
logger = logging.getLogger(__name__)
STORAGE_DIR = Path(os.getenv("STORAGE_DIR", "storage/midi_files"))

# Models
class ArrangementBlock(BaseModel):
    type: str # intro, verse, chorus, bridge, outro
    bars: int = 4
    intensity: str = "medium"

class ArrangementRequest(BaseModel):
    name: str = "My Song"
    style: str = "techno"
    instrument: str = "full_kit"
    bpm: int = 120
    key: str = "C"
    scale: str = "minor"
    blocks: List[ArrangementBlock]

@router.post("/")
async def generate_arrangement(
    request: ArrangementRequest,
    current_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    """
    Generate a full arrangement by stitching multiple blocks.
    """
    user = db.query(models.User).filter(models.User.email == current_email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    try:
        # Use Service
        service = ArrangementService()
        
        # Convert Pydantic blocks to dicts
        structure = [b.dict() for b in request.blocks]
        
        final_mid = service.generate_arrangement(
            structure=structure,
            style=request.style,
            key=request.key,
            scale=request.scale,
            bpm=request.bpm,
            instrument=request.instrument
        )

        # Save
        filename = f"amc_Arrangement_{user.id}_{request.name.replace(' ', '_')}.mid"
        file_path = STORAGE_DIR / filename
        final_mid.save(file_path)
        
        # Record
        new_gen = models.Generation(
            description=f"[ARRANGEMENT] {request.name} ({len(request.blocks)} blocks) - {request.key} {request.scale}",
            file_path=str(file_path),
            user_id=user.id
        )
        db.add(new_gen)
        db.commit()
        
        return {
            "url": f"/midi_files/{filename}",
            "filename": filename,
            "status": "success",
            "blocks_processed": len(request.blocks)
        }

    except Exception as e:
        logger.error(f"Arrangement Service Failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
