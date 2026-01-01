# Integrated MIDI Generator - Documentation

## Overview

The `IntegratedMidiGenerator` combines the basic `MidiGenerator` with the advanced `AdvancedPatternGenerator` and `HumanizationEngine` to provide a flexible, intelligent MIDI generation system.

## Recent Improvements (2025-12-27)

### High Priority Fixes

1. **Fixed Channel Assignment**
   - Drum instruments (kick, snare, hat, etc.) now correctly use MIDI channel 9
   - Melodic instruments (bass, melody, synth, etc.) use MIDI channel 0
   - Channel assignment is based on instrument type, not pitch range
   - See `_get_channel_for_instrument()` method

2. **Re-sorting After Humanization**
   - Events are now properly re-sorted after humanization applies timing variations
   - Prevents timing integrity issues in generated MIDI
   - Implemented in `_generate_with_dna()` at line 169

3. **Added Pitch to Events**
   - Advanced generator events now include pitch information
   - Proper pitch mapping for drum instruments using drum_map
   - Default pitch (middle C) for melodic instruments
   - See `_add_pitch_to_events()` method

4. **Fixed Delta Time Calculation**
   - Properly handles overlapping notes
   - Converts events to note_on/note_off pairs before sorting
   - Ensures all delta times are non-negative
   - See `_events_to_midi()` method (lines 271-350)

### Medium Priority Improvements

5. **Style/Instrument Validation**
   - Validates style against supported styles: techno, trap, house, dnb, lofi
   - Validates instrument type (drums vs. melodic)
   - Logs warnings for unsupported combinations
   - See `_validate_generation_params()` method

6. **Separated use_dna from Complexity**
   - `use_dna` parameter now independent of complexity threshold
   - Auto-detection based on style support in advanced generator
   - Can force DNA or basic generator explicitly
   - Low complexity patterns can still use DNA if desired

7. **Comprehensive Error Handling**
   - Try-catch blocks around generation logic
   - Validates event structure before MIDI conversion
   - Skips incomplete events with warnings
   - Raises `ValueError` with clear messages on failure

8. **Complete Documentation**
   - Docstrings for all methods
   - Event structure documented in class docstring
   - Parameter descriptions for all methods
   - Units clearly specified (beats, ticks, BPM)

### Low Priority Enhancements

9. **Configurable Humanization**
   - Humanization can be enabled/disabled at initialization
   - Per-call override with `humanize` parameter
   - Default: enabled

10. **Logging Support**
    - Logs generation routing decisions (INFO level)
    - Logs DNA parameters (DEBUG level)
    - Logs warnings for validation issues
    - Logs errors with full stack traces

11. **Comprehensive Unit Tests**
    - 20+ test cases covering all functionality
    - Tests for channel assignment, timing, validation
    - Tests for DNA integration and humanization
    - Mock-based tests for component integration
    - See `test_integrated_midi_generator.py`

## Usage

### Basic Usage

```python
from services.integrated_midi_generator import IntegratedMidiGenerator

# Create generator
generator = IntegratedMidiGenerator(enable_humanization=True)

# Generate techno kick pattern
midi_file = generator.generate(
    description="dark techno kick",
    style="techno",
    instrument="kick",
    bpm=130,
    bars=4
)

# Save the file
midi_file.save("output.mid")
```

### Advanced Usage with DNA

```python
# Explicitly use DNA-based generation
midi_file = generator.generate(
    description="complex trap hi-hats",
    use_dna=True,
    style="trap",
    instrument="hat",
    density=0.9,
    complexity=0.8,
    groove=0.3,
    velocity_curve='exponential',
    evolution=0.4,
    bpm=140,
    bars=8
)
```

### Disabling Humanization

```python
# Per-call disable
midi_file = generator.generate(
    description="quantized techno",
    humanize=False,
    style="techno"
)

# Or disable by default
generator = IntegratedMidiGenerator(enable_humanization=False)
```

## Event Structure

Events are dictionaries with the following required keys:

```python
{
    'time': float,      # Time in beats (quarter notes) from start
    'velocity': int,    # MIDI velocity (1-127)
    'duration': float,  # Note duration in beats
    'pitch': int,       # MIDI note number (0-127)
    'channel': int      # MIDI channel (0-15, where 9 = drums)
}
```

### Time Units

- **Beats**: Quarter notes. A 4/4 bar = 4 beats
- **Ticks**: MIDI resolution. Default = 480 ticks per beat
- **BPM**: Beats (quarter notes) per minute

## Supported Styles

- **techno**: 4-on-floor kicks, driving rhythm
- **trap**: Half-time snares, rolling hi-hats
- **house**: Groovy 4/4 patterns
- **dnb**: Fast breakbeats (174 BPM)
- **lofi**: Relaxed, sparse patterns

## Supported Instruments

### Drum Instruments (Channel 9)
- drums, drum, full_drums, percussion
- kick, snare, hat, hats, hihat
- clap, rim, crash, ride, tom

### Melodic Instruments (Channel 0)
- bass, sub, 808
- melody, lead, synth

## Architecture

```
IntegratedMidiGenerator
├── MidiGenerator (basic patterns)
├── AdvancedPatternGenerator (DNA-based)
└── HumanizationEngine (timing/velocity variation)
```

### Generation Flow

1. **Parameter Validation**
   - Validate style/instrument combination
   - Determine MIDI channel
   - Auto-detect DNA usage if not specified

2. **Pattern Generation**
   - Route to DNA generator or basic generator
   - Generate events with proper pitch/channel

3. **Humanization** (optional)
   - Apply timing and velocity variations
   - Re-sort events to maintain timing integrity

4. **MIDI Conversion**
   - Convert events to note_on/note_off messages
   - Sort messages by absolute time
   - Calculate delta times
   - Create MidiFile

## Testing

Run tests from the backend directory:

```bash
cd backend
python test_runner.py
```

Or run specific test classes:

```bash
python -m unittest services.test_integrated_midi_generator.TestIntegratedMidiGenerator -v
```

## Error Handling

All public methods include error handling:

- **ValueError**: Invalid parameters or generation failure
- **Warnings**: Logged for unsupported styles, incomplete events
- **Debug logs**: Available for troubleshooting generation routing

Enable logging to see detailed information:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Performance Considerations

- DNA generation is more CPU-intensive than basic generation
- Humanization adds minimal overhead
- MIDI file size grows with event count and duration
- Consider using basic generator for real-time or low-latency needs

## Future Improvements

Potential enhancements:
- Support for more styles (ambient, dubstep, etc.)
- Polyphonic melodic generation
- Multi-track generation in single MIDI file
- MIDI CC support (automation)
- Pattern variation and arrangement
- Export to other formats (MusicXML, audio)
