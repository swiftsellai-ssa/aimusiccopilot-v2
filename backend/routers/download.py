from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from services.packager_service import ProjectPackager
from services.midi_generator import MidiGenerator # <--- Acum acest import va merge!
import os
import tempfile

router = APIRouter(prefix="/api/download", tags=["download"])

# Instanțiem serviciile
packager = ProjectPackager(assets_dir="assets") 
midi_gen = MidiGenerator()

@router.post("/package")
async def download_package(
    project_name: str = "amc Track",
    bpm: int = 120,
    style: str = "Techno"
):
    temp_midi_path = None
    try:
        # 1. Creăm un fișier temporar pentru MIDI
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mid") as tmp:
            temp_midi_path = tmp.name

        # 2. Generăm conținutul MIDI folosind generatorul
        # (Aici poți pune logică mai complexă pe viitor)
        midi_gen.generate_simple_midi(temp_midi_path, bpm=bpm)

        # 3. Creăm ZIP-ul Universal (Packager-ul știe să facă restul)
        zip_buffer = packager.create_universal_package(
            midi_path=temp_midi_path,
            project_name=project_name,
            bpm=bpm,
            style=style
        )
        
        # 4. Trimitem ZIP-ul la utilizator
        # Nume curat pentru fișierul descărcat
        filename = f"{project_name.replace(' ', '_')}_{style}_{bpm}bpm.zip"
        
        return Response(
            content=zip_buffer.getvalue(),
            media_type='application/zip',
            headers={
                'Content-Disposition': f'attachment; filename="{filename}"'
            }
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
        
    finally:
        # Curățenie: ștergem fișierul MIDI temporar de pe server
        if temp_midi_path and os.path.exists(temp_midi_path):
            os.remove(temp_midi_path)