# AI Music Copilot

Advanced AI-powered MIDI generation platform with DNA-based pattern algorithms.

---

## Features

### Complete Track Generation
- Full multi-track MIDI generation
- AI-powered composition
- Style-aware arrangements
- Ableton export support
- Pattern DNA analysis

### DNA Pattern Generator
- Individual instrument pattern generation
- Advanced DNA parameters (density, complexity, groove, evolution)
- Humanization engine for natural feel
- 5 music styles: Techno, Trap, House, DnB, Lo-Fi
- 15+ instruments: drums and melodic elements
- Preset system for quick workflows
- Real-time parameter control

### Multi-Track Projects (New! 🎼)
- Combine drums, bass, melody into full arrangements
- Professional mixer controls (volume, pan, mute, solo)
- Export as Type 1 MIDI for any DAW
- Visual track timeline editor
- DNA parameters preserved per track
- Project-level settings (BPM, key, scale)
- Track variations with A/B testing (coming soon)

### Social & Sharing Features
- Share generations publicly with unique links
- Public gallery with trending/popular patterns
- Community voting (upvote/downvote)
- Preset marketplace for sharing custom presets
- Engagement tracking (views, plays, downloads)

---

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Installation

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run database migrations (if needed)
alembic upgrade head
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install
```

### Running the Application

#### Start Backend
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload
```
Backend runs at: http://localhost:8000

Swagger UI: http://localhost:8000/docs

#### Start Frontend
```bash
cd frontend
npm run dev
```
Frontend runs at: http://localhost:3000

---

## Project Structure

```
aimusiccopilot/
├── backend/
│   ├── main.py                          # FastAPI application
│   ├── models/                          # Database models
│   ├── routers/                         # API routes
│   │   ├── auth.py                     # Authentication
│   │   ├── download.py                 # File downloads
│   │   └── integrated_midi.py          # Pattern generator API
│   ├── services/                        # Business logic
│   │   ├── integrated_midi_generator.py # Main pattern generator
│   │   ├── advanced_midi_generator.py   # DNA-based patterns
│   │   ├── humanization_engine.py       # Timing humanization
│   │   ├── midi_generator.py            # Basic MIDI generation
│   │   ├── ai_service.py                # AI intelligence
│   │   ├── packager_service.py          # Project packaging
│   │   └── recommendation_engine.py     # Recommendations
│   ├── utils/                           # Utilities
│   ├── storage/                         # Generated files
│   │   ├── integrated_midi/            # Pattern files
│   │   └── generations/                # Complete tracks
│   ├── examples/                        # Example scripts
│   └── requirements.txt                 # Python dependencies
│
├── frontend/
│   ├── app/                             # Next.js app directory
│   │   ├── page.tsx                    # Main page
│   │   └── pattern-generator/
│   │       └── page.tsx                # Pattern generator page
│   ├── src/
│   │   └── components/                 # React components
│   │       ├── IntegratedMidiGenerator.jsx
│   │       ├── IntegratedMidiGenerator.tsx
│   │       ├── IntegratedMidiGenerator.css
│   │       ├── MusicPlayer.tsx
│   │       ├── MidiVisualizer.tsx
│   │       └── ...
│   └── package.json                    # npm dependencies
│
└── Documentation/
    ├── README.md                        # This file
    ├── SETUP_AND_RUN.md                # Setup guide
    ├── NEXTJS_INTEGRATION_GUIDE.md     # Integration guide
    ├── API_TESTING_GUIDE.md            # API testing
    └── backend/
        ├── INTEGRATION_COMPLETE.md     # Integration status
        ├── QUICKSTART_INTEGRATED.md    # Quick reference
        └── services/
            ├── QUICK_REFERENCE.md      # API reference
            ├── ARCHITECTURE.md         # Architecture docs
            └── ...
```

---

## API Endpoints

### Authentication
- `POST /token` - Login and get JWT token
- `POST /register` - Create new account

### Complete Track Generation (v2)
- `POST /api/v2/generate/complete` - Generate full track
- `POST /api/v2/generate/layer` - Generate single layer
- `GET /api/v2/download/{id}` - Download generation
- `GET /api/history` - Get generation history
- `POST /api/recommendations` - Get AI recommendations

### Pattern Generator (Integrated MIDI)
- `GET /api/integrated-midi/styles` - Get available styles
- `GET /api/integrated-midi/instruments` - Get instruments
- `GET /api/integrated-midi/presets` - Get DNA presets
- `POST /api/integrated-midi/quick-generate` - Quick generation
- `POST /api/integrated-midi/generate` - Advanced generation
- `GET /api/integrated-midi/download/{id}` - Download pattern

---

## Usage Examples

### Quick Pattern Generation (API)

```bash
# Login
TOKEN=$(curl -X POST "http://localhost:8000/token" \
  -d "username=user@example.com&password=password" \
  | jq -r '.access_token')

# Generate pattern
curl -X POST "http://localhost:8000/api/integrated-midi/quick-generate?description=techno%20kick&style=techno" \
  -H "Authorization: Bearer $TOKEN"
```

### Advanced Pattern Generation (API)

```bash
curl -X POST http://localhost:8000/api/integrated-midi/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "dark techno kick",
    "style": "techno",
    "instrument": "kick",
    "bpm": 130,
    "bars": 4,
    "use_dna": true,
    "humanize": true,
    "density": 0.7,
    "complexity": 0.6,
    "groove": 0.2,
    "evolution": 0.3
  }'
```

### Using the Frontend

1. **Navigate to Pattern Generator**: http://localhost:3000/pattern-generator
2. **Quick Generate**: Enter description, select style, click "Quick Generate"
3. **Advanced Mode**: Expand "Advanced Parameters" for full control
4. **DNA Parameters**: Adjust sliders for density, complexity, groove, evolution
5. **Download**: Click download button to get MIDI file

---

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **JWT** - Authentication
- **mido** - MIDI file handling
- **numpy** - Mathematical operations

### Frontend
- **Next.js** - React framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **axios** - HTTP client

### AI/Generation
- **Custom DNA Algorithm** - Pattern generation
- **Humanization Engine** - Natural timing
- **Music Intelligence** - AI recommendations

---

## Configuration

### Environment Variables

Create `.env` file in backend directory:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///./music_copilot.db
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### Frontend Configuration

Update API base URL in frontend if needed:

```typescript
// frontend/src/config.ts
export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

---

## Development

### Running Tests

#### Backend Tests
```bash
cd backend
pytest
python -m pytest tests/
```

#### Integration Tests
```bash
python test_integration.py
```

#### Frontend Tests
```bash
cd frontend
npm test
npm run lint
```

### Running Demo Scripts

```bash
cd backend
python examples/integrated_generator_demo.py
```

This generates 6 example MIDI files in `backend/output/demo/`

---

## Deployment

### Backend Deployment

```bash
# Install production dependencies
pip install -r requirements.txt

# Run with gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Frontend Deployment

```bash
# Build for production
npm run build

# Start production server
npm start
```

### Docker Deployment (Optional)

```dockerfile
# Backend Dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Documentation

- **[SETUP_AND_RUN.md](SETUP_AND_RUN.md)** - Complete setup guide
- **[NEXTJS_INTEGRATION_GUIDE.md](NEXTJS_INTEGRATION_GUIDE.md)** - Frontend integration
- **[API_TESTING_GUIDE.md](API_TESTING_GUIDE.md)** - API testing guide
- **[backend/INTEGRATION_COMPLETE.md](backend/INTEGRATION_COMPLETE.md)** - Integration details
- **[backend/QUICKSTART_INTEGRATED.md](backend/QUICKSTART_INTEGRATED.md)** - Quick reference
- **[backend/services/ARCHITECTURE.md](backend/services/ARCHITECTURE.md)** - System architecture

---

## Features in Detail

### DNA-Based Pattern Generation

The pattern generator uses a sophisticated DNA system:

- **Density** (0.0-1.0): Controls how many notes are in the pattern
- **Complexity** (0.0-1.0): Determines pattern variation and intricacy
- **Groove** (0.0-1.0): Adds swing and timing feel
- **Evolution** (0.0-1.0): Pattern changes over time
- **Velocity Curve**: Natural, Accent, Exponential, Random

### Humanization Engine

Makes patterns feel more natural:

- Timing variations (±10ms)
- Velocity randomization
- Micro-timing adjustments
- Musical feel preservation

### Style Support

Five distinct music styles with appropriate defaults:

- **Techno**: 130 BPM, 4/4, minimal and driving
- **Trap**: 140 BPM, complex hi-hats, 808 bass
- **House**: 125 BPM, groovy, four-to-the-floor
- **DnB**: 174 BPM, fast breaks, rolling bass
- **Lo-Fi**: 85 BPM, laid-back, jazzy

### Instrument Categories

**Drums:**
- kick, snare, hat, clap, rim, tom, crash, ride, perc, drums

**Melodic:**
- bass, melody, lead, pad, synth

---

## Troubleshooting

### Common Issues

**Backend won't start**
- Check Python version: `python --version` (need 3.8+)
- Verify virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

**Frontend won't start**
- Check Node version: `node --version` (need 16+)
- Clear cache: `rm -rf node_modules && npm install`
- Check for port conflicts on 3000

**401 Unauthorized errors**
- Verify you're logged in
- Check token in localStorage
- Token may be expired - login again

**MIDI files not generating**
- Check storage directory exists
- Verify database connection
- Check logs for errors

**Download not working**
- Ensure proper token in Authorization header
- Check CORS configuration
- Verify file exists in storage

See [SETUP_AND_RUN.md](SETUP_AND_RUN.md) for detailed troubleshooting.

---

## Contributing

### Development Workflow

1. Create feature branch: `git checkout -b feature/new-feature`
2. Make changes and test
3. Run tests: `pytest` and `npm test`
4. Commit changes: `git commit -m "Add new feature"`
5. Push and create PR

### Code Style

**Python:**
- Follow PEP 8
- Use type hints
- Add docstrings

**TypeScript:**
- Use ESLint configuration
- Follow React best practices
- Add JSDoc comments

---

## License

[Your License Here]

---

## Credits

Built with:
- FastAPI
- Next.js
- mido (MIDI library)
- And many other amazing open source projects

---

## Support

For issues and questions:
- Check documentation first
- Review troubleshooting guide
- Check existing issues
- Create new issue with details

---

## Roadmap

- [ ] Multi-track pattern generation
- [ ] MIDI CC automation
- [ ] More music styles
- [ ] VST plugin integration
- [ ] Cloud storage integration
- [ ] Collaborative features
- [ ] Mobile app

---

**Happy music making! 🎵🎹🎶**
