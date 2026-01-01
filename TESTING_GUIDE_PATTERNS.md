# Pattern Generation Testing Guide

This document outlines the testing strategy for the Pattern Generation module of the AI Music Copilot. It covers the verification of genre templates, melodic generation, variation logic, and density algorithms.

## 1. Test Scope

The following features require verification:
*   **Genre Templates**: House, DnB, LoFi (Kick, Bass, Hat, Snare).
*   **Melodic Generation**: Bass and Melody line generation.
*   **Algorithms**: Pattern variation selection and Density adjustments.

## 2. Unit Testing Strategy

These tests should be automated (using `pytest` for Python or `Jest` for JS/TS) to verify the structural integrity of the generated patterns.

### 2.1 Genre Template Verification

For each genre, verify that the generated pattern contains the correct instruments and adheres to the fundamental rhythmic rules of the genre.

| Genre | Instrument | Assertion Criteria |
| :--- | :--- | :--- |
| **House** | Kick | **4-on-the-floor**: Events present at steps 0, 4, 8, 12 (assuming 16-step grid). |
| **House** | Hat | **Off-beat**: Events present at steps 2, 6, 10, 14 (open hats) or 16th note shuffle. |
| **DnB** | Kick/Snare | **Breakbeat**: Kick at step 0, Snare around step 4 and 12. Tempo check (if applicable). |
| **LoFi** | General | **Velocity/Timing**: Check for "humanization" (micro-timing offsets) or lower velocity ranges. |

**Example Test Case (Pseudocode):**
```python
def test_house_kick_pattern():
    pattern = generate_pattern(genre="HOUSE", instrument="KICK")
    assert pattern.length == 16
    # Check for kicks on downbeats
    assert pattern.has_event_at(0)
    assert pattern.has_event_at(4)
    assert pattern.has_event_at(8)
    assert pattern.has_event_at(12)
```

### 2.2 Melodic Generation

Verify that melodic lines adhere to musical constraints.

*   **Scale Adherence**: Ensure all generated notes belong to the requested Key/Scale (e.g., C Minor).
*   **Range**: Ensure Bass notes stay within low frequency MIDI ranges (e.g., MIDI 24-48) and Melody within higher ranges.
*   **Monophony**: If the generator is monophonic (basslines), ensure no two notes overlap at the same start time.

## 3. Algorithm Verification

### 3.1 Density Algorithm

The density parameter controls how "busy" a pattern is.

*   **Test**: Generate patterns with Density `0.2`, `0.5`, and `0.8`.
*   **Assertion**: `Count(Events_0.8) > Count(Events_0.5) > Count(Events_0.2)`.
*   **Edge Cases**:
    *   Density `0.0`: Should return silence or minimal viable pattern (e.g., just the '1').
    *   Density `1.0`: Should not exceed grid resolution (no overlapping notes that cause audio artifacts).

### 3.2 Pattern Variation Logic

Verify that the variation logic produces distinct but related patterns.

*   **Uniqueness**: `generate_variation(seed_pattern)` should not equal `seed_pattern`.
*   **Consistency**: The variation should maintain the same Genre and Kit as the seed.
*   **Determinism**: If a seed is provided, the output should be reproducible (if designed to be deterministic).

## 4. Musicality & Manual Testing Checklist

Since "musicality" is subjective, use this checklist for manual review sessions.

### Setup
*   Load the application.
*   Select a BPM appropriate for the genre (e.g., 120 for House, 174 for DnB, 85 for LoFi).

### Checklist

- [ ] **House Template**: Does the groove feel steady? Are the hi-hats interacting well with the kick?
- [ ] **DnB Template**: Does the kick/snare interplay create the expected "rolling" feel?
- [ ] **LoFi Template**: Is the swing perceptible? Does it feel relaxed rather than robotic?
- [ ] **Melody/Bass Integration**:
    - Generate a Bass line.
    - Generate a Melody.
    - **Check**: Do they clash? (e.g., dissonant intervals on strong beats).
- [ ] **Density Check**:
    - Start at low density.
    - Slowly increase to max.
    - **Check**: Does the pattern evolve naturally, or does it just become random noise?
- [ ] **Variation**:
    - Create a pattern you like.
    - Click "Variate".
    - **Check**: Is the new pattern usable as a B-section or fill?

## 5. Automated Integration Tests

Create a script that runs a full generation cycle to ensure no crashes occur during complex requests.

```javascript
// Example Integration Test
test('Full Band Generation', async () => {
    const session = new MusicSession();
    await session.addTrack('Drums', { genre: 'DNB' });
    await session.addTrack('Bass', { genre: 'DNB', density: 0.7 });
    
    const result = await session.generateAll();
    
    expect(result.tracks.length).toBe(2);
    expect(result.tracks[0].clips.length).toBeGreaterThan(0);
});
```