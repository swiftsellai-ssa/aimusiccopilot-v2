from fastapi import APIRouter, UploadFile, File, HTTPException
from services.midi_analyzer import MidiAnalyzer
import logging

router = APIRouter(prefix="/api/analyze", tags=["analysis"])
logger = logging.getLogger(__name__)

@router.post("/midi")
async def analyze_midi(file: UploadFile = File(...)):
    """
    Analyze an uploaded MIDI file to extract BPM and Harmonic Context.
    """
    if not file.filename.endswith('.mid') and not file.filename.endswith('.midi'):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a .mid file.")
    
    try:
        content = await file.read()
        analyzer = MidiAnalyzer()
        result = analyzer.analyze_structure(content)
        
        return result
        
    except Exception as e:
        logger.error(f"Analysis Failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
