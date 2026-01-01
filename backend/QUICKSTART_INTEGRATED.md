# 🚀 Quick Start - Integrated MIDI Generator

## ✅ Integration Complete!

Everything is installed, configured, and ready to use!

---

## 🎯 Start Using It Now

### 1. Start the Backend (2 minutes)

```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload
```

**Expected output**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### 2. Test the API (1 minute)

Open http://127.0.0.1:8000/docs in your browser

You'll see new endpoints:
- `/api/integrated-midi/generate` - Generate MIDI
- `/api/integrated-midi/quick-generate` - Quick generate
- `/api/integrated-midi/download/{id}` - Download file
- `/api/integrated-midi/styles` - Get styles
- `/api/integrated-midi/instruments` - Get instruments
- `/api/integrated-midi/presets` - Get presets

### 3. Generate Your First Pattern (30 seconds)

#### Using the Demo Script:
```bash
cd backend
python examples/integrated_generator_demo.py
```

**Output**: 6 MIDI files in `output/demo/`

#### Using the API:
1. Login to get token
2. Use Swagger UI at http://127.0.0.1:8000/docs
3. Try `/api/integrated-midi/quick-generate`
4. Download the generated MIDI

---

## 🎨 Frontend Integration

### Add to Your React App

```jsx
// In your App.js or routes
import IntegratedMidiGenerator from './components/IntegratedMidiGenerator';

<IntegratedMidiGenerator />
```

### Start Frontend

```bash
cd frontend
npm start
```

Navigate to the component and start generating!

---

## 📋 What's Available

### API Endpoints

✅ **POST** `/api/integrated-midi/generate`
  - Full control over all parameters
  - Returns generation_id for download

✅ **POST** `/api/integrated-midi/quick-generate`
  - One-click generation
  - Smart defaults based on style

✅ **GET** `/api/integrated-midi/download/{generation_id}`
  - Download generated MIDI file

✅ **GET** `/api/integrated-midi/styles`
  - List: techno, trap, house, dnb, lofi

✅ **GET** `/api/integrated-midi/instruments`
  - Drums: kick, snare, hat, clap, etc.
  - Melodic: bass, melody, lead, synth

✅ **GET** `/api/integrated-midi/presets`
  - Minimal, Balanced, Complex, Groovy

### Features

✅ Text description → MIDI pattern
✅ 5 music styles supported
✅ 15+ instruments available
✅ DNA-based generation
✅ Humanization engine
✅ BPM control (60-200)
✅ Bar count (1-32)
✅ Musical key/scale selection
✅ Preset system
✅ Database persistence
✅ User authentication
✅ Download management

---

## 🧪 Quick Tests

### Test 1: API Works
```bash
curl http://localhost:8000/api/integrated-midi/styles
```

**Expected**: List of styles

### Test 2: Generate MIDI (requires auth token)
```bash
curl -X POST "http://localhost:8000/api/integrated-midi/quick-generate?description=techno%20kick&style=techno" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Expected**: JSON with generation_id

### Test 3: Demo Script
```bash
python examples/integrated_generator_demo.py
```

**Expected**: 6 MIDI files created

---

## 📖 Example Requests

### Simple Generation
```json
POST /api/integrated-midi/generate
{
  "description": "dark techno kick",
  "style": "techno",
  "instrument": "kick",
  "bpm": 130,
  "bars": 4
}
```

### Complex Pattern with DNA
```json
POST /api/integrated-midi/generate
{
  "description": "rolling trap hi-hats",
  "style": "trap",
  "instrument": "hat",
  "bpm": 140,
  "bars": 8,
  "use_dna": true,
  "humanize": true,
  "density": 0.9,
  "complexity": 0.8,
  "groove": 0.3,
  "evolution": 0.4,
  "velocity_curve": "exponential"
}
```

### Minimal Pattern
```json
POST /api/integrated-midi/generate
{
  "description": "minimal techno",
  "style": "techno",
  "instrument": "kick",
  "bpm": 125,
  "bars": 8,
  "density": 0.3,
  "complexity": 0.2,
  "evolution": 0.1
}
```

---

## 🎯 Common Use Cases

### Use Case 1: Quick Beat for DAW
```
1. Quick generate → "aggressive trap beat"
2. Download MIDI
3. Import into Ableton/FL Studio
4. Add sounds and effects
5. Done!
```

### Use Case 2: Custom Pattern
```
1. Describe pattern
2. Select style and instrument
3. Tweak DNA parameters
4. Generate
5. Download and use
```

### Use Case 3: Variations
```
1. Generate base pattern
2. Adjust complexity slider
3. Generate variations
4. Compare and choose best
```

---

## 🐛 Troubleshooting

### Server won't start?
```bash
# Check virtual environment
cd backend
venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt

# Try again
uvicorn main:app --reload
```

### Import errors?
```bash
# All imports should work:
python -c "from routers import integrated_midi"
python -c "from services.integrated_midi_generator import IntegratedMidiGenerator"
python -c "import main"
```

### Generation fails?
- Check you're logged in (have valid token)
- Check storage directory exists
- Enable logging in router
- Check main.py includes router

---

## 📁 File Locations

### Generated Files
```
backend/storage/integrated_midi/
  ├── pattern_kick_123_1234567890.mid
  ├── pattern_hat_123_1234567891.mid
  └── ...
```

### Demo Output
```
backend/output/demo/
  ├── techno_kick.mid
  ├── trap_hats.mid
  ├── house_drums_quantized.mid
  └── ...
```

---

## 🎓 Next Steps

### Learn More
1. Read [QUICK_REFERENCE.md](services/QUICK_REFERENCE.md)
2. Check [INTEGRATION_COMPLETE.md](INTEGRATION_COMPLETE.md)
3. Review [ARCHITECTURE.md](services/ARCHITECTURE.md)

### Customize
1. Add more styles in `advanced_midi_generator.py`
2. Create custom presets in router
3. Modify frontend component styling
4. Add more instruments

### Extend
1. Create multi-track generation
2. Add MIDI CC automation
3. Implement pattern variations
4. Build pattern library

---

## ✅ Success Checklist

- [x] Backend server starts
- [x] API endpoints accessible
- [x] Demo script works
- [x] Frontend component available
- [x] Database integration working
- [x] Authentication integrated
- [x] Files can be downloaded
- [x] All styles working
- [x] All instruments working
- [x] DNA parameters functional
- [x] Humanization working
- [x] Presets available

---

## 🎉 You're Ready!

Everything is set up and ready to use. Start generating amazing MIDI patterns!

### Quick Commands

```bash
# Start backend
cd backend && venv\Scripts\activate && uvicorn main:app --reload

# Run demo
cd backend && python examples/integrated_generator_demo.py

# Start frontend
cd frontend && npm start
```

**Happy generating! 🎵🎹🎶**
