# 🚀 Social Features Setup Guide

Quick guide to get the new social/sharing features up and running.

## Prerequisites

- Backend running on `http://localhost:8000`
- Frontend running on `http://localhost:3000`
- SQLite database initialized
- User account created

## Setup Steps

### 1. Create Database Tables

The social feature tables will be created automatically when you start the backend:

```bash
cd backend
python main.py
```

**Tables Created:**
- `shared_generations` - Public MIDI generations
- `generation_votes` - Votes on shared generations
- `shared_presets` - Community presets
- `preset_votes` - Votes on presets

**Verify Tables:**
```bash
sqlite3 sql_app.db
.tables
# Should show: shared_generations, generation_votes, shared_presets, preset_votes
.quit
```

### 2. Start Backend

```bash
cd backend
uvicorn main:app --reload
```

**Verify Social Endpoints:**
- Open browser to `http://localhost:8000/docs`
- Look for `/social/*` endpoints in the API docs
- Should see 11 new endpoints

### 3. Start Frontend

```bash
cd frontend
npm run dev
```

**Verify Pages:**
- Main generator: `http://localhost:3000/`
- Public gallery: `http://localhost:3000/gallery`
- Preset marketplace: `http://localhost:3000/presets`

### 4. Test Features

#### Test Share Generation:

1. Log in to the app
2. Generate a pattern (any type)
3. Click "🔗 Share" button (next to Save Preset)
4. Enter title: "Test Pattern"
5. Click "Share Publicly"
6. Link copied to clipboard!
7. Open link in new tab (can be anonymous)
8. Should see public view page with MIDI player

#### Test Public Gallery:

1. Open `http://localhost:3000/gallery`
2. Should see your shared pattern
3. Click on it to view details
4. Try sorting (Recent/Popular/Trending)
5. Try filters (Type/Style)

#### Test Voting:

1. Open a shared generation page
2. Click 👍 Upvote button
3. Vote count should increase
4. Click 👎 Downvote button
5. Vote should change

#### Test Preset Marketplace:

1. Open `http://localhost:3000/presets`
2. No presets yet (marketplace empty)
3. Go back to main generator
4. Create custom preset (Ctrl+Shift+S)
5. Future: Add "Share Preset" button

---

## Troubleshooting

### Backend Issues

**Problem:** Tables not created
```bash
# Solution: Manually create tables
cd backend
python -c "from database import engine; from models import social; social.Base.metadata.create_all(bind=engine)"
```

**Problem:** 404 on /social/ endpoints
```bash
# Solution: Check main.py imports
# Should have:
from models import social
from routers import social as social_router
app.include_router(social_router.router)
```

**Problem:** Database errors
```bash
# Solution: Delete and recreate database
rm sql_app.db
python main.py  # Will recreate tables
```

### Frontend Issues

**Problem:** Share button not showing
- Check: Is there a current MIDI file? (Generate first)
- Check: Browser console for errors
- Solution: Clear browser cache

**Problem:** Gallery page 404
- Check: File exists at `frontend/app/gallery/page.tsx`
- Solution: Restart Next.js dev server

**Problem:** Share link not working
- Check: Backend is running
- Check: Network tab in browser DevTools
- Check: Share ID format (should be 12-16 chars)

**Problem:** Voting not working
- Check: User is logged in (check localStorage for 'token')
- Check: Network tab shows 401 error → Need to log in
- Solution: Log in first, then vote

---

## Quick Test Script

Copy and paste this into your browser console (on main generator page):

```javascript
// Quick test of share functionality
(async function testShare() {
  console.log('Testing social features...');

  // 1. Check if user is authenticated
  const token = localStorage.getItem('token');
  if (!token) {
    console.error('❌ Not logged in. Please log in first.');
    return;
  }
  console.log('✅ User authenticated');

  // 2. Check if MIDI file exists
  const midiUrl = document.querySelector('[class*="midiUrl"]');
  if (!midiUrl) {
    console.log('⚠️ No MIDI file yet. Generate a pattern first.');
  } else {
    console.log('✅ MIDI file ready');
  }

  // 3. Check if backend is running
  try {
    const response = await fetch('http://localhost:8000/social/generations?limit=1');
    if (response.ok) {
      console.log('✅ Backend /social endpoint working');
      const data = await response.json();
      console.log(`📊 Found ${data.length} shared generations`);
    } else {
      console.error('❌ Backend responded with error:', response.status);
    }
  } catch (err) {
    console.error('❌ Backend not reachable:', err.message);
  }

  console.log('Test complete!');
})();
```

---

## Feature Checklist

Use this to verify everything is working:

### Backend ✅
- [ ] Social tables created in database
- [ ] `/social/generations/share` endpoint working
- [ ] `/social/generations` (gallery) endpoint working
- [ ] `/social/presets` (marketplace) endpoint working
- [ ] Voting endpoints working
- [ ] Engagement tracking (play/download) working

### Frontend ✅
- [ ] Share button visible (after generation)
- [ ] Share modal opens
- [ ] Share link generated and copied
- [ ] Public view page loads (`/share/{shareId}`)
- [ ] MIDI player works on public page
- [ ] Gallery page loads (`/gallery`)
- [ ] Marketplace page loads (`/presets`)
- [ ] Navigation links in header work
- [ ] Voting buttons work (with login check)

### Integration ✅
- [ ] Can share a generation
- [ ] Can view shared generation (anonymous)
- [ ] Can vote on shared generation (logged in)
- [ ] Can browse gallery
- [ ] Can filter/sort gallery
- [ ] Can browse marketplace
- [ ] Can use marketplace preset
- [ ] Engagement counts increase

---

## Common Workflows

### Workflow 1: Share Your First Pattern

```
1. Log in
2. Generate pattern (e.g., Techno Drums, 128 BPM)
3. Click "🔗 Share"
4. Title: "My First Techno Kick"
5. Description: "Testing the share feature!"
6. Click "Share Publicly"
7. Copy link (auto-copied)
8. Open in new incognito window
9. Verify pattern plays
10. Success! 🎉
```

### Workflow 2: Browse Community Patterns

```
1. Open /gallery
2. Sort by "Trending"
3. Filter by "Techno"
4. Click interesting pattern
5. Listen to MIDI
6. Upvote if you like it
7. Download MIDI file
8. Create your own variation
9. Share it back to gallery
10. Viral loop! 🔁
```

### Workflow 3: Use Marketplace Preset

```
1. Open /presets
2. Sort by "Trending"
3. Find preset you like
4. Click "✨ Use Preset"
5. Redirected to main generator
6. Open "🎨 My Presets"
7. See preset in list (marked "from marketplace")
8. Click to load
9. Generate pattern
10. Amazing results! ⭐
```

---

## API Examples

### Share a Generation

```bash
curl -X POST http://localhost:8000/social/generations/share \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Epic Techno Kick",
    "description": "Hard hitting kick pattern",
    "mode": "advanced",
    "type": "drums",
    "style": "techno",
    "bpm": 145,
    "key": "C",
    "scale": "minor",
    "density": 0.8,
    "complexity": 0.7,
    "groove": 0.3,
    "evolution": 0.4,
    "bars": 4,
    "midi_url": "/storage/midi_files/your_file.mid"
  }'
```

### Get Gallery

```bash
curl http://localhost:8000/social/generations?sort_by=trending&limit=10
```

### Get Marketplace

```bash
curl http://localhost:8000/social/presets?sort_by=popular&genre=techno
```

### Vote on Generation

```bash
curl -X POST http://localhost:8000/social/generations/SHARE_ID/vote \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"vote_type": "upvote"}'
```

---

## Environment Variables

No additional environment variables needed! Uses existing setup:

```env
# .env (backend)
DATABASE_URL=sqlite:///./sql_app.db
SECRET_KEY=your-secret-key-here-change-in-production
ALLOWED_ORIGINS=http://localhost:3000

# Frontend uses hardcoded localhost URLs
API_URL=http://localhost:8000  # (implicit in code)
```

---

## Database Inspection

View shared content in database:

```bash
sqlite3 sql_app.db

# View shared generations
SELECT id, title, style, bpm, upvotes, downvotes, view_count FROM shared_generations;

# View votes
SELECT g.title, u.email, v.vote_type
FROM generation_votes v
JOIN shared_generations g ON v.generation_id = g.id
JOIN users u ON v.user_id = u.id;

# View presets
SELECT id, name, genre, use_count, upvotes FROM shared_presets;

.quit
```

---

## Success! 🎉

If all checks pass, you're ready to use the social features!

**Try it yourself:**
1. Generate an amazing pattern
2. Share it with the world
3. Browse what others created
4. Vote on your favorites
5. Use cool presets from the marketplace

**Have fun creating music! 🎵**

---

**Setup Guide Version:** 1.0
**Last Updated:** 2025-12-28
**Status:** ✅ Ready to Use
