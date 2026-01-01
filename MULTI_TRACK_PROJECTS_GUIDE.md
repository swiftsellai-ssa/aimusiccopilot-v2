# 🎼 Multi-Track Projects Guide

Complete guide to using the multi-track projects feature in AI Music Copilot.

## Table of Contents

1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [Creating a Project](#creating-a-project)
4. [Adding Tracks](#adding-tracks)
5. [Mixer Controls](#mixer-controls)
6. [Exporting Multi-Track MIDI](#exporting-multi-track-midi)
7. [Track Variations](#track-variations)
8. [API Reference](#api-reference)
9. [Troubleshooting](#troubleshooting)

---

## Overview

Multi-track projects allow you to:
- **Combine multiple patterns** into one arrangement
- **Layer drums, bass, melody, chords, and FX** together
- **Mix each track** with volume, pan, mute, and solo controls
- **Export as Type 1 MIDI** file compatible with all DAWs
- **Create variations** of tracks with mutated DNA parameters
- **A/B test different versions** of the same track

### Feature Highlights

- ✅ Unlimited tracks per project
- ✅ Global project settings (BPM, key, scale)
- ✅ Per-track mixer controls (volume, pan, mute, solo)
- ✅ DNA parameter preservation for each track
- ✅ Multi-track MIDI export (Type 1 format)
- ✅ Track versioning for variations
- ✅ Visual timeline view
- ✅ Real-time MIDI playback

---

## Getting Started

### Prerequisites

1. **Backend running**: `cd backend && uvicorn main:app --reload`
2. **Frontend running**: `cd frontend && npm run dev`
3. **User account**: Create account and log in
4. **Generated patterns**: Create some drum, bass, or melody patterns first

### Quick Start Workflow

```
1. Log in to AI Music Copilot
2. Navigate to "🎼 Projects" in header
3. Click "+ New Project"
4. Enter project details (name, BPM, key, scale)
5. Go back to main generator
6. Generate a drum pattern
7. Click "🎼 Add to Project"
8. Select your project and enter track name
9. Generate bass, melody, etc. and add to same project
10. Open project to see all tracks in timeline
11. Adjust mixer settings (volume, pan, mute, solo)
12. Click "💾 Export Multi-Track MIDI"
13. Download and open in your DAW!
```

---

## Creating a Project

### From Projects Page

1. Navigate to [http://localhost:3000/projects](http://localhost:3000/projects)
2. Click "+ New Project" button
3. Fill in project details:
   - **Name**: Descriptive name (e.g., "Epic Techno Track")
   - **Description**: Optional details about the project
   - **BPM**: Tempo (60-200)
   - **Key**: Musical key (C, C#, D, etc.)
   - **Scale**: Scale type (major, minor, dorian, etc.)
4. Click "Create Project"

### Project Settings

All tracks in a project share these global settings:
- **BPM**: Sets playback tempo for all tracks
- **Key**: Musical key for harmonic consistency
- **Scale**: Scale mode for all melodic elements
- **Total Bars**: Project length (default: 8 bars)

You can update these settings later from the project editor.

---

## Adding Tracks

### Method 1: From Generator (Recommended)

1. **Generate a pattern** in main generator
2. Click "**🎼 Add to Project**" button
3. Enter **track name** (e.g., "Kick Pattern 1")
4. **Select project** from list
5. Click "**Add Track**"
6. Optionally navigate to project to see it

### Method 2: Direct Project Link

1. Open project editor: `/projects/{project_id}`
2. Click "+ Add Track" button
3. Redirects to main generator with project context
4. Generate pattern
5. Automatically added to project

### Track Properties

Each track stores:
- **Name**: Custom track name
- **Type**: drums, bass, melody, chords, fx
- **MIDI URL**: Path to generated MIDI file
- **DNA Parameters**: density, complexity, groove, evolution, bars
- **Mixer Settings**: volume, pan, muted, solo
- **Order Index**: Position in timeline

---

## Mixer Controls

### Volume

- **Range**: 0% to 100%
- **Default**: 80%
- **Controls**: Slider in track timeline
- **MIDI**: Mapped to CC 7 (Channel Volume)

```
Full Volume (100%) = MIDI value 127
Half Volume (50%) = MIDI value 64
Muted (0%) = MIDI value 0
```

### Pan

- **Range**: Full Left (0%) to Full Right (100%)
- **Default**: Center (50%)
- **Controls**: Slider in track timeline
- **MIDI**: Mapped to CC 10 (Pan)
- **Display**: Shows "L" (left), "C" (center), "R" (right)

```
Full Left (0%) = MIDI value 0
Center (50%) = MIDI value 64
Full Right (100%) = MIDI value 127
```

### Mute (M)

- **Function**: Silences track in export
- **Visual**: Red button when active
- **Effect**: Skips all note events for this track in MIDI export
- **Use Case**: Temporarily disable tracks while mixing

### Solo (S)

- **Function**: Listen to only this track (future feature)
- **Visual**: Yellow button when active
- **Current**: Stored in database, UI integration pending
- **Future**: Will mute all other tracks during playback

---

## Exporting Multi-Track MIDI

### Export Process

1. Open project with at least one track
2. Click "**💾 Export Multi-Track MIDI**"
3. Wait for export process (1-3 seconds)
4. Green success message appears
5. Click "**⬇️ Download**" button
6. MIDI file saves to your downloads folder

### MIDI File Format

- **Type**: MIDI Type 1 (multi-track)
- **Format**: `.mid` file
- **Tracks**:
  - Track 0: Conductor track (tempo, time signature)
  - Track 1-N: Your music tracks
- **Channels**: Each track assigned unique MIDI channel (1-16)
- **Resolution**: 480 ticks per beat (standard)

### Track 0 (Conductor Track)

```
Meta Events:
- Track Name: "Conductor"
- Set Tempo: BPM converted to microseconds per beat
- Time Signature: 4/4 (or project setting)
- End of Track marker
```

### Music Tracks (Track 1+)

```
Meta Events:
- Track Name: Your custom track name

Control Changes (at start):
- CC 7: Volume (0-127)
- CC 10: Pan (0-127)

Note Events:
- Note On/Off messages with velocity
- Timing preserved from original generation

Program Change:
- Instrument selection (if applicable)
```

### DAW Compatibility

Tested and working with:
- ✅ **Ableton Live** 11+
- ✅ **FL Studio** 20+
- ✅ **Logic Pro** X
- ✅ **Cubase** 12+
- ✅ **Reaper** 6+
- ✅ **Pro Tools** 2022+

All DAWs that support MIDI Type 1 format should work.

---

## Track Variations

### Creating Variations

Variations allow you to experiment with different DNA parameters while keeping the original track.

**Coming Soon!** The variation algorithm is currently in development.

### Planned Features

1. **Generate Variation**:
   - Click variation button on track
   - Algorithm mutates DNA parameters
   - Creates new version with subtle changes

2. **A/B Comparison**:
   - Compare original vs. variation
   - Listen to both side-by-side
   - Choose which version to keep

3. **DNA Mutation**:
   - **Density**: ±10-20% change
   - **Complexity**: ±10-20% change
   - **Groove**: ±5-15% change
   - **Evolution**: ±5-15% change

4. **Version Management**:
   - Track stores multiple versions
   - Switch between versions
   - Delete unwanted versions

---

## API Reference

### Endpoints

#### Create Project
```http
POST /api/projects
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "My Project",
  "description": "Optional description",
  "bpm": 120,
  "key": "C",
  "scale": "minor",
  "total_bars": 8
}

Response: ProjectResponse (201 Created)
```

#### List Projects
```http
GET /api/projects?limit=50&offset=0
Authorization: Bearer {token}

Response: ProjectResponse[] (200 OK)
```

#### Get Project
```http
GET /api/projects/{project_id}
Authorization: Bearer {token}

Response: ProjectResponse with tracks[] (200 OK)
```

#### Update Project
```http
PUT /api/projects/{project_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Updated Name",
  "bpm": 128,
  "is_public": false
}

Response: ProjectResponse (200 OK)
```

#### Delete Project
```http
DELETE /api/projects/{project_id}
Authorization: Bearer {token}

Response: 204 No Content
```

#### Add Track
```http
POST /api/projects/{project_id}/tracks
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Kick Pattern 1",
  "type": "drums",
  "midi_url": "/storage/midi_files/pattern.mid",
  "density": 0.8,
  "complexity": 0.7,
  "groove": 0.3,
  "evolution": 0.4,
  "bars": 4,
  "volume": 0.8,
  "pan": 0.5,
  "muted": false,
  "solo": false
}

Response: TrackResponse (201 Created)
```

#### Update Track
```http
PUT /api/projects/{project_id}/tracks/{track_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "volume": 0.6,
  "pan": 0.3,
  "muted": true
}

Response: TrackResponse (200 OK)
```

#### Delete Track
```http
DELETE /api/projects/{project_id}/tracks/{track_id}
Authorization: Bearer {token}

Response: 204 No Content
```

#### Export Project
```http
GET /api/projects/{project_id}/export
Authorization: Bearer {token}

Response: {
  "message": "Project exported successfully",
  "file_url": "/storage/exports/project_1_My_Project.mid",
  "track_count": 3
} (200 OK)
```

### Data Models

#### Project
```typescript
interface Project {
  id: number;
  user_id: number;
  name: string;
  description: string | null;
  bpm: number;
  key: string;
  scale: string;
  total_bars: number;
  is_public: boolean;
  created_at: string;
  updated_at: string;
  tracks: Track[];
}
```

#### Track
```typescript
interface Track {
  id: number;
  project_id: number;
  name: string;
  type: 'drums' | 'bass' | 'melody' | 'chords' | 'fx';
  midi_url: string;
  density: number;      // 0.0 - 1.0
  complexity: number;   // 0.0 - 1.0
  groove: number;       // 0.0 - 1.0
  evolution: number;    // 0.0 - 1.0
  bars: number;
  volume: number;       // 0.0 - 1.0
  pan: number;          // 0.0 - 1.0 (0.5 = center)
  muted: boolean;
  solo: boolean;
  order_index: number;
  created_at: string;
  updated_at: string;
}
```

---

## Troubleshooting

### Project won't export

**Problem**: "Project has no tracks to export" error

**Solution**:
1. Add at least one track to the project
2. Ensure tracks have valid MIDI files
3. Check that MIDI files exist in `backend/storage/midi_files/`

---

### Tracks not playing

**Problem**: Tracks added but no sound

**Solution**:
1. Check if track is muted (M button should be gray, not red)
2. Verify volume is above 0%
3. Try downloading MIDI and checking in DAW
4. Check browser console for errors

---

### Export file not downloading

**Problem**: Export succeeds but file won't download

**Solution**:
1. Check browser's download settings
2. Verify `backend/storage/exports/` directory exists
3. Check file permissions on exports folder
4. Try right-click → "Save Link As" on download button

---

### Tracks out of sync

**Problem**: Tracks don't line up in DAW

**Solution**:
1. All tracks use project BPM setting
2. Ensure you're importing at correct BPM in DAW
3. Check that all tracks start at bar 1
4. Verify DAW's MIDI import settings

---

### Can't add track to project

**Problem**: "Add to Project" button disabled

**Solution**:
1. Generate a pattern first
2. Ensure you're logged in
3. Create a project if you don't have one
4. Check browser console for errors

---

## Advanced Tips

### Best Practices

1. **Start with drums**: Build foundation first
2. **Match BPM**: Keep all patterns at same tempo
3. **Use proper types**: drums for percussion, bass for low end, etc.
4. **Mix as you go**: Adjust volume/pan while adding tracks
5. **Export often**: Save versions as you build

### Workflow Example

```
Project: "Techno Banger" (140 BPM, C minor)

Track 1: Kick Pattern (drums)
  - DNA: density 80%, complexity 30%
  - Mixer: volume 100%, pan center, NOT muted

Track 2: Hi-Hats (drums)
  - DNA: density 60%, complexity 50%
  - Mixer: volume 60%, pan slight right, NOT muted

Track 3: Bass Line (bass)
  - DNA: density 70%, complexity 60%
  - Mixer: volume 85%, pan center, NOT muted

Track 4: Lead Melody (melody)
  - DNA: density 50%, complexity 70%
  - Mixer: volume 75%, pan slight left, NOT muted

Export → Download → Import to Ableton → Add your own touches!
```

### Keyboard Shortcuts

In project editor:
- **M**: Toggle mute on selected track (coming soon)
- **S**: Toggle solo on selected track (coming soon)
- **Delete**: Delete selected track (coming soon)
- **Ctrl+E**: Export project (coming soon)

---

## What's Next?

### Upcoming Features

1. **Smart Variations** ⏳
   - AI-powered DNA mutation
   - A/B comparison UI
   - Version management

2. **Project Sharing** ⏳
   - Share projects publicly
   - Browse community projects
   - Remix others' projects

3. **Advanced Mixing** ⏳
   - Effects chains per track
   - Automation curves
   - Mastering tools

4. **Collaboration** 🔮
   - Multi-user projects
   - Real-time collaboration
   - Comments and feedback

---

## Need Help?

- **GitHub Issues**: [Report bugs here](https://github.com/your-repo/issues)
- **Documentation**: Check other guides in repo
- **Examples**: See `examples/` folder for sample projects

---

**Guide Version:** 1.0
**Last Updated:** 2025-12-28
**Status:** ✅ Core Features Complete, Variations In Progress
