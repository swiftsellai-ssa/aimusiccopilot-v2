# 🎲 Smart Variations Testing Guide

Quick test checklist for the Smart Variations feature.

---

## Prerequisites

- ✅ Backend running on http://localhost:8000
- ✅ Frontend running on http://localhost:3000
- ✅ At least one project with tracks created

---

## Test 1: Open Variation Modal ✅

### Steps:
1. Navigate to any project with tracks
2. Find a track in the timeline
3. Click the "🎲 Variation" button (purple)

### Expected Result:
- ✅ Modal opens with dark gradient background
- ✅ Shows original track name and DNA parameters
- ✅ Strategy buttons visible (Subtle, Moderate, Extreme)
- ✅ "Preserve Feel" checkbox visible
- ✅ Cancel and Generate buttons visible

---

## Test 2: Strategy Selection ✅

### Steps:
1. In variation modal
2. Click "Subtle" button
3. Click "Moderate" button
4. Click "Extreme" button

### Expected Result:
- ✅ Clicked button highlights (changes background color)
- ✅ Only one strategy selected at a time
- ✅ Each shows different emoji and percentage range

---

## Test 3: Preserve Feel Toggle ✅

### Steps:
1. In variation modal
2. Click "Preserve Feel" checkbox ON
3. Click checkbox OFF

### Expected Result:
- ✅ Checkbox toggles between checked/unchecked
- ✅ No errors occur

---

## Test 4: Generate Subtle Variation ✅

### Steps:
1. Select a drums track (kick pattern)
2. Open variation modal
3. Select "Subtle" strategy
4. Enable "Preserve Feel"
5. Click "Generate Variation"

### Expected Result:
- ✅ Button shows "Generating..." during process
- ✅ Toast notification: "Variation DNA generated! (subtle strategy)"
- ✅ Toast notification: "Variation MIDI generated!"
- ✅ Toast notification: "Variation added to project!"
- ✅ Modal closes automatically
- ✅ New track appears in timeline: "{Original Name} (subtle)"
- ✅ New track has slightly different DNA parameters (~5-10% change)

### Verify:
- Compare original and variation DNA parameters
- They should be very similar (subtle changes only)

---

## Test 5: Generate Moderate Variation ✅

### Steps:
1. Select a bass track
2. Open variation modal
3. Select "Moderate" strategy
4. Disable "Preserve Feel"
5. Click "Generate Variation"

### Expected Result:
- ✅ New track: "{Original Name} (moderate)"
- ✅ DNA parameters differ by ~10-20%
- ✅ More noticeable differences than subtle

---

## Test 6: Generate Extreme Variation ✅

### Steps:
1. Select a melody track
2. Open variation modal
3. Select "Extreme" strategy
4. Disable "Preserve Feel"
5. Click "Generate Variation"

### Expected Result:
- ✅ New track: "{Original Name} (extreme)"
- ✅ DNA parameters differ by ~20-40%
- ✅ Dramatically different from original

---

## Test 7: Multiple Variations of Same Track ✅

### Steps:
1. Select one track
2. Generate "Subtle" variation
3. Select the SAME original track again
4. Generate "Moderate" variation
5. Select SAME original track again
6. Generate "Extreme" variation

### Expected Result:
- ✅ Project now has 4 tracks:
  - Original
  - {Name} (subtle)
  - {Name} (moderate)
  - {Name} (extreme)
- ✅ Each variation has different DNA parameters
- ✅ All are playable

---

## Test 8: Variation Chain (Variation of Variation) ✅

### Steps:
1. Generate a variation of Track A → Track B
2. Now generate a variation of Track B → Track C
3. Compare all three tracks

### Expected Result:
- ✅ Track C is based on Track B's parameters, not Track A
- ✅ Progressive evolution from A → B → C
- ✅ Each step shows cumulative changes

---

## Test 9: Playback Variations ✅

### Steps:
1. Generate 3 variations of a kick pattern
2. Play each one using the MIDI player
3. Listen to differences

### Expected Result:
- ✅ All variations play successfully
- ✅ Subtle variations sound very similar
- ✅ Moderate variations sound noticeably different
- ✅ Extreme variations sound dramatically different

---

## Test 10: Export with Variations ✅

### Steps:
1. Create project with:
   - Kick (original)
   - Kick (subtle)
   - Bass (original)
   - Bass (moderate)
2. Export multi-track MIDI
3. Download and open in DAW

### Expected Result:
- ✅ Export includes all tracks (4 tracks)
- ✅ Each track is separate in DAW
- ✅ Variations have different MIDI notes/patterns
- ✅ Can use variations for different song sections

---

## Test 11: Delete Variation ✅

### Steps:
1. Generate a variation
2. Click "Delete" on the variation track
3. Confirm deletion

### Expected Result:
- ✅ Variation deleted
- ✅ Original track remains
- ✅ No errors

---

## Test 12: Cancel Variation Modal ✅

### Steps:
1. Open variation modal
2. Select strategy and options
3. Click "Cancel" button

### Expected Result:
- ✅ Modal closes
- ✅ No variation generated
- ✅ No changes to project

---

## Test 13: Error Handling ✅

### Steps:
1. Disconnect backend (stop uvicorn)
2. Try to generate variation
3. Check error message

### Expected Result:
- ✅ Error toast appears
- ✅ Message indicates failure
- ✅ Modal doesn't close
- ✅ Can retry or cancel

---

## Test 14: Preserve Feel Comparison ✅

### Steps:
1. Generate "Moderate" variation WITH "Preserve Feel"
2. Note the groove and evolution values
3. Generate another "Moderate" variation WITHOUT "Preserve Feel"
4. Compare groove and evolution

### Expected Result:
- ✅ With Preserve Feel: Groove/Evolution change by ~2.5-5%
- ✅ Without Preserve Feel: Groove/Evolution change by ~10-20%
- ✅ Density/Complexity change similarly in both cases

---

## 🎯 Success Criteria

All tests should pass with these results:

- [x] Variation modal opens and displays correctly
- [x] All three strategies work (Subtle, Moderate, Extreme)
- [x] Preserve Feel affects groove/evolution mutations
- [x] Variations added as new tracks with correct naming
- [x] Can generate multiple variations of same track
- [x] Variation chains work (variation of variation)
- [x] All variations are playable
- [x] Variations export correctly in multi-track MIDI
- [x] Can delete variations
- [x] Error handling works gracefully
- [x] No console errors
- [x] No backend crashes

---

## 🐛 Found a Bug?

If you encounter issues:

1. **Check browser console** (F12 → Console)
2. **Check backend logs** (terminal running uvicorn)
3. **Note exact steps** to reproduce
4. **Share error details**:
   - Which strategy was selected?
   - Was "Preserve Feel" enabled?
   - What was the original track type?
   - Full error message

---

## 📊 Example Test Results

After testing, you should have a project that looks like:

```
Project: "Variation Test" (120 BPM, C minor)

Tracks:
1. Kick Pattern (original)          [Density: 70%, Complexity: 40%]
2. Kick Pattern (subtle)             [Density: 73%, Complexity: 42%]
3. Kick Pattern (moderate)           [Density: 82%, Complexity: 51%]
4. Kick Pattern (extreme)            [Density: 95%, Complexity: 65%]
5. Bass Line (original)              [Density: 60%, Complexity: 55%]
6. Bass Line (moderate)              [Density: 72%, Complexity: 42%]
7. Bass Line (moderate) (moderate)   [Density: 85%, Complexity: 38%]

Export: 7 tracks in Type 1 MIDI file
```

---

## ✅ After Testing

Once all tests pass:
1. Smart Variations feature is fully functional
2. Ready to use in real music production
3. Can create complex arrangements with variations
4. Export to DAW and finish tracks

**Happy Testing!** 🎲
