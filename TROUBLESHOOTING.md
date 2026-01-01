# 🔧 Troubleshooting Guide - AI Music Copilot

## Common Issues and Solutions

---

### 1. 401 Unauthorized Error When Sharing

**Symptoms:**
- Click Share button
- Error: "Failed to share generation"
- Console shows: `401 (Unauthorized)`

**Root Cause:**
- JWT authentication token expired or invalid
- Token wasn't saved properly
- Backend was restarted with different SECRET_KEY

**Solution:**

**Option A: Log Out and Back In (Recommended)**
```
1. Click "Logout" button in header
2. Log in again with your credentials
3. Generate a new pattern
4. Try sharing again
```

**Option B: Clear Browser Storage**
```
1. Open DevTools (F12)
2. Application → Local Storage → http://localhost:3000
3. Delete the "token" key
4. Refresh page
5. Log in again
```

**Option C: Check Backend Logs**
```bash
# If backend shows JWT errors, restart it:
cd backend
# Stop with Ctrl+C
uvicorn main:app --reload
```

---

### 2. MIDI Player RangeError

**Symptoms:**
- Error: `RangeError: Value must be within [0, Infinity], got: -2.7284841053187847e-12`
- MIDI player crashes
- Error boundary catches the error

**Root Cause:**
- Tone.js Transport timing issue
- Negative time value when stopping playback
- Race condition in cleanup

**Solution:**

✅ **Already Fixed** in latest code update!

The MidiPlayer component now has:
- Try-catch blocks around Tone.js operations
- Proper cleanup order (stop parts before transport)
- Error handling for edge cases

**If issue persists:**
```
1. Refresh the frontend page (to load updated code)
2. Generate a new pattern
3. If still crashes, check browser console for new errors
```

---

### 3. 404 File Not Found (MIDI Files)

**Symptoms:**
- MIDI player shows: "Failed to load MIDI file"
- Console: `404 (Not Found)` for MIDI file URL
- URL shows old filename format

**Root Cause:**
- Old MIDI files from before integrated generator was set up
- Files saved to wrong directory
- Storage directory was cleared

**Solution:**

```
1. Generate a NEW pattern (don't reload old ones)
2. Old patterns in history won't work
3. New patterns will be saved to correct location
```

**To clear old history:**
```javascript
// In browser console:
localStorage.removeItem('generationHistory');
location.reload();
```

---

### 4. Share Button Disabled/Not Showing

**Symptoms:**
- Share button grayed out
- Can't click Share button
- Button missing entirely

**Root Cause:**
- No current MIDI file loaded
- Haven't generated a pattern yet
- Component not fully loaded

**Solution:**

```
1. Generate a pattern first (any type)
2. Wait for MIDI player to appear
3. Share button should become active
4. If still disabled, check:
   - currentMidiUrl is set (check React DevTools)
   - isAuthenticated is true
```

---

### 5. Gallery/Marketplace Shows Empty

**Symptoms:**
- Gallery page shows "No patterns found"
- Marketplace shows "No presets found"
- Everything appears empty

**Root Cause:**
- No content shared yet (expected on first use)
- Database tables empty
- Backend not connected

**Solution:**

**Expected Behavior:**
- Gallery/Marketplace will be empty until users share content

**To Add Content:**
```
1. Generate a pattern
2. Click Share button
3. Share it publicly
4. Visit gallery - should see your pattern
```

**If backend issue:**
```bash
# Check backend logs for errors
cd backend
python test_social_setup.py
# Should show 0 shared generations (normal if nothing shared yet)
```

---

### 6. CORS Errors

**Symptoms:**
- Console: "Access to XMLHttpRequest... has been blocked by CORS policy"
- "No 'Access-Control-Allow-Origin' header"
- Requests fail with network errors

**Root Cause:**
- Backend not running
- CORS middleware not configured
- Wrong backend URL

**Solution:**

**Check Backend is Running:**
```bash
cd backend
# Should see:
# INFO: Application startup complete.
# INFO: Uvicorn running on http://127.0.0.1:8000
```

**Verify CORS Configuration:**
```python
# In backend/main.py, should have:
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Disposition"],
)
```

**If still issues:**
```bash
# Restart backend
cd backend
# Ctrl+C to stop
uvicorn main:app --reload
```

---

### 7. Database Table Missing Errors

**Symptoms:**
- Backend logs: `sqlite3.OperationalError: no such table: shared_generations`
- Social endpoints return 500 errors
- API calls fail

**Root Cause:**
- Social tables not created
- Database file deleted
- Migration didn't run

**Solution:**

**Auto-create tables:**
```bash
cd backend
# Tables should auto-create on startup
uvicorn main:app --reload
# Check logs for: "Creating tables..."
```

**Manual table creation:**
```bash
cd backend
python -c "from database import engine; from models import social; social.Base.metadata.create_all(bind=engine)"
```

**Verify tables exist:**
```bash
sqlite3 sql_app.db
.tables
# Should show: shared_generations, generation_votes, shared_presets, preset_votes
.quit
```

---

### 8. Share Link Not Working

**Symptoms:**
- Share link created successfully
- Opening link shows 404 or error
- Public page doesn't load

**Root Cause:**
- Share ID not in database
- Backend not serving static files
- Route not configured

**Solution:**

**Check backend logs:**
```bash
# Should see POST request succeed:
# INFO: "POST /social/generations/share HTTP/1.1" 200 OK
```

**Test share link manually:**
```bash
# Get the share_id from the URL
curl http://localhost:8000/social/generations/SHARE_ID
# Should return generation data
```

**If 404:**
```
1. Check share ID is correct (alphanumeric, 12-16 chars)
2. Verify backend has the generation in database
3. Check route is registered in main.py
```

---

### 9. Vote Buttons Not Working

**Symptoms:**
- Click upvote/downvote
- Nothing happens
- Error in console

**Root Cause:**
- Not logged in
- Invalid token
- Backend issue

**Solution:**

**Check authentication:**
```javascript
// In browser console:
localStorage.getItem('token')
// Should return a long string (JWT token)
// If null, log in first
```

**Log in and try again:**
```
1. Make sure you're logged in
2. Click upvote/downvote
3. Should see toast notification
4. Count should update
```

---

### 10. Frontend Build Errors

**Symptoms:**
- `npm run dev` fails
- TypeScript errors
- Module not found errors

**Root Cause:**
- Missing dependencies
- TypeScript configuration issue
- Cache corruption

**Solution:**

**Clear cache and reinstall:**
```bash
cd frontend
rm -rf node_modules .next
npm install
npm run dev
```

**If TypeScript errors:**
```bash
# Check all imports are correct
# Verify @/ alias is configured in tsconfig.json
```

---

## Quick Diagnostic Checklist

### Backend Health Check ✅

```bash
cd backend
python test_social_setup.py
```

Should show:
- ✅ Backend is running
- ✅ Found X social endpoints
- ✅ Gallery endpoint working (0 shared generations)
- ✅ Marketplace endpoint working (0 shared presets)

### Frontend Health Check ✅

```
1. Open http://localhost:3000
2. Check browser console for errors
3. Can log in? ✓
4. Can generate pattern? ✓
5. MIDI player works? ✓
6. Share button enabled? ✓
```

### Database Health Check ✅

```bash
cd backend
sqlite3 sql_app.db
.tables
# Should show all tables including:
# - shared_generations
# - generation_votes
# - shared_presets
# - preset_votes
.quit
```

---

## Getting Help

### Enable Debug Mode

**Backend:**
```bash
# In terminal
export LOG_LEVEL=DEBUG
uvicorn main:app --reload --log-level debug
```

**Frontend:**
```javascript
// In browser console
localStorage.setItem('debug', 'true');
location.reload();
```

### Useful Browser Console Commands

```javascript
// Check authentication
console.log('Token:', localStorage.getItem('token'));
console.log('Authenticated:', !!localStorage.getItem('token'));

// Check history
console.log('History:', JSON.parse(localStorage.getItem('generationHistory') || '[]'));

// Check presets
console.log('Presets:', JSON.parse(localStorage.getItem('customPresets') || '[]'));

// Clear all data (fresh start)
localStorage.clear();
location.reload();
```

### Check API Endpoints

```bash
# View API documentation
open http://localhost:8000/docs

# Test endpoint manually
curl http://localhost:8000/social/generations
curl http://localhost:8000/social/presets
```

---

## Reset Everything (Nuclear Option)

If nothing works, start fresh:

```bash
# 1. Stop both frontend and backend (Ctrl+C)

# 2. Clear backend database
cd backend
rm sql_app.db

# 3. Clear frontend cache
cd ../frontend
rm -rf .next node_modules
npm install

# 4. Start backend
cd ../backend
uvicorn main:app --reload

# 5. Start frontend (new terminal)
cd ../frontend
npm run dev

# 6. Clear browser data
# - Open DevTools (F12)
# - Application → Clear Storage → Clear site data
# - Reload page

# 7. Create new account and test
```

---

## Still Having Issues?

1. **Check the logs** - Both backend terminal and browser console
2. **Read error messages carefully** - They usually tell you what's wrong
3. **Try the examples** - Use the test scripts provided
4. **Start fresh** - Clear cache, logout/login, regenerate patterns
5. **Verify setup** - Run `test_social_setup.py` to check backend

---

**Last Updated:** 2025-12-28
**Version:** 1.0
