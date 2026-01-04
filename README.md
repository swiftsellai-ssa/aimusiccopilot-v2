# amc (AI Music Co-pilot) 🎹

**amc** (formerly SwiftSell AI) is an advanced AI-powered MIDI generation platform designed to act as a creative partner for musicians and producers. Unlike random note generators, **amc** uses music theory constraints, style-specific algorithms, and sophisticated "humanization" engines to create professional-grade loops that are drag-and-drop ready for any DAW.

> **Philosophy:** "Complexity in Simplicity." We hide sophisticated music theory engines behind a simple, intuitive interface.

---

## 🚀 Key Features (v2)

### 🧠 Advanced Intelligence Engines
* **Pattern Intelligence:** Generates logical phrases using **AABA**, **ABAB**, or **Call-and-Response** structures rather than repetitive loops.
* **Harmonic Engine:** Replaces random pitch selection with style-specific functional harmony (e.g., **ii-V-I** for Jazz, **i-VI-III-VII** for Trap) and intelligent voice leading.
* **Rhythm Engine:** Applies genre-specific swing (e.g., *Tresillo* for Reggaeton, *Tumbao* for Latin Bass) and generates "ghost notes" for realism.
* **Production Engine:** Automation for Velocity (Dynamics) and Articulation (Staccato/Legato).

### 🌍 Extended Style Library (15+ Genres)
Support for over 15 distinct genres with unique algorithmic definitions:

| Category | Styles | Distinctive Features |
| :--- | :--- | :--- |
| **Electronic** | Techno, House, Deep House, Trap, DnB | Rolling Hi-Hats, Offbeat Bass, Buildups |
| **Urban** | Hip Hop, Boom Bap, Lofi, RnB | Laid-back Swing, Ghost Kicks, Jazz Chords |
| **Pop/Rock** | Pop, Rock, Indie, Funk, Disco | Strong Backbeats, Power Chords, Walking Bass |
| **Jazz/Soul** | Jazz, Soul, Gospel | ii-V-I Progressions, 8th Note Swing, Extended Chords |
| **World** | Reggaeton, Latin, Afrobeat | Tresillo Rhythms, Tumbao Bass, Percussion Fills |
| **Hard** | Metal, Punk | Aggressive Velocity, Fast Tempos |

### 🎼 Multi-Track Projects
* Combine Drums, Bass, and Melody into full arrangements.
* **Smart Export:** Files are automatically named with professional metadata (e.g., `amc_Latin_Bass_Verse_Cm_100bpm.mid`).

---

## 🛠️ Tech Stack

* **Frontend:** Next.js 14, TypeScript, Tailwind CSS, Tone.js (Audio Preview & Visualization).
* **Backend:** Python 3.10+, FastAPI, Pydantic, SQLAlchemy.
* **Audio/MIDI:** Custom Python MIDI construction algorithms (Mido).
* **Deployment:** Docker / Render.

---

## ⚡ Quick Start

### Prerequisites
* Python 3.10+
* Node.js 18+

### 1. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload
```
The backend API will be available at `http://localhost:8000`.

### 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```
The application will be available at `http://localhost:3000`.

---


## 📂 Project Structure

```
amc/
├── backend/
│   ├── main.py                      # FastAPI Entry Point
│   ├── services/
│   │   ├── integrated_midi_generator.py # MAIN ORCHESTRATOR
│   │   ├── pattern_intelligence.py      # Structure (AABA)
│   │   ├── harmonic_engine.py           # Theory (Chords/Scales)
│   │   ├── rhythm_engine.py             # Groove & Ghost Notes
│   │   ├── production_engine.py         # Velocity & Humanization
│   │   └── style_patterns.py            # Genre Definitions
│   └── output/                          # Generated MIDI files
│
└── frontend/
    ├── src/
    │   ├── components/
    │   │   ├── EnhancedGenerator.tsx    # Main UI
    │   │   ├── MidiVisualizer.tsx       # Canvas Piano Roll
    │   │   └── ...
    │   └── constants/
    │       └── musicStyles.ts           # Frontend Style Config
```

---

## 🔌 API Endpoints

### Generation (v2)
* `POST /api/generate/midi` - The core endpoint for the new engine.
    * **Params**: `style`, `instrument`, `sub_option` (e.g., 'groove_bass'), `complexity` ('expert' enables AABA/Passing Tones), `key`, `bpm`.

### Legacy / Utility
* `GET /api/styles` - Get available styles.
* `GET /midi_files/{filename}` - Download generated MIDI.

---

## 🗺️ Roadmap & Status

[x] **Phase 1**: Core MIDI Generation.
[x] **Phase 2**: Advanced Engines (Pattern, Rhythm, Harmony).
[x] **Phase 3**: Style Library Expansion (15+ Genres).
[x] **Phase 4**: Professional UI/UX (Visualizer, Dark Mode).
[x] **Phase 5**: Smart Export & File Naming.
[ ] **Phase 6**: Arrangement Mode (Verse/Chorus Sequence Builder).
[ ] **Phase 7**: VST Plugin Integration.

---

## 🤝 Contributing

This project is part of a **#buildinpublic** journey. Feedback, PRs, and feature requests are welcome!

Built with 💜 by Gabriel. @swiftsell_ai

---

## 📚 Documentation

For more detailed guides on API usage, testing, and architecture, please refer to the `Documentation/` directory.
