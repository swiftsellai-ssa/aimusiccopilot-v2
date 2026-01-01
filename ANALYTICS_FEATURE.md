# 📊 Analytics Feature - AI Music Copilot

## Overview

The Analytics feature automatically tracks user behavior and preferences to provide insights and recommendations. This helps users understand their creative patterns and discover new possibilities.

## What Gets Tracked

### Generation Events
Every MIDI generation is tracked with:
- **Mode**: Simple or Advanced (DNA)
- **Generation Type**: Drums, Bass, Melody, or Full Track
- **Style**: Techno, House, Trap, DnB, Lo-Fi
- **BPM**: Tempo setting
- **Musical Key & Scale**: Harmonic settings
- **DNA Parameters** (Advanced mode): Density, Complexity, Groove, Evolution, Bars
- **Success/Failure**: Whether generation succeeded
- **Generation Time**: How long it took to generate
- **User Interactions**: Downloads, plays, play duration

### User Sessions
- Session start/end times
- Total session duration
- Generations per session
- Downloads per session
- Plays per session

## Features

### 1. Analytics Dashboard

Access by clicking the **📊 Analytics** button in the top-right corner.

**Metrics Displayed:**
- **Total Generations**: How many MIDI patterns you've created
- **Success Rate**: Percentage of successful generations
- **Download Rate**: Percentage of generations you downloaded
- **Average BPM**: Your preferred tempo
- **Mode Usage**: Simple vs DNA Mode breakdown
- **Favorites**: Most popular type, style, key, and scale
- **DNA Averages** (if using Advanced mode): Average parameter values

### 2. Personalized Insights

The system analyzes your usage patterns and provides:

**Insights:**
- "You prefer Simple Mode (50 generations vs 10 in DNA Mode)"
- "Your favorite style is Techno (30 generations)"
- "Your average BPM is 128"
- "High download rate: 85% - you love almost everything you generate!"

**Recommendations:**
- "Try DNA Mode for more control over your patterns!"
- "Try exploring: House, Trap"
- "Experiment with extreme DNA parameter values for unique sounds"
- "Try lower density (0.3-0.5) for minimalist vibes"

### 3. Time Period Filtering

View analytics for different time periods:
- **7 days**: Recent trends
- **30 days**: Monthly overview (default)
- **90 days**: Long-term patterns

## Backend Implementation

### Database Models

**GenerationEvent** (`backend/models/analytics.py`)
```python
- id: Primary key
- user_id: Foreign key to User
- mode, generation_type, style, bpm, etc.
- DNA parameters (nullable)
- success, error_message, generation_time_ms
- was_downloaded, was_played, play_duration_seconds
- created_at, ip_address, user_agent
```

**UserSession** (`backend/models/analytics.py`)
```python
- id: Primary key
- user_id: Foreign key to User
- session_start, session_end, duration_seconds
- generations_count, downloads_count, plays_count
- ip_address, user_agent
```

**AnalyticsSummary** (`backend/models/analytics.py`)
```python
- Aggregated statistics for dashboard
- Period-based (daily, weekly, monthly)
- Pre-calculated metrics for fast loading
```

### API Endpoints

**Track Generation:**
```http
POST /api/analytics/track/generation
Authorization: Bearer {token}
Body: {
  mode, generation_type, style, bpm,
  musical_key, musical_scale,
  density, complexity, groove, evolution, bars,
  success, error_message, generation_time_ms
}
Response: { event_id, message }
```

**Track Interaction:**
```http
POST /api/analytics/track/interaction
Authorization: Bearer {token}
Body: {
  event_id, action, play_duration_seconds
}
Response: { message }
```

**Start Session:**
```http
POST /api/analytics/track/session/start
Authorization: Bearer {token}
Response: { session_id, message }
```

**End Session:**
```http
POST /api/analytics/track/session/end/{session_id}
Authorization: Bearer {token}
Response: { message }
```

**Get Summary:**
```http
GET /api/analytics/summary?days=30
Authorization: Bearer {token}
Response: AnalyticsResponse
```

**Get Insights:**
```http
GET /api/analytics/insights?days=30
Authorization: Bearer {token}
Response: { insights: [...], recommendations: [...] }
```

## Frontend Implementation

### Analytics Utility

**File:** `frontend/lib/analytics.ts`

**Usage:**
```typescript
import { analytics } from '@/lib/analytics';

// Start session (automatically on login)
await analytics.startSession();

// Track generation
const eventId = await analytics.trackGeneration({
  mode: 'advanced',
  generation_type: 'drums',
  style: 'techno',
  bpm: 128,
  density: 0.7,
  complexity: 0.5,
  success: true,
  generation_time_ms: 3500
});

// Track download
await analytics.trackDownload(eventId);

// Track play
await analytics.trackPlayStart(eventId);
await analytics.trackPlayStop(eventId); // Auto-calculates duration

// Get summary
const summary = await analytics.getSummary(30); // Last 30 days

// Get insights
const insights = await analytics.getInsights(30);

// End session (automatically on unmount)
await analytics.endSession();
```

### Analytics Dashboard Component

**File:** `frontend/components/AnalyticsDashboard.tsx`

**Features:**
- Overview stats (total generations, success rate, download rate, avg BPM)
- Mode usage breakdown with progress bars
- Favorites section (type, style, key, scale)
- DNA parameters averages (if using Advanced mode)
- Insights & recommendations

**Integration:**
```typescript
import AnalyticsDashboard from '@/components/AnalyticsDashboard';

<AnalyticsDashboard />
```

## Automatic Tracking

All tracking happens automatically:

1. **Session Tracking**: Starts when you login, ends when you logout or close the app
2. **Generation Tracking**: Fires when you click "Generate" (success or failure)
3. **Interaction Tracking**: Can be triggered manually (future enhancement)

## Privacy & Security

- ✅ All analytics data is **private** to each user
- ✅ Only authenticated users can access their own analytics
- ✅ IP address and user agent are stored for security (not displayed)
- ✅ No analytics data is shared between users
- ✅ Analytics are **optional** - you can ignore them if you want

## Database Setup

### Option 1: Automatic (Recommended)

The analytics tables are created automatically when you start the backend:

```bash
cd backend
python -m uvicorn main:app --reload
```

FastAPI will run `models.Base.metadata.create_all(bind=engine)` which creates all tables including analytics.

### Option 2: Manual Migration

If you need to manually create the tables:

```python
# backend/create_analytics_tables.py
from database import engine
from models.analytics import Base

Base.metadata.create_all(bind=engine)
print("Analytics tables created successfully!")
```

Run:
```bash
cd backend
python create_analytics_tables.py
```

## Usage Workflow

### For Users:

1. **Login** - Session tracking starts automatically
2. **Generate MIDI** - Generation event tracked automatically
3. **Play/Download** - Interactions tracked (future enhancement)
4. **View Analytics** - Click 📊 Analytics button
5. **Review Insights** - See personalized recommendations
6. **Adjust Workflow** - Try suggested styles, BPMs, or parameters

### For Developers:

1. **Backend Setup**:
   - Analytics router added to `main.py`
   - Models defined in `backend/models/analytics.py`
   - Endpoints in `backend/routers/analytics.py`

2. **Frontend Integration**:
   - Analytics utility in `frontend/lib/analytics.ts`
   - Dashboard component in `frontend/components/AnalyticsDashboard.tsx`
   - Integrated in `frontend/app/page.tsx`

3. **Tracking Points**:
   - Session start/end in `useEffect` hooks
   - Generation tracking in `handleGenerate`
   - Interaction tracking (future: in MidiPlayerWithAudio)

## Future Enhancements

### Phase 2:
- [ ] Track play events from MidiPlayerWithAudio
- [ ] Track download events from MidiPlayerWithAudio
- [ ] Export analytics as CSV/JSON
- [ ] Compare analytics across time periods
- [ ] Global leaderboards (opt-in)

### Phase 3:
- [ ] AI-powered pattern recommendations based on analytics
- [ ] "Generate similar to your favorites" feature
- [ ] Style transfer based on your preferred DNA parameters
- [ ] Collaborative filtering (users with similar tastes)

### Phase 4:
- [ ] Admin dashboard (aggregate analytics across all users)
- [ ] Popular patterns showcase
- [ ] Trending styles and BPMs
- [ ] Community features

## Testing Analytics

### Generate Test Data:

1. **Login** to your account
2. **Generate multiple patterns**:
   - Try different modes (Simple vs DNA)
   - Try different types (Drums, Bass, Melody, Full)
   - Try different styles (Techno, House, Trap, etc.)
   - Vary BPM (100-180)
3. **Click Analytics** button
4. **Review metrics**:
   - Check total generations count
   - Check mode breakdown
   - Check favorites
   - Read insights and recommendations
5. **Change time period** (7d, 30d, 90d)

### Verify Tracking:

**Backend logs:**
```bash
cd backend
python -m uvicorn main:app --reload
# Watch for "📊 Analytics..." logs in console
```

**Browser console:**
```javascript
// Open DevTools (F12)
// Check for analytics tracking logs:
// "📊 Analytics session started: 123"
// "📊 Generation tracked: 456"
// "📊 Interaction tracked: download"
```

**Database:**
```sql
-- Check generation events
SELECT * FROM generation_events ORDER BY created_at DESC LIMIT 10;

-- Check user sessions
SELECT * FROM user_sessions ORDER BY session_start DESC LIMIT 10;

-- Count by mode
SELECT mode, COUNT(*) FROM generation_events GROUP BY mode;

-- Count by type
SELECT generation_type, COUNT(*) FROM generation_events GROUP BY generation_type;

-- Average BPM
SELECT AVG(bpm) FROM generation_events;
```

## Troubleshooting

### Analytics dashboard not showing data

**Cause**: No generations yet or database tables not created

**Fix**:
1. Generate some MIDI patterns first
2. Check backend logs for errors
3. Verify analytics tables exist in database
4. Check browser console for API errors

### Tracking not working

**Cause**: Token expired or network error

**Fix**:
1. Logout and login again
2. Check browser console for errors
3. Verify backend is running
4. Check network tab for failed API calls

### Insights showing "Start generating..."

**Cause**: Not enough data yet

**Fix**:
- Generate at least 5-10 patterns
- Try different styles and modes
- Wait a bit, then refresh analytics

## Benefits

### For Users:
- 🎯 **Understand your style**: See what you create most
- 💡 **Get recommendations**: Discover new creative directions
- 📈 **Track progress**: Monitor your creative output
- 🎨 **Find patterns**: Identify your preferences
- 🚀 **Improve workflow**: Optimize based on insights

### For Product:
- 📊 **Usage metrics**: Understand user behavior
- 🎯 **Feature priorities**: What gets used most
- 🐛 **Error tracking**: Identify failure patterns
- 💰 **Conversion**: Track engagement and retention
- 🔮 **Product decisions**: Data-driven development

---

## Summary

The Analytics feature provides automatic tracking and insights for AI Music Copilot users. It helps you understand your creative patterns, discover new possibilities, and optimize your workflow - all while keeping your data private and secure.

**Key Points:**
- ✅ Automatic tracking (no manual work required)
- ✅ Private & secure (your data only)
- ✅ Actionable insights & recommendations
- ✅ Easy to use (one-click access)
- ✅ Fully integrated (backend + frontend)

**Start using it**: Click the 📊 Analytics button after generating some patterns!
