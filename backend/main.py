from fastapi import FastAPI, HTTPException, Depends, Request, status, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Dict
import datetime
import os
from pathlib import Path
import logging
from sqlalchemy.orm import Session
from jose import jwt
import traceback
from database import engine
from models import models
from models import analytics  # Import analytics models
from models import social  # Import social/sharing models
from models import projects  # Import multi-track project models
from routers import auth
from routers import download
from routers.auth import get_db
from utils.security import ALGORITHM, SECRET_KEY

# Configurare Logging
logger = logging.getLogger("uvicorn.error")

# Creăm directorul pentru storage persistent
STORAGE_DIR = Path(os.getenv("STORAGE_DIR", "storage/midi_files"))
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

# Crearea tabelelor în baza de date (including analytics, social, and projects)
models.Base.metadata.create_all(bind=engine)
analytics.Base.metadata.create_all(bind=engine)  # Create analytics tables
social.Base.metadata.create_all(bind=engine)  # Create social/sharing tables
projects.Base.metadata.create_all(bind=engine)  # Create multi-track project tables

app = FastAPI()

# Global Exception Handlers
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions with user-friendly messages"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url)
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed information"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
            "path": str(request.url)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all uncaught exceptions"""
    # Log the full traceback for debugging
    error_traceback = traceback.format_exc()
    logger.error(f"❌ Unhandled Exception:\n{error_traceback}")

    # Return user-friendly error message
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An internal server error occurred. Please try again later.",
            "error_type": type(exc).__name__,
            "path": str(request.url)
        }
    )

# Configurare Environment Variables
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")

# Configurare CORS (Permitem Frontend-ului să vorbească cu noi)
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],  # Permite frontend-ului să citească headerul pentru download
)

# Includem rutele de autentificare
app.include_router(auth.router)
app.include_router(download.router)

# Include IntegratedMidiGenerator router
from routers import integrated_midi
app.include_router(integrated_midi.router)

# Include Analytics router
from routers import analytics
app.include_router(analytics.router)

# Include Social/Sharing router
from routers import social as social_router
app.include_router(social_router.router)

# Include Projects router (Multi-track projects)
from routers import projects as projects_router
app.include_router(projects_router.router)

# Mount static files to serve MIDI files
app.mount("/storage", StaticFiles(directory="storage"), name="storage")

# Importuri pentru generarea MIDI
from services.midi_generator import MidiGenerator
from services.ai_service import MusicIntelligence
from services.packager_service import ProjectPackager
from services.recommendation_engine import RecommendationEngine
from services.advanced_midi_generator import AdvancedPatternGenerator, PatternDNA
from services.humanization_engine import HumanizationEngine

# OAuth2 scheme pentru autentificare
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Pydantic model pentru recommendation context
class RecommendationContext(BaseModel):
    instrument: str
    style: str = "trap"
    key: str = "C"
    scale: str = "minor"
    bpm: int = 120

# Funcție helper pentru a afla userul curent din token
def get_current_user_email(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid auth")
        return email
    except:
        raise HTTPException(status_code=401, detail="Invalid auth")

@app.post("/api/generate/midi")
async def generate_midi(
    description: str,
    instrument: str = "full_drums",  # Instrument mode: 'full_drums', 'kick', 'bass', 'melody'
    musical_key: str = "C",          # Musical key: 'C', 'D', 'F#', 'Bb', etc.
    musical_scale: str = "minor",    # Scale type: 'minor', 'major', 'dorian', 'phrygian'
    current_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    """Endpoint pentru generarea MIDI modulară cu control complet asupra tonalității"""

    # 1. Găsim userul în DB pe baza emailului din token
    user = db.query(models.User).filter(models.User.email == current_email).first()

    # 2. AI-ul analizează cererea ("The Architect")
    brain = MusicIntelligence()
    ai_params = brain.analyze_request(description)

    # 3. Algoritmul generează notele ("The Builder") - cu key și scale dinamice
    generator = MidiGenerator()
    midi = generator.generate_track(
        description,
        musical_key=musical_key,
        musical_scale=musical_scale,
        instrument_mode=instrument,
    )

    # 4. Salvăm fișierul fizic în storage persistent cu informații complete
    filename = f"{instrument}_{musical_key}_{musical_scale}_{user.id}_{int(datetime.datetime.now().timestamp())}.mid"
    file_path = STORAGE_DIR / filename

    midi.save(file_path)

    # 5. Salvăm în DB cu tag-uri complete
    new_generation = models.Generation(
        description=f"[{instrument.upper()}] {musical_key} {musical_scale.title()} - {description}",
        file_path=str(file_path),
        user_id=user.id
    )
    db.add(new_generation)
    db.commit()

    # Return JSON with file URL instead of FileResponse
    return {
        "file_url": f"/storage/midi_files/{filename}",
        "filename": filename,
        "message": "MIDI file generated successfully"
    }

@app.post("/api/generate/advanced")
async def generate_advanced(
    description: str,
    dna_params: Dict = Body(None)  # Allow manual DNA control
):
    dna_params = dna_params or {}
    # Parse description to DNA
    dna = PatternDNA(
        density=dna_params.get('density', 0.7),
        complexity=dna_params.get('complexity', 0.5),
        groove=dna_params.get('groove', 0.2),
        velocity_curve='natural',
        evolution=dna_params.get('evolution', 0.3)
    )
    
    # Generate with DNA
    generator = AdvancedPatternGenerator()
    pattern = generator.generate_pattern_with_dna(
        style='techno',
        instrument='drums',
        dna=dna
    )
    
    # Humanize
    humanizer = HumanizationEngine()
    pattern = humanizer.humanize_midi(pattern)
    
    return pattern

# Endpoint pentru istoricul generărilor utilizatorului
@app.get("/api/history")
def get_history(
    current_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    """Returnează ultimele 10 generări ale utilizatorului curent"""
    user = db.query(models.User).filter(models.User.email == current_email).first()
    # Returnăm ultimele 10 generări, cele mai noi primele
    return db.query(models.Generation)\
             .filter(models.Generation.user_id == user.id)\
             .order_by(models.Generation.created_at.desc())\
             .limit(10)\
             .all()

# Endpoint pentru generarea variațiilor
@app.post("/api/variations/{generation_id}")
async def generate_variations(
    generation_id: int,
    current_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    """
    Generează 3 variații ale unui beat existent.
    Returnează lista cu ID-urile și descrierile noilor generări.
    """
    # 1. Găsim generarea originală
    original = db.query(models.Generation).filter(models.Generation.id == generation_id).first()
    if not original:
        raise HTTPException(status_code=404, detail="Generation not found")

    # Verificăm dacă aparține userului
    user = db.query(models.User).filter(models.User.email == current_email).first()
    if original.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not your beat")

    # 2. Reconstituim parametrii AI
    # Pentru MVP, regenerăm parametrii din descrierea originală
    brain = MusicIntelligence()
    ai_params = brain.analyze_request(original.description)

    # 3. Generăm variațiile
    generator = MidiGenerator()
    variations_data = generator.create_variations(ai_params)

    response_variations = []

    for midi_obj, suffix in variations_data:
        # Salvăm fișierul în storage persistent
        filename = f"beat_{user.id}_var_{suffix}_{datetime.datetime.now().timestamp()}.mid"
        file_path = STORAGE_DIR / filename

        midi_obj.save(file_path)

        # Salvăm în DB ca generare nouă
        new_desc = f"{original.description} ({suffix})"
        new_gen = models.Generation(
            description=new_desc,
            file_path=str(file_path),
            user_id=user.id
        )
        db.add(new_gen)
        db.commit()

        # Adăugăm la răspuns
        response_variations.append({
            "id": new_gen.id,
            "description": new_desc,
            "filename": filename
        })

    return {
        "original_id": generation_id,
        "variations": response_variations
    }

# Endpoint pentru descărcarea/redarea fișierelor MIDI
@app.get("/api/download/{generation_id}")
async def download_midi(
    generation_id: int,
    current_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    """
    Servește fișierul MIDI asociat unei generări.
    Verifică ownership înainte de a permite descărcarea.
    """
    # 1. Găsim înregistrarea
    gen = db.query(models.Generation).filter(models.Generation.id == generation_id).first()
    if not gen:
        raise HTTPException(status_code=404, detail="Not found")

    # 2. Verificăm permisiunea
    user = db.query(models.User).filter(models.User.email == current_email).first()
    if gen.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not yours")

    # 3. Verificăm dacă fișierul fizic există
    if os.path.exists(gen.file_path):
        return FileResponse(
            gen.file_path,
            media_type='audio/midi',
            filename=f"{gen.description}.mid"
        )
    else:
        # Dacă fișierul lipsește, îl regenerăm (fallback)
        brain = MusicIntelligence()
        ai_params = brain.analyze_request(gen.description)
        generator = MidiGenerator()
        # Default la full_drums pentru backward compatibility
        midi = generator.generate_track(ai_params, instrument_mode='full_drums')

        # Re-salvăm fișierul
        midi.save(gen.file_path)

        return FileResponse(
            gen.file_path,
            media_type='audio/midi',
            filename=f"{gen.description}.mid"
        )

# Endpoint pentru descărcarea proiectului complet (ZIP cu MIDI + Assets)
@app.get("/api/download/project/{generation_id}")
async def download_project_bundle(
    generation_id: int,
    current_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    """
    Creează și returnează un ZIP cu:
    - Fișierul MIDI
    - Sample-uri audio (kick, snare, hihat)
    - README cu instrucțiuni
    Structură organizată pentru import direct în Ableton Live.
    """
    # 1. Verificări standard (există generarea + ownership)
    gen = db.query(models.Generation).filter(models.Generation.id == generation_id).first()
    if not gen:
        raise HTTPException(status_code=404, detail="Not found")

    user = db.query(models.User).filter(models.User.email == current_email).first()
    if gen.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not yours")

    # 2. Generăm ZIP-ul folosind PackagerService
    assets_path = os.path.join(os.getcwd(), "assets")
    packager = ProjectPackager(assets_dir=assets_path)

    # Verificăm dacă fișierul MIDI există
    if not os.path.exists(gen.file_path):
        # Fallback: regenerăm MIDI-ul dacă lipsește
        brain = MusicIntelligence()
        ai_params = brain.analyze_request(gen.description)
        generator = MidiGenerator()
        # Default la full_drums pentru backward compatibility
        midi = generator.generate_track(ai_params, instrument_mode='full_drums')
        midi.save(gen.file_path)

    zip_buffer = packager.create_ableton_project(gen.file_path, gen.description)

    # 3. Returnăm ZIP-ul ca download
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": f"attachment; filename=AIMusic_Project_{gen.id}.zip"
        }
    )

# Endpoint pentru ștergerea unei generări
@app.delete("/api/history/{generation_id}")
async def delete_generation(
    generation_id: int,
    current_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    """
    Șterge o generare din istoric.
    Șterge atât înregistrarea din DB cât și fișierul MIDI fizic.
    """
    # 1. Căutăm generarea
    gen = db.query(models.Generation).filter(models.Generation.id == generation_id).first()
    if not gen:
        raise HTTPException(status_code=404, detail="Not found")

    # 2. Verificăm proprietarul
    user = db.query(models.User).filter(models.User.email == current_email).first()
    if gen.user_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    # 3. Ștergem fișierul fizic (Opțional, dar recomandat pentru curățenie)
    if gen.file_path and os.path.exists(gen.file_path):
        try:
            os.remove(gen.file_path)
        except Exception as e:
            print(f"Error deleting file: {e}")

    # 4. Ștergem din baza de date
    db.delete(gen)
    db.commit()

    return {"status": "deleted"}

# Pydantic model pentru cererea de generare Ableton project
class AbletonProjectRequest(BaseModel):
    project_name: str = "AI Generated Project"
    bpm: int = 120
    pattern_type: str = "techno"
    bars: int = 4

# Endpoint pentru generarea directă a proiectului Ableton
@app.post("/api/ableton/generate-project")
async def generate_ableton_project(
    request: AbletonProjectRequest,
    current_email: str = Depends(get_current_user_email),
    db: Session = Depends(get_db)
):
    """
    Generează direct un fișier .als Ableton Live cu MIDI și sample-uri incluse.
    Returnează fișierul .als pentru download imediat.
    """
    # 1. Găsim userul în DB
    user = db.query(models.User).filter(models.User.email == current_email).first()

    # 2. Generăm MIDI-ul cu parametrii specificați
    brain = MusicIntelligence()
    ai_params = brain.analyze_request(f"{request.pattern_type} beat at {request.bpm} BPM")
    ai_params['bpm'] = request.bpm  # Override cu BPM-ul cerut

    # 3. Generăm track-ul MIDI complet (full drums)
    generator = MidiGenerator()
    midi = generator.generate_track(ai_params, instrument_mode='full_drums')

    # 4. Salvăm MIDI-ul temporar
    timestamp = int(datetime.datetime.now().timestamp())
    midi_filename = f"temp_ableton_{user.id}_{timestamp}.mid"
    midi_path = STORAGE_DIR / midi_filename

    midi.save(midi_path)

    # 5. Generăm proiectul Ableton (.als) folosind PackagerService
    assets_path = os.path.join(os.getcwd(), "assets")
    packager = ProjectPackager(assets_dir=assets_path)

    try:
        zip_buffer = packager.create_ableton_project(str(midi_path), request.project_name)

        # 6. Salvăm generarea în DB pentru istoric
        new_generation = models.Generation(
            description=f"[ABLETON] {request.project_name} - {request.bpm} BPM {request.pattern_type}",
            file_path=str(midi_path),
            user_id=user.id
        )
        db.add(new_generation)
        db.commit()

        # 7. Returnăm ZIP-ul ca download
        return StreamingResponse(
            zip_buffer,
            media_type="application/zip",
            headers={
                "Content-Disposition": f"attachment; filename={request.project_name.replace(' ', '_')}_{request.bpm}bpm.zip"
            }
        )
    except Exception as e:
        # Curățăm fișierul temporar în caz de eroare
        if os.path.exists(midi_path):
            os.remove(midi_path)
        raise HTTPException(status_code=500, detail=f"Failed to generate Ableton project: {str(e)}")

# Endpoint pentru recomandări inteligente
@app.post("/api/recommendations")
async def get_recommendations(
    context: RecommendationContext,
    current_email: str = Depends(get_current_user_email)
):
    """
    Returnează sugestii personalizate bazate pe contextul curent al utilizatorului.
    Analizează ultimul instrument generat și propune următorii pași logici.
    """
    engine = RecommendationEngine()
    suggestions = engine.get_suggestions(context.model_dump())
    return {"suggestions": suggestions}

# Root endpoint doar ca să vedem că merge serverul
@app.get("/")
def read_root():
    return {"status": "AIMusicCopilot Backend is running"}
