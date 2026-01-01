# backend/services/packager_service.py

import io
import zipfile
import os
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

class ProjectPackager:
    def __init__(self, assets_dir: str = "assets"):
        self.assets_dir = Path(assets_dir)
        os.makedirs(self.assets_dir, exist_ok=True)

    def create_ableton_project(self, midi_path: str, description: str) -> io.BytesIO:
        """
        Create a ZIP package for Ableton Live projects.
        Backwards compatible wrapper for create_universal_package.
        """
        # Parse description to extract metadata
        bpm = 120  # default
        style = "trap"  # default

        # Try to extract BPM from description
        import re
        bpm_match = re.search(r'(\d+)\s*bpm', description, re.IGNORECASE)
        if bpm_match:
            bpm = int(bpm_match.group(1))

        # Try to extract style/genre from description
        common_styles = ['trap', 'house', 'techno', 'dubstep', 'dnb', 'ambient', 'hip hop']
        description_lower = description.lower()
        for s in common_styles:
            if s in description_lower:
                style = s
                break

        # Use description as project name
        project_name = description[:50]  # Limit length

        return self.create_universal_package(
            midi_path=midi_path,
            project_name=project_name,
            bpm=bpm,
            style=style,
            metadata={}
        )

    def create_universal_package(self,
                                midi_path: str,
                                project_name: str,
                                bpm: int,
                                style: str,
                                metadata: Optional[Dict] = None) -> io.BytesIO:
        """
        Create a professional ZIP package with all assets
        """
        zip_buffer = io.BytesIO()
        
        # Clean project name
        clean_name = "".join([c for c in project_name if c.isalnum() or c in (' ', '-', '_')]).strip()
        if not clean_name or clean_name.lower() in ["ai generated", "untitled"]:
            clean_name = f"{style.title()}_Project"
        
        # Generate unique folder name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        folder_name = f"{clean_name}_{style}_{bpm}bpm_{timestamp}"
        
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            
            # 1. Add MIDI file
            if os.path.exists(midi_path):
                midi_name = f"{clean_name}.mid"
                zf.write(midi_path, arcname=f"{folder_name}/MIDI/{midi_name}")
            
            # 2. Create project info JSON
            project_info = {
                "name": clean_name,
                "style": style,
                "bpm": bpm,
                "created": timestamp,
                "generator": "AI Music Copilot",
                "metadata": metadata or {}
            }
            
            import json
            zf.writestr(f"{folder_name}/project.json", 
                       json.dumps(project_info, indent=2))
            
            # 3. Create README with instructions
            readme_content = self._generate_readme(clean_name, style, bpm, metadata)
            zf.writestr(f"{folder_name}/README.txt", readme_content)
            
            # 4. Create Ableton folder structure
            zf.writestr(f"{folder_name}/Ableton Project Info/readme.txt", 
                       "Place .als files here when available")
            
            # 5. Add presets folder
            zf.writestr(f"{folder_name}/Presets/readme.txt",
                       "Device presets will be added here")
            
        zip_buffer.seek(0)
        return zip_buffer

    def _generate_readme(self, name: str, style: str, bpm: int, metadata: Dict) -> str:
        """Generate professional README"""
        
        key = metadata.get('key', 'C') if metadata else 'C'
        scale = metadata.get('scale', 'minor') if metadata else 'minor'
        
        readme = f"""
╔══════════════════════════════════════════════════════════════════╗
║                     AI MUSIC COPILOT PROJECT                     ║
╚══════════════════════════════════════════════════════════════════╝

PROJECT: {name}
STYLE: {style.upper()}
TEMPO: {bpm} BPM
KEY: {key} {scale}
GENERATED: {datetime.now().strftime('%Y-%m-%d %H:%M')}

═══════════════════════════════════════════════════════════════════

QUICK START GUIDE:
─────────────────
1. Import MIDI:
   • Drag the .mid file from /MIDI/ into your DAW
   • MIDI Channel 10: Drums
   • MIDI Channel 1: Melodic instruments

2. In Ableton Live:
   • Create MIDI tracks for each channel
   • Load Drum Rack on Channel 10
   • Load your favorite synth on Channel 1

3. Production Tips for {style.upper()}:
   • Kick: Use compression ratio 4:1 with fast attack
   • Bass: Apply subtle saturation for warmth
   • Mix: Leave headroom of -6dB for mastering

═══════════════════════════════════════════════════════════════════

TRACK STRUCTURE:
───────────────
- Bars 1-4: Main Pattern
- Suggested Arrangement:
  - Intro: 8 bars (filtered)
  - Build: 8 bars (add elements)
  - Drop: 16 bars (full energy)
  - Breakdown: 8 bars (remove kick)
  - Build 2: 8 bars
  - Drop 2: 16 bars
  - Outro: 8 bars

═══════════════════════════════════════════════════════════════════

RECOMMENDED WORKFLOW:
────────────────────
□ Load MIDI into your DAW
□ Assign appropriate instruments
□ Add sidechain compression (kick → bass)
□ Apply EQ to carve frequency space
□ Add reverb sends for depth
□ Automate filters for movement
□ Master with limiter at -0.3dB ceiling

═══════════════════════════════════════════════════════════════════

SUPPORT & UPDATES:
─────────────────
Web: aimusiccopilot.com
Contact: support@aimusiccopilot.com

Created with ❤️ by u/EthericSounds
© {datetime.now().year} - All rights reserved
═══════════════════════════════════════════════════════════════════
"""
        return readme