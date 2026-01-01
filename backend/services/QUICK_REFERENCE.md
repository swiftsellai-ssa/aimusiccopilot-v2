# IntegratedMidiGenerator - Quick Reference

## 🚀 Quick Start

```python
from services.integrated_midi_generator import IntegratedMidiGenerator

# Create generator
gen = IntegratedMidiGenerator()

# Generate MIDI
midi = gen.generate("dark techno kick", bpm=130, bars=4)

# Save
midi.save("output.mid")
```

---

## 📋 Common Usage Patterns

### Pattern 1: Auto-Detect Everything
```python
midi = gen.generate("aggressive trap hi-hats with rolls")
# Style: trap, Instrument: hat, DNA: auto, Humanize: on
```

### Pattern 2: Explicit Parameters
```python
midi = gen.generate(
    description="minimal techno",
    style="techno",
    instrument="kick",
    bpm=128,
    bars=8,
    use_dna=True,
    humanize=True
)
```

### Pattern 3: DNA Tuning
```python
midi = gen.generate(
    description="complex beat",
    use_dna=True,
    density=0.9,      # Very dense
    complexity=0.8,   # Complex variations
    groove=0.3,       # Swung timing
    evolution=0.5,    # Lots of variation
    velocity_curve='accent'
)
```

### Pattern 4: Quantized (No Humanization)
```python
midi = gen.generate(
    description="precise techno",
    humanize=False    # Perfect quantization
)
```

---

## 🎛️ Parameters Reference

### Core Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `description` | str | required | Text description of pattern |
| `style` | str | auto | techno, trap, house, dnb, lofi |
| `instrument` | str | auto | kick, snare, hat, bass, melody, etc. |
| `bpm` | int | 120 | Tempo (40-300) |
| `bars` | int | 4 | Number of bars (1-32) |
| `use_dna` | bool | None | Force DNA generator (None=auto) |
| `humanize` | bool | None | Apply humanization (None=default) |

### DNA Parameters (when use_dna=True)
| Parameter | Type | Range | Description |
|-----------|------|-------|-------------|
| `density` | float | 0-1 | Note density (0.7=default) |
| `complexity` | float | 0-1 | Pattern complexity (0.5=default) |
| `groove` | float | 0-1 | Swing/groove (0.2=default) |
| `velocity_curve` | str | - | 'natural', 'accent', 'exponential', 'random' |
| `evolution` | float | 0-1 | Pattern variation (0.3=default) |

### Musical Parameters
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `musical_key` | str | 'C' | Root note |
| `musical_scale` | str | 'minor' | Scale type |

---

## 🎵 Supported Styles

| Style | BPM Range | Characteristics | Best For |
|-------|-----------|-----------------|----------|
| `techno` | 125-135 | 4-on-floor, driving | Kicks, minimal patterns |
| `trap` | 135-145 | Half-time, rolling hats | Hi-hats, 808s |
| `house` | 120-130 | Groovy, funky | Full drums, bass |
| `dnb` | 160-180 | Fast breaks | Breakbeats, energy |
| `lofi` | 80-95 | Relaxed, sparse | Laid-back patterns |

---

## 🥁 Supported Instruments

### Drums (Channel 9)
```
kick, snare, clap, rim
hat, hats, hihat (closed/open)
crash, ride, tom
drums (full kit)
```

### Melodic (Channel 0)
```
bass, sub, 808
melody, lead, synth
```

---

## 🎨 DNA Presets

### Minimal
```python
density=0.3, complexity=0.2, evolution=0.1
```

### Balanced
```python
density=0.6, complexity=0.5, evolution=0.3
```

### Complex
```python
density=0.9, complexity=0.8, evolution=0.5
```

### Groovy
```python
density=0.7, groove=0.4, velocity_curve='accent'
```

---

## 🔍 Common Patterns

### Techno Kick
```python
gen.generate("techno kick", style="techno", instrument="kick", bpm=130)
```

### Trap Hi-Hats
```python
gen.generate("trap hats", style="trap", instrument="hat",
             density=0.9, complexity=0.8, bpm=140)
```

### House Drums
```python
gen.generate("house drums", style="house", instrument="drums",
             groove=0.3, bpm=125)
```

### DnB Break
```python
gen.generate("dnb break", style="dnb", instrument="drums", bpm=174)
```

### Lo-Fi Beat
```python
gen.generate("lofi beat", style="lofi", instrument="drums",
             complexity=0.3, bpm=85)
```

---

## ⚠️ Common Issues

### Issue: Wrong MIDI Channel
**Symptom**: Drums sound like piano
**Solution**: Instrument type must be in DRUM_INSTRUMENTS
```python
# ❌ Wrong
gen.generate(description="drums", instrument="beat")

# ✅ Correct
gen.generate(description="drums", instrument="drums")
```

### Issue: No Notes Generated
**Symptom**: Empty MIDI file
**Solution**: Check density and complexity aren't too low
```python
# ❌ Too sparse
gen.generate(description="kick", density=0.1)

# ✅ Better
gen.generate(description="kick", density=0.6)
```

### Issue: Timing Feels Off
**Symptom**: Notes not quantized properly
**Solution**: Disable humanization or check BPM
```python
gen.generate(description="kick", humanize=False, bpm=120)
```

---

## 🧪 Testing

### Quick Test
```python
# Should generate 4 bars of techno kicks
midi = gen.generate("techno kick", bars=4)
assert len(midi.tracks[0]) > 0
```

### Run All Tests
```bash
cd backend
python test_runner.py
```

### Run Demo
```bash
python examples/integrated_generator_demo.py
```

---

## 📊 Performance Tips

### Fast Generation
```python
gen.generate(description="kick", use_dna=False, humanize=False)
# Uses basic generator, no humanization
```

### High Quality
```python
gen.generate(description="kick", use_dna=True, humanize=True,
             complexity=0.8, evolution=0.5)
# DNA + humanization, more variation
```

### Batch Generation
```python
# Reuse generator instance
gen = IntegratedMidiGenerator()
for i in range(10):
    midi = gen.generate(f"pattern {i}")
    midi.save(f"output_{i}.mid")
```

---

## 🐛 Debugging

### Enable Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now you'll see:
# - Generation routing decisions
# - DNA parameters
# - Event counts
# - Warnings
```

### Check Generated Events
```python
# Access internal methods for debugging
events = gen.advanced_generator.generate_pattern_with_dna(
    style="techno", instrument="kick", dna=dna, bars=4
)
print(f"Generated {len(events)} events")
for e in events[:5]:
    print(e)
```

---

## 🔗 Integration Examples

### FastAPI
```python
from fastapi import FastAPI
from services.integrated_midi_generator import IntegratedMidiGenerator

app = FastAPI()
gen = IntegratedMidiGenerator()

@app.post("/generate")
def generate(description: str, bpm: int = 120):
    midi = gen.generate(description, bpm=bpm)
    midi.save("temp.mid")
    return {"file": "temp.mid"}
```

### Flask
```python
from flask import Flask, request
app = Flask(__name__)
gen = IntegratedMidiGenerator()

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    midi = gen.generate(**data)
    midi.save("output.mid")
    return {"status": "success"}
```

---

## 📚 Further Reading

- [README](INTEGRATED_GENERATOR_README.md) - Complete usage guide
- [Architecture](ARCHITECTURE.md) - System design
- [Changelog](CHANGELOG_INTEGRATED_GENERATOR.md) - Version history
- [Tests](test_integrated_midi_generator.py) - Test examples

---

## 💡 Pro Tips

1. **Start Simple**: Use auto-detection first, then tune parameters
2. **DNA for Variation**: Use DNA when you want evolving patterns
3. **Basic for Speed**: Use basic generator for simple, fast patterns
4. **Humanize Selectively**: Enable for organic feel, disable for precision
5. **Log Everything**: Enable logging when developing/debugging
6. **Reuse Generator**: Create once, use many times
7. **Test Often**: Run tests after making changes

---

## 🎯 Cheat Sheet

```python
# Minimal example
gen = IntegratedMidiGenerator()
midi = gen.generate("techno kick")
midi.save("out.mid")

# Full control
midi = gen.generate(
    description="dark industrial techno",
    style="techno",
    instrument="kick",
    use_dna=True,
    humanize=True,
    bpm=132,
    bars=8,
    density=0.7,
    complexity=0.6,
    groove=0.2,
    evolution=0.4,
    velocity_curve='accent'
)
```

---

**Need help?** Check the [README](INTEGRATED_GENERATOR_README.md) or run the [demo](../examples/integrated_generator_demo.py)!
