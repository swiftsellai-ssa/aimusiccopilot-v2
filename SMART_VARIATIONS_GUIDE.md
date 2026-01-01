# 🎲 Smart Variations Feature Guide

## What Are Smart Variations?

Smart Variations use an intelligent DNA mutation algorithm to create related but different versions of your tracks. Instead of manually tweaking parameters, the variation engine automatically generates interesting alternatives while maintaining the essence of the original.

---

## How It Works

### 1. The Variation Engine

The backend variation engine ([variation_engine.py](backend/services/variation_engine.py)) intelligently mutates DNA parameters using three strategies:

- **Subtle** 🌱: 5-10% change - Minor tweaks for subtle differences
- **Moderate** ⚡: 10-20% change - Noticeable variations while preserving character
- **Extreme** 🔥: 20-40% change - Bold changes for dramatically different results

### 2. Preserve Feel Option

When enabled, this keeps **groove** and **evolution** parameters closer to the original (50% smaller mutations). This maintains the rhythmic feel while allowing density and complexity to vary more freely.

---

## Using Smart Variations

### Step 1: Open Your Project

Navigate to your project editor at `http://localhost:3000/projects/{id}`

### Step 2: Select a Track

Find the track you want to create a variation of in your timeline.

### Step 3: Click "🎲 Variation" Button

Each track has a purple "Variation" button in the actions column (right side).

### Step 4: Choose Strategy

The variation modal shows:
- **Original Track DNA**: Current density, complexity, groove, bars
- **Strategy Selection**: Choose Subtle, Moderate, or Extreme
- **Preserve Feel**: Toggle to maintain rhythmic character

### Step 5: Generate

Click "🎲 Generate Variation" and the system will:

1. **Mutate DNA Parameters** - Backend generates new parameters based on strategy
2. **Generate MIDI** - Creates new MIDI file with mutated parameters
3. **Add as New Track** - Adds variation to your project as a new track

The new track is named: `{Original Name} ({strategy})`

Example: `"Kick Pattern (moderate)"`

---

## Workflow Examples

### Example 1: Finding the Perfect Kick

```
1. Generate techno kick pattern
2. Add to project as "Kick"
3. Click "Variation" → Choose "Subtle"
4. Generate 2-3 subtle variations
5. A/B compare them all
6. Delete the ones you don't like
7. Export multi-track with your favorite
```

### Example 2: Progressive Build

```
1. Start with simple bass line (low density/complexity)
2. Generate "Moderate" variation → Slightly more complex
3. Generate "Moderate" variation of that → Even more complex
4. Now you have 3 versions for intro/verse/chorus
5. Arrange them in your DAW
```

### Example 3: Exploring Ideas

```
1. Generate melody with random parameters
2. Like the general vibe but not perfect?
3. Generate 5-10 "Extreme" variations
4. Keep the best ones
5. Each will be wildly different but related
```

---

## Technical Details

### DNA Parameter Mutation

The variation engine intelligently mutates parameters while respecting boundaries:

**Density** (0.0 - 1.0):
- Controls note density (sparse vs. busy)
- Can vary freely based on strategy

**Complexity** (0.0 - 1.0):
- Controls pattern complexity
- Can vary freely based on strategy

**Groove** (0.0 - 1.0):
- Controls rhythmic feel and swing
- Reduced mutation when "Preserve Feel" is enabled

**Evolution** (0.0 - 1.0):
- Controls how much patterns change over time
- Reduced mutation when "Preserve Feel" is enabled

**Bars** (1 - 16):
- Number of bars in the pattern
- Rarely changes (30% chance on moderate/extreme)
- Can double or halve the length

### Edge Avoidance

The engine avoids pushing parameters too close to 0.0 or 1.0, as extreme values often sound unmusical. If a mutation would push a parameter to the edge, it flips direction.

---

## API Endpoint

The variation generation uses this endpoint:

```
POST /api/projects/{project_id}/tracks/{track_id}/variations
```

**Request Body:**
```json
{
  "strategy": "moderate",      // "subtle" | "moderate" | "extreme"
  "preserve_feel": true,       // boolean
  "name": "My Variation"       // optional custom name
}
```

**Response:**
```json
{
  "id": 123,
  "name": "Variation 1",
  "density": 0.65,
  "complexity": 0.48,
  "groove": 0.52,
  "evolution": 0.35,
  "bars": 4,
  // ... other track fields
}
```

---

## Tips & Best Practices

### 1. Start Moderate
- Begin with "Moderate" strategy to get a feel for the variation engine
- Subtle might be too similar, Extreme might be too different

### 2. Use Preserve Feel for Drums
- Drums rely heavily on groove and timing
- Enable "Preserve Feel" to maintain rhythmic pocket

### 3. Go Extreme for Melodies
- Melodic elements benefit from bold changes
- Disable "Preserve Feel" to explore different melodic contours

### 4. Generate Multiple Variations
- Don't settle for the first variation
- Generate 3-5 variations and pick the best

### 5. Progressive Variations
- Use a variation as the base for another variation
- Create "variation chains" for gradual evolution

### 6. Clean Up as You Go
- Delete variations you don't like immediately
- Keeps your project timeline clean and organized

---

## Keyboard Shortcuts (Future)

Coming soon:
- `V` - Open variation modal for selected track
- `1`, `2`, `3` - Quick select Subtle/Moderate/Extreme
- `Enter` - Generate variation
- `Esc` - Close modal

---

## Troubleshooting

### Variation Sounds Too Similar
- Try "Extreme" strategy
- Disable "Preserve Feel"
- Generate multiple variations and pick the most different one

### Variation Sounds Too Different
- Try "Subtle" strategy
- Enable "Preserve Feel"
- Focus on single-parameter changes (density only, complexity only)

### Generation Failed
- Check backend terminal for errors
- Verify original track has valid DNA parameters
- Ensure MIDI generation service is running

---

## What's Next?

### Planned Enhancements

1. **A/B Comparison UI** - Play two tracks side-by-side
2. **Version History** - See all variations of a track
3. **Favorite Variations** - Mark best variations with stars
4. **Batch Generation** - Generate 5 variations at once
5. **Undo Variation** - Revert to previous version
6. **Parameter Locking** - Lock specific parameters from mutation
7. **Smart Suggestions** - AI recommends which strategy to use

---

## Example Session

```
Project: "Techno Banger" (140 BPM, C minor)

Tracks:
1. Kick Pattern (original)
2. Kick Pattern (subtle) ← Generated variation
3. Bass Line (original)
4. Bass Line (moderate) ← Generated variation
5. Bass Line (extreme) ← Generated variation
6. Lead Synth (original)
7. Lead Synth (moderate) ← Generated variation

Export multi-track MIDI → Import to Ableton
Arrange variations across intro/verse/chorus sections
Add effects and mixing
Final track complete! 🎉
```

---

## Summary

Smart Variations give you:
- ✅ Instant alternative versions of tracks
- ✅ Intelligent DNA parameter mutation
- ✅ Control over how different variations are
- ✅ Professional workflow for exploring ideas
- ✅ No manual parameter tweaking required

**Ready to explore?** Open any project, click the "🎲 Variation" button, and start creating!
