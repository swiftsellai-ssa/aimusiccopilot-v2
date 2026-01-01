# 🧪 Multi-Track Projects Testing Guide

Follow these steps to test the complete multi-track workflow.

## Prerequisites

- ✅ Backend running on http://localhost:8000
- ✅ Frontend running on http://localhost:3000
- ✅ Logged in with a user account

---

## Test 1: Create a Project ✅

### Steps:
1. Navigate to http://localhost:3000/projects
2. Click "**+ New Project**" button
3. Fill in the form:
   - **Name**: "Test Techno Track"
   - **Description**: "Testing multi-track export"
   - **BPM**: 140
   - **Key**: C
   - **Scale**: minor
4. Click "**Create Project**"

### Expected Result:
- ✅ Modal closes
- ✅ Redirects to project editor page `/projects/{id}`
- ✅ Shows empty project with 0 tracks
- ✅ Project info displays: 140 BPM, C minor, 0 tracks

### If it fails:
- Check browser console for errors
- Check backend terminal for errors
- Verify you're logged in (check localStorage for 'token')

---

## Test 2: Generate and Add Drums ✅

### Steps:
1. Click "**← Back to Generator**" or navigate to http://localhost:3000
2. Switch to "**🧬 DNA Mode**"
3. Set parameters:
   - Type: **Drums**
   - Style: **Techno**
   - BPM: **140**
   - DNA Density: **80%**
   - DNA Complexity: **40%**
   - Bars: **4**
4. Click "**🎵 Generate Pattern**"
5. Wait for generation (~2-3 seconds)
6. Click "**🎼 Add to Project**" button
7. In modal:
   - Track Name: "Kick Pattern"
   - Select your "Test Techno Track" project
8. Click "**Add Track**"

### Expected Result:
- ✅ Success toast: "Track added to project!"
- ✅ Confirmation dialog: "Track added! View project?"
- ✅ Click "OK" → Redirects to project editor
- ✅ Shows 1 track in timeline
- ✅ Track displays: name, type (drums), DNA parameters

### If it fails:
- Check if MIDI file was generated (should have URL)
- Verify project exists in `/projects` page
- Check network tab for API errors

---

## Test 3: Add Bass Track ✅

### Steps:
1. From project editor, click "**+ Add Track**" button (or go to main generator)
2. Generate bass pattern:
   - Type: **Bass**
   - Style: **Techno**
   - BPM: **140** (keep same!)
   - DNA Density: **70%**
   - DNA Complexity: **60%**
   - Bars: **4**
3. Click "**🎵 Generate Pattern**"
4. Click "**🎼 Add to Project**"
5. Track Name: "Bass Line"
6. Select same project
7. Click "**Add Track**"

### Expected Result:
- ✅ Project now shows 2 tracks
- ✅ Tracks are ordered (Kick Pattern, Bass Line)
- ✅ Each track has different colored icon (red for drums, blue for bass)

---

## Test 4: Add Melody Track ✅

### Steps:
1. Generate melody pattern:
   - Type: **Melody**
   - Style: **Techno**
   - BPM: **140**
   - Key: **C**
   - Scale: **minor**
   - DNA Density: **50%**
   - DNA Complexity: **70%**
   - Bars: **4**
2. Click "**🎵 Generate Pattern**"
3. Click "**🎼 Add to Project**"
4. Track Name: "Lead Synth"
5. Add to same project

### Expected Result:
- ✅ Project now shows 3 tracks
- ✅ All tracks visible in timeline
- ✅ Melody track has green icon

---

## Test 5: Mixer Controls ✅

### Steps:
1. Open project editor with 3 tracks
2. For **Kick Pattern** track:
   - Adjust **Volume** slider to **100%**
   - Adjust **Pan** to **Center** (50%)
   - Leave **Mute** OFF (gray)
3. For **Bass Line** track:
   - Adjust **Volume** to **85%**
   - Adjust **Pan** to **Slight Left** (40%)
4. For **Lead Synth** track:
   - Adjust **Volume** to **75%**
   - Adjust **Pan** to **Slight Right** (60%)
5. Click **Mute** button on Bass Line (should turn red)

### Expected Result:
- ✅ Sliders move smoothly
- ✅ Values update in real-time
- ✅ Pan shows "L", "C", or "R" indicator
- ✅ Mute button turns red when active
- ✅ Changes persist (refresh page → settings saved)

### To verify persistence:
- Refresh the page (F5)
- Check that all mixer settings are maintained

---

## Test 6: MIDI Playback (Individual Tracks) ✅

### Steps:
1. In project editor, find the **MIDI player** for each track
2. Click **▶️ Play** button on Kick Pattern
3. Listen to the pattern play
4. Click **⏸️ Pause** to stop
5. Repeat for Bass Line and Lead Synth

### Expected Result:
- ✅ Each track plays its MIDI pattern
- ✅ Sound is synthesized using Tone.js
- ✅ Playback is smooth without glitches
- ✅ Can pause and resume

### If sound doesn't play:
- Check browser console for Tone.js errors
- Try clicking anywhere on page first (browsers require user interaction for audio)
- Check browser volume settings

---

## Test 7: Export Multi-Track MIDI ✅

### Steps:
1. With all 3 tracks in project
2. **Unmute** all tracks (all Mute buttons should be gray)
3. Click "**💾 Export Multi-Track MIDI**" button
4. Wait for export process (1-3 seconds)

### Expected Result:
- ✅ Green success message appears
- ✅ Shows: "Multi-track MIDI exported! (3 tracks)"
- ✅ Export panel appears with:
   - "Multi-Track MIDI Ready!"
   - File info: "3 tracks merged into Type 1 MIDI file"
   - **⬇️ Download** button
   - **▶️ Play** button for preview

### If export fails:
- Check backend terminal for errors
- Verify `backend/storage/exports/` directory exists
- Check that all tracks have valid MIDI files

---

## Test 8: Download and Verify MIDI File ✅

### Steps:
1. Click "**⬇️ Download**" button on export panel
2. MIDI file downloads to your Downloads folder
3. Locate file: `project_1_Test_Techno_Track.mid`
4. **Import into DAW** (Ableton, FL Studio, Logic, etc.)

### Expected Result in DAW:
- ✅ File opens as multi-track MIDI
- ✅ Shows **4 tracks total**:
   - Track 0: "Conductor" (empty, just tempo/time sig)
   - Track 1: "Kick Pattern" (MIDI notes)
   - Track 2: "Bass Line" (MIDI notes)
   - Track 3: "Lead Synth" (MIDI notes)
- ✅ Tempo is **140 BPM**
- ✅ Time signature is **4/4**
- ✅ All tracks are **4 bars long**
- ✅ Volume levels match mixer settings
- ✅ Pan settings match mixer settings

### DAW-Specific Checks:

**Ableton Live:**
```
- Each track loads into separate MIDI track
- Notes are in correct positions
- Tempo is 140 BPM
- Can play back immediately
```

**FL Studio:**
```
- Tracks appear in Piano Roll
- Each track on separate channel
- Notes quantized correctly
```

**Logic Pro:**
```
- Multi-track region appears
- Each track on separate instrument
- Tempo and time sig correct
```

---

## Test 9: Mute Track and Re-Export ✅

### Steps:
1. Back in project editor
2. Click **Mute** button on Bass Line (should turn red)
3. Click "**💾 Export Multi-Track MIDI**" again
4. Download new file

### Expected Result:
- ✅ Export succeeds
- ✅ New MIDI file has **2 tracks** (Kick + Lead, no Bass)
- ✅ Muted track (Bass Line) is excluded from export
- ✅ In DAW: Only 2 music tracks (plus conductor track)

---

## Test 10: Delete Track ✅

### Steps:
1. In project editor
2. Click "**🗑️ Delete**" button on Lead Synth track
3. Confirm deletion dialog

### Expected Result:
- ✅ Confirmation dialog appears
- ✅ After confirm: track removed from timeline
- ✅ Project now shows 2 tracks (Kick + Bass)
- ✅ Refresh page → track still deleted (persisted)

---

## Test 11: Delete Project ✅

### Steps:
1. Navigate to http://localhost:3000/projects
2. Find your "Test Techno Track" project
3. Click "**🗑️**" button
4. Confirm deletion

### Expected Result:
- ✅ Confirmation dialog: "Are you sure you want to delete..."
- ✅ After confirm: project removed from list
- ✅ Refresh page → project still gone

---

## Test 12: Edge Cases ✅

### Test 12a: Empty Project Export
1. Create new project
2. Don't add any tracks
3. Try to click "Export" button

**Expected:** Button should be disabled OR show error "Add at least one track"

### Test 12b: Unmute Before Export
1. Create project with 1 track
2. Mute the track
3. Try to export

**Expected:** Should export successfully with 0 music tracks (just conductor), OR show warning

### Test 12c: Multiple Projects
1. Create 3 different projects
2. Add tracks to each
3. Navigate between projects

**Expected:** Each project maintains its own tracks, no mixing

### Test 12d: Volume Edge Cases
1. Set volume to 0%
2. Export
3. Check MIDI file

**Expected:** Track included but with CC 7 value = 0

---

## 🎯 Success Criteria

All tests should pass with these results:

- [x] Can create projects
- [x] Can add generated patterns as tracks
- [x] Can adjust mixer controls (volume, pan, mute)
- [x] Mixer settings persist after refresh
- [x] Can export multi-track MIDI
- [x] Exported MIDI opens correctly in DAW
- [x] Muted tracks excluded from export
- [x] Can delete tracks
- [x] Can delete projects
- [x] No console errors
- [x] No backend crashes

---

## 📊 Test Results Checklist

As you complete each test, mark it:

```
✅ Test 1: Create a Project
✅ Test 2: Generate and Add Drums
✅ Test 3: Add Bass Track
✅ Test 4: Add Melody Track
✅ Test 5: Mixer Controls
✅ Test 6: MIDI Playback
✅ Test 7: Export Multi-Track MIDI
✅ Test 8: Download and Verify in DAW
✅ Test 9: Mute Track and Re-Export
✅ Test 10: Delete Track
✅ Test 11: Delete Project
✅ Test 12: Edge Cases
```

---

## 🐛 Found a Bug?

If you encounter any issues:

1. **Note the exact steps** to reproduce
2. **Check browser console** (F12 → Console tab)
3. **Check backend logs** (terminal running uvicorn)
4. **Share the error** with details:
   - What you were doing
   - Error message
   - Expected vs actual behavior

---

## ✅ After Testing

Once all tests pass, you're ready to:
1. Use the multi-track feature for real music projects
2. Move on to **Smart Variations** implementation
3. Or implement **Project Sharing** features

**Happy Testing!** 🎵
