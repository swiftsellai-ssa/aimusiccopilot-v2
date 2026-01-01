# IntegratedMidiGenerator - Architecture

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    IntegratedMidiGenerator                       │
│                                                                   │
│  Responsibilities:                                               │
│  • Parameter validation                                          │
│  • Generation routing (DNA vs Basic)                             │
│  • Channel assignment (drums vs melodic)                         │
│  • Event enrichment (pitch, channel)                             │
│  • Humanization orchestration                                    │
│  • MIDI file conversion                                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ uses
                              ▼
        ┌─────────────────────────────────────────────┐
        │                                             │
        ▼                                             ▼
┌──────────────────┐                      ┌──────────────────────┐
│  MidiGenerator   │                      │ AdvancedPattern-     │
│     (Basic)      │                      │    Generator         │
│                  │                      │    (DNA-based)       │
│ • Style patterns │                      │ • PatternDNA         │
│ • Simple rhythm  │                      │ • Complexity         │
│ • Quick gen      │                      │ • Evolution          │
│ • Fallback       │                      │ • Ghost notes        │
└──────────────────┘                      └──────────────────────┘
        │                                             │
        │                                             │
        └─────────────────┬───────────────────────────┘
                          │ events
                          ▼
                ┌──────────────────────┐
                │ HumanizationEngine   │
                │                      │
                │ • Timing variance    │
                │ • Velocity variance  │
                │ • Micro-timing       │
                └──────────────────────┘
                          │
                          │ humanized events
                          ▼
                ┌──────────────────────┐
                │  MIDI Conversion     │
                │                      │
                │ • Event → Messages   │
                │ • Absolute → Delta   │
                │ • Overlapping notes  │
                └──────────────────────┘
                          │
                          ▼
                    ┌──────────┐
                    │ MidiFile │
                    └──────────┘
```

---

## Generation Flow

```
User Request
    │
    ▼
┌─────────────────────────────────────┐
│ 1. Parameter Extraction             │
│    • Parse description              │
│    • Detect/validate style          │
│    • Detect/validate instrument     │
│    • Extract DNA parameters         │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ 2. Validation                       │
│    • Check style support            │
│    • Check instrument type          │
│    • Validate parameter ranges      │
│    • Log warnings if needed         │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│ 3. Channel Assignment               │
│    • Drums → Channel 9              │
│    • Melodic → Channel 0            │
│    • Based on instrument semantics  │
└─────────────────────────────────────┘
    │
    ▼
    ┌─────────────┐
    │ use_dna?    │
    └─────────────┘
         │      │
     No  │      │ Yes
         │      │
         ▼      ▼
    ┌────────┐ ┌────────────────────┐
    │ Basic  │ │ DNA Generator      │
    │ Gen    │ │ • Create DNA       │
    │        │ │ • Generate events  │
    │        │ │ • Add pitch/chan   │
    └────────┘ └────────────────────┘
         │             │
         └──────┬──────┘
                │ events
                ▼
         ┌──────────────┐
         │ Humanize?    │
         └──────────────┘
                │
            Yes │ No
                │
                ▼
         ┌──────────────────┐
         │ Humanization     │
         │ • Time variance  │
         │ • Vel variance   │
         │ • Re-sort events │
         └──────────────────┘
                │
                ▼
         ┌──────────────────┐
         │ MIDI Conversion  │
         │ • Note on/off    │
         │ • Delta times    │
         │ • Sort messages  │
         └──────────────────┘
                │
                ▼
            MidiFile
```

---

## Event Data Structure

### Event Object (Internal)

```python
{
    'time': float,       # Absolute time in beats (quarter notes)
    'pitch': int,        # MIDI note number (0-127)
    'velocity': int,     # Note velocity (1-127)
    'duration': float,   # Note length in beats
    'channel': int,      # MIDI channel (0-15)
    'probability': float # Generation probability (metadata)
}
```

### MIDI Message (Output)

```python
mido.Message(
    type='note_on',     # or 'note_off'
    note=int,           # MIDI note (0-127)
    velocity=int,       # Velocity (0-127)
    time=int,           # Delta time in ticks
    channel=int         # MIDI channel (0-15)
)
```

---

## Class Hierarchy

```
IntegratedMidiGenerator
├── Properties
│   ├── DRUM_INSTRUMENTS (set)
│   ├── MELODIC_INSTRUMENTS (set)
│   ├── SUPPORTED_STYLES (set)
│   ├── basic_generator (MidiGenerator)
│   ├── advanced_generator (AdvancedPatternGenerator)
│   ├── humanizer (HumanizationEngine)
│   └── enable_humanization (bool)
│
├── Public Methods
│   ├── __init__(enable_humanization: bool)
│   └── generate(description, use_dna, humanize, **kwargs) → MidiFile
│
└── Private Methods
    ├── _generate_with_dna(...) → MidiFile
    ├── _validate_generation_params(style, instrument)
    ├── _get_channel_for_instrument(instrument) → int
    ├── _detect_style(description) → str
    ├── _detect_instrument(description) → str
    ├── _add_pitch_to_events(events, instrument, channel) → List[Dict]
    └── _events_to_midi(events, bpm) → MidiFile
```

---

## Component Interactions

### 1. Basic Generator Path

```
User Request
    ↓
validate_params()
    ↓
detect_style()
detect_instrument()
    ↓
get_channel_for_instrument()
    ↓
basic_generator.generate_track()
    ↓
MidiFile
```

### 2. DNA Generator Path

```
User Request
    ↓
validate_params()
    ↓
Create PatternDNA
    ↓
advanced_generator.generate_pattern_with_dna()
    ↓
add_pitch_to_events()
    ↓
humanizer.humanize_midi() [optional]
    ↓
Re-sort events
    ↓
events_to_midi()
    ↓
MidiFile
```

---

## Time Units & Conversions

```
Beats (Quarter Notes)
    │
    │ × 480 (ticks per beat)
    ▼
Ticks (MIDI Resolution)
    │
    │ + Delta Calculation
    ▼
Delta Times (MIDI Messages)

Example:
  0.25 beats = 120 ticks
  0.50 beats = 240 ticks
  1.00 beats = 480 ticks
  4.00 beats = 1920 ticks (1 bar in 4/4)
```

### BPM Conversion

```
BPM → Tempo (microseconds per beat)
120 BPM → 500,000 microseconds per beat

Formula:
  tempo = 60,000,000 / BPM
```

---

## Channel Assignment Logic

```
          Instrument Type
                │
    ┌───────────┴────────────┐
    │                        │
    ▼                        ▼
Is in                   Is in
DRUM_INSTRUMENTS?      MELODIC_INSTRUMENTS?
    │                        │
    │ Yes                    │ Yes
    ▼                        ▼
Channel 9              Channel 0
(Drums)                (Melodic)

DRUM_INSTRUMENTS = {
    'drums', 'kick', 'snare', 'hat',
    'clap', 'rim', 'crash', 'ride', 'tom'
}

MELODIC_INSTRUMENTS = {
    'bass', 'sub', '808',
    'melody', 'lead', 'synth'
}
```

---

## Error Handling Flow

```
generate()
    │
    ├─ Try:
    │   ├─ Validate parameters
    │   ├─ Route to generator
    │   └─ Return MidiFile
    │
    └─ Except:
        ├─ Log error with stack trace
        └─ Raise ValueError with message

events_to_midi()
    │
    ├─ For each event:
    │   ├─ Validate structure
    │   ├─ If incomplete → Log warning, skip
    │   └─ If valid → Convert
    │
    └─ Return MidiFile

Delta time calculation:
    │
    ├─ If delta < 0:
    │   ├─ Log warning
    │   └─ Set to 0
    │
    └─ Continue
```

---

## Logging Levels

```
DEBUG
  • DNA parameters
  • Event counts
  • Detailed flow

INFO
  • Generation routing
  • Auto-detection decisions
  • Final file info

WARNING
  • Unsupported styles
  • Unknown instruments
  • Incomplete events
  • Negative deltas

ERROR
  • Generation failures
  • Validation errors
  • Exception stack traces
```

---

## Performance Characteristics

### Time Complexity

```
Operation                    Complexity      Notes
─────────────────────────────────────────────────────
Parameter validation         O(1)            Constant
Style detection              O(n)            n = style count
Event generation            O(m)            m = bars × resolution
Event sorting               O(m log m)      Humanization re-sort
MIDI conversion             O(m log m)      Message sorting
Total                       O(m log m)      Dominated by sorting
```

### Space Complexity

```
Component                    Space           Notes
─────────────────────────────────────────────────────
Events list                  O(m)            m = note count
MIDI messages               O(2m)           note_on + note_off
Final file                  O(2m)           Compressed
Total                       O(m)            Linear in note count
```

### Typical Sizes

```
Pattern Type         Events    Messages    File Size
──────────────────────────────────────────────────────
Simple kick (4 bars)   16        32         < 1 KB
Full drums (4 bars)    64        128        < 2 KB
Complex trap (8 bars)  200       400        < 5 KB
```

---

## Design Patterns Used

### 1. **Strategy Pattern**
- Routing between Basic and DNA generators
- Different generation strategies for different needs

### 2. **Template Method**
- Base flow in `generate()`
- Subclasses (`_generate_with_dna()`) fill in details

### 3. **Singleton (Recommended)**
- Single generator instance in API
- Reuse expensive initialization

### 4. **Builder Pattern**
- PatternDNA construction
- Event structure building

### 5. **Adapter Pattern**
- Converting events to MIDI messages
- Adapting time representations (beats → ticks → deltas)

---

## Dependencies

```
IntegratedMidiGenerator
    ├── mido (MIDI file handling)
    ├── numpy (math operations)
    ├── logging (debugging)
    ├── typing (type hints)
    │
    ├── MidiGenerator
    │   ├── mido
    │   ├── random
    │   └── AdvancedPatternGenerator
    │
    ├── AdvancedPatternGenerator
    │   ├── numpy
    │   ├── random
    │   └── PatternDNA
    │
    └── HumanizationEngine
        └── random
```

---

## Extension Points

### Adding New Styles

```python
# In AdvancedPatternGenerator
self.pattern_templates['dubstep'] = {
    'kick': { ... },
    'snare': { ... },
    ...
}

# In MidiGenerator
self.style_patterns['dubstep'] = {
    'bpm': 140,
    'kick_pattern': [...],
    ...
}
```

### Adding New Instruments

```python
# In IntegratedMidiGenerator
DRUM_INSTRUMENTS.add('shaker')

# In MidiGenerator
self.drum_map['shaker'] = 70  # MIDI note
```

### Custom Humanization

```python
# Extend HumanizationEngine
class AdvancedHumanizer(HumanizationEngine):
    def humanize_midi(self, events):
        # Custom logic
        return super().humanize_midi(events)

# Use in IntegratedMidiGenerator
self.humanizer = AdvancedHumanizer()
```

---

## Testing Architecture

```
TestIntegratedMidiGenerator
├── Setup/Teardown
│   └── Create generator instance
│
├── Unit Tests
│   ├── Channel assignment
│   ├── Pitch assignment
│   ├── Event validation
│   └── Time calculation
│
├── Integration Tests
│   ├── Full generation flow
│   ├── DNA integration
│   └── Humanization
│
└── Edge Case Tests
    ├── Overlapping notes
    ├── Empty events
    ├── Invalid parameters
    └── Boundary conditions
```

---

## Deployment Considerations

### Production Setup

```python
# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Not DEBUG in production
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Initialize generator (singleton)
generator = IntegratedMidiGenerator(enable_humanization=True)

# Use in API
@app.post("/generate")
def generate(request):
    return generator.generate(**request.dict())
```

### Resource Management

- Generator is lightweight, can be singleton
- MIDI files should be cleaned up after serving
- Consider file size limits for long patterns
- Cache generated files if appropriate

---

## Summary

The architecture is designed for:
- ✅ **Flexibility**: Multiple generation strategies
- ✅ **Correctness**: Proper MIDI timing and channels
- ✅ **Extensibility**: Easy to add styles/instruments
- ✅ **Debuggability**: Comprehensive logging
- ✅ **Testability**: Modular design with clear interfaces
- ✅ **Performance**: Efficient algorithms, O(m log m) complexity
