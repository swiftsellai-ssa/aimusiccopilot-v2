# Setup and Run Guide - AI Music Copilot

Complete guide to get everything running quickly.

---

## Quick Start (3 Steps)

### Step 1: Start the Backend (2 minutes)

```bash
# Navigate to backend
cd backend

# Activate virtual environment
venv\Scripts\activate

# Start server
uvicorn main:app --reload
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**Verify:** Open http://127.0.0.1:8000/docs - you should see Swagger UI

---

### Step 2: Start the Frontend (1 minute)

```bash
# Open new terminal
cd frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

**Expected Output:**
```
ready - started server on 0.0.0.0:3000
```

**Verify:** Open http://localhost:3000

---

### Step 3: Test the Integration (30 seconds)

#### Option A: Use the Test Script

```bash
# In project root
python test_integration.py
```

Update the credentials in the script first:
```python
EMAIL = "your@email.com"
PASSWORD = "yourpassword"
```

#### Option B: Use Swagger UI

1. Go to http://127.0.0.1:8000/docs
2. Click "Authorize"
3. Login via `/token` endpoint
4. Copy access token
5. Test `/api/integrated-midi/quick-generate`

#### Option C: Use the Frontend

1. Go to http://localhost:3000
2. Login with your account
3. Navigate to Pattern Generator
4. Try Quick Generate

---

## Project Structure

```
aimusiccopilot/
├── backend/
│   ├── main.py                          # FastAPI app (router included ✓)
│   ├── routers/
│   │   └── integrated_midi.py           # New MIDI generator endpoints
│   ├── services/
│   │   ├── integrated_midi_generator.py # Core generator (fixed ✓)
│   │   ├── advanced_midi_generator.py   # DNA patterns
│   │   └── humanization_engine.py       # Humanization
│   ├── storage/
│   │   └── integrated_midi/             # Generated files
│   └── requirements.txt                 # Dependencies (mido added ✓)
│
├── frontend/
│   ├── src/components/
│   │   ├── IntegratedMidiGenerator.jsx  # React component
│   │   ├── IntegratedMidiGenerator.tsx  # TypeScript version
│   │   └── IntegratedMidiGenerator.css  # Styling
│   └── app/
│       ├── page.tsx                      # Your main page
│       └── pattern-generator/
│           └── page.tsx                  # Dedicated pattern page (new)
│
└── Documentation/
    ├── NEXTJS_INTEGRATION_GUIDE.md      # How to integrate
    ├── API_TESTING_GUIDE.md             # Testing endpoints
    ├── INTEGRATION_COMPLETE.md          # What's integrated
    └── QUICKSTART_INTEGRATED.md         # Quick reference
```

---

## Available Endpoints

### Integrated MIDI Generator (New)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/integrated-midi/styles` | GET | No | Get available styles |
| `/api/integrated-midi/instruments` | GET | No | Get available instruments |
| `/api/integrated-midi/presets` | GET | No | Get DNA presets |
| `/api/integrated-midi/quick-generate` | POST | Yes | Quick pattern generation |
| `/api/integrated-midi/generate` | POST | Yes | Advanced pattern generation |
| `/api/integrated-midi/download/{id}` | GET | Yes | Download MIDI file |

### Existing API (v2)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v2/generate/complete` | POST | Yes | Generate complete track |
| `/api/v2/generate/layer` | POST | Yes | Generate single layer |
| `/api/v2/download/{id}` | GET | Yes | Download generation |
| `/api/history` | GET | Yes | Get generation history |

---

## Frontend Integration Options

### Option 1: Standalone Page (Easiest)

Already created at [/app/pattern-generator/page.tsx](frontend/app/pattern-generator/page.tsx)

**Access:** http://localhost:3000/pattern-generator

**Add navigation to your main page:**
```tsx
// In your navigation component
<Link href="/pattern-generator">
  Pattern Generator
</Link>
```

---

### Option 2: Tab Integration

Add to your existing [page.tsx](frontend/app/page.tsx):

```tsx
'use client';

import { useState } from 'react';
import IntegratedMidiGenerator from '@/components/IntegratedMidiGenerator';
// ... your other imports

export default function Home() {
  const [activeTab, setActiveTab] = useState<'complete' | 'pattern'>('complete');

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Tab Toggle */}
      <div className="flex justify-center gap-4 mb-8">
        <button
          onClick={() => setActiveTab('complete')}
          className={`px-6 py-3 rounded-lg ${
            activeTab === 'complete' ? 'bg-blue-600' : 'bg-gray-700'
          }`}
        >
          Complete Track
        </button>
        <button
          onClick={() => setActiveTab('pattern')}
          className={`px-6 py-3 rounded-lg ${
            activeTab === 'pattern' ? 'bg-blue-600' : 'bg-gray-700'
          }`}
        >
          Pattern Generator
        </button>
      </div>

      {/* Content */}
      {activeTab === 'complete' ? (
        // Your existing components
        <div>
          {/* MusicPlayer, MidiVisualizer, etc. */}
        </div>
      ) : (
        // New pattern generator
        <IntegratedMidiGenerator />
      )}
    </div>
  );
}
```

---

### Option 3: Side-by-Side

Display both generators:

```tsx
<div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
  <div>
    <h2>Complete Track Generator</h2>
    {/* Your existing generator */}
  </div>
  <div>
    <h2>Pattern Generator</h2>
    <IntegratedMidiGenerator />
  </div>
</div>
```

---

## Testing Checklist

Before using in production, test these scenarios:

### Backend Tests

- [ ] Server starts without errors
- [ ] Swagger UI accessible at `/docs`
- [ ] Can login and get JWT token
- [ ] `/api/integrated-midi/styles` returns styles
- [ ] `/api/integrated-midi/instruments` returns instruments
- [ ] `/api/integrated-midi/quick-generate` creates MIDI
- [ ] `/api/integrated-midi/generate` with full params works
- [ ] `/api/integrated-midi/download/{id}` downloads file
- [ ] Files saved to `storage/integrated_midi/`
- [ ] Database records created in `generations` table

### Frontend Tests

- [ ] Component loads without errors
- [ ] Can see styles in dropdown
- [ ] Can see instruments in dropdown
- [ ] Quick Generate button works
- [ ] Advanced parameters expand/collapse
- [ ] DNA sliders update values
- [ ] Presets apply parameters
- [ ] Generate button shows loading state
- [ ] Success message displays after generation
- [ ] Download button downloads MIDI file
- [ ] CSS styling loads correctly

### Integration Tests

- [ ] Run `python test_integration.py` - all pass
- [ ] Can generate from frontend and download
- [ ] Files appear in backend storage
- [ ] Database shows new generations
- [ ] Can view history in `/api/history`

---

## Troubleshooting

### Backend won't start

```bash
# Check virtual environment
cd backend
venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt

# Check for port conflicts
netstat -ano | findstr :8000
```

### Frontend won't start

```bash
# Clear cache and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### 401 Unauthorized errors

- Check you're logged in
- Verify token in localStorage: `localStorage.getItem('token')`
- Token may be expired - login again

### Downloads not working

The component needs proper token handling. Update download function:

```tsx
const handleDownload = async () => {
  const token = localStorage.getItem('token');
  const response = await axios.get(
    `/api/integrated-midi/download/${result.generation_id}`,
    {
      headers: { Authorization: `Bearer ${token}` },
      responseType: 'blob'
    }
  );
  const url = window.URL.createObjectURL(new Blob([response.data]));
  const link = document.createElement('a');
  link.href = url;
  link.download = 'pattern.mid';
  link.click();
};
```

### CORS errors

Make sure backend has CORS configured in [main.py](backend/main.py):

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Demo Script

Test the generator without frontend:

```bash
cd backend
python examples/integrated_generator_demo.py
```

This creates 6 MIDI files in `backend/output/demo/`

---

## Common Commands

### Backend

```bash
# Start server
cd backend && venv\Scripts\activate && uvicorn main:app --reload

# Run tests
cd backend && python -m pytest

# Run demo
cd backend && python examples/integrated_generator_demo.py

# Check imports
cd backend && python -c "from services.integrated_midi_generator import IntegratedMidiGenerator"
```

### Frontend

```bash
# Start dev server
cd frontend && npm run dev

# Build for production
cd frontend && npm run build

# Run production build
cd frontend && npm start

# Check for errors
cd frontend && npm run lint
```

### Testing

```bash
# Run integration tests
python test_integration.py

# Quick API test
curl http://localhost:8000/api/integrated-midi/styles

# Test with auth (replace TOKEN)
curl -X POST "http://localhost:8000/api/integrated-midi/quick-generate?description=test&style=techno" \
  -H "Authorization: Bearer TOKEN"
```

---

## Next Steps

1. ✅ **Backend is integrated** - Router loaded in main.py
2. ✅ **Frontend component ready** - Both .jsx and .tsx versions
3. ✅ **Documentation complete** - Multiple guides available
4. ✅ **Testing tools ready** - Scripts and guides provided

### To Use It:

1. Start backend: `cd backend && uvicorn main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Navigate to: http://localhost:3000/pattern-generator
4. Or integrate into your main page using the examples above

### To Customize:

- Modify DNA parameters in the backend generator
- Add more styles in `advanced_midi_generator.py`
- Customize frontend styling in `IntegratedMidiGenerator.css`
- Add more presets in the router

---

## Documentation Index

- **[NEXTJS_INTEGRATION_GUIDE.md](NEXTJS_INTEGRATION_GUIDE.md)** - How to integrate the component
- **[API_TESTING_GUIDE.md](API_TESTING_GUIDE.md)** - Complete API testing guide
- **[backend/INTEGRATION_COMPLETE.md](backend/INTEGRATION_COMPLETE.md)** - What's been integrated
- **[backend/QUICKSTART_INTEGRATED.md](backend/QUICKSTART_INTEGRATED.md)** - Quick reference
- **[backend/services/QUICK_REFERENCE.md](backend/services/QUICK_REFERENCE.md)** - API quick reference

---

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the relevant documentation
3. Check browser console for frontend errors
4. Check terminal output for backend errors
5. Enable DEBUG logging in the router

---

**Everything is ready to use! Start the servers and begin generating patterns! 🎵**
