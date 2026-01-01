# Integration Guide - IntegratedMidiGenerator

This guide shows how to integrate the IntegratedMidiGenerator with your existing AI Music Copilot application.

---

## Quick Integration

### 1. Import and Initialize

```python
from services.integrated_midi_generator import IntegratedMidiGenerator

# Create once, reuse many times (singleton pattern recommended)
midi_generator = IntegratedMidiGenerator(enable_humanization=True)
```

### 2. Basic Usage

```python
# Generate MIDI from description
midi_file = midi_generator.generate(
    description="dark techno kick pattern",
    bpm=130,
    bars=4
)

# Save to file
midi_file.save("output/pattern.mid")
```

---

## Integration with Existing Services

### With ChordProgressionGenerator

```python
from services.chord_progression_generator import ChordProgressionGenerator
from services.integrated_midi_generator import IntegratedMidiGenerator

chord_gen = ChordProgressionGenerator()
midi_gen = IntegratedMidiGenerator()

# Generate chords
chords = chord_gen.generate_progression(key="C", scale="minor", bars=4)

# Generate drums to accompany
drums = midi_gen.generate(
    description="drums",
    style="house",
    instrument="drums",
    bpm=125,
    bars=4,
    musical_key="C",
    musical_scale="minor"
)

# Combine (both are mido.MidiFile objects)
combined = mido.MidiFile()
combined.tracks.extend(chords.tracks)
combined.tracks.extend(drums.tracks)
combined.save("output/chords_and_drums.mid")
```

### With MelodyGenerator

```python
from services.melody_generator import MelodyGenerator
from services.integrated_midi_generator import IntegratedMidiGenerator

melody_gen = MelodyGenerator()
midi_gen = IntegratedMidiGenerator()

# Generate melody
melody = melody_gen.generate_melody(key="A", scale="minor", bars=8)

# Generate bass line in same key
bass = midi_gen.generate(
    description="bass line",
    instrument="bass",
    musical_key="A",
    musical_scale="minor",
    bpm=120,
    bars=8
)

# Combine
combined = mido.MidiFile()
combined.tracks.extend(melody.tracks)
combined.tracks.extend(bass.tracks)
combined.save("output/melody_and_bass.mid")
```

---

## FastAPI Integration

### Add to your existing FastAPI app

```python
# In backend/main.py or your main app file

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from services.integrated_midi_generator import IntegratedMidiGenerator
import logging

app = FastAPI()

# Initialize generator (singleton)
midi_generator = IntegratedMidiGenerator(enable_humanization=True)

# Request model
class MidiGenerationRequest(BaseModel):
    description: str
    style: str | None = None
    instrument: str | None = None
    bpm: int = 120
    bars: int = 4
    use_dna: bool | None = None
    humanize: bool | None = None
    density: float = 0.7
    complexity: float = 0.5
    groove: float = 0.2

# Response model
class MidiGenerationResponse(BaseModel):
    success: bool
    file_path: str
    message: str

# Endpoint
@app.post("/api/generate-pattern", response_model=MidiGenerationResponse)
async def generate_pattern(request: MidiGenerationRequest):
    """Generate a MIDI pattern"""
    try:
        midi_file = midi_generator.generate(
            description=request.description,
            style=request.style,
            instrument=request.instrument,
            bpm=request.bpm,
            bars=request.bars,
            use_dna=request.use_dna,
            humanize=request.humanize,
            density=request.density,
            complexity=request.complexity,
            groove=request.groove
        )

        # Save file
        file_path = f"output/{request.description.replace(' ', '_')}.mid"
        midi_file.save(file_path)

        return MidiGenerationResponse(
            success=True,
            file_path=file_path,
            message="MIDI pattern generated successfully"
        )

    except Exception as e:
        logging.error(f"Generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
```

### Test the endpoint

```bash
curl -X POST "http://localhost:8000/api/generate-pattern" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "dark techno kick",
    "style": "techno",
    "instrument": "kick",
    "bpm": 130,
    "bars": 4,
    "use_dna": true,
    "complexity": 0.6
  }'
```

---

## Integration with AI Service

### Use with OpenAI to generate from natural language

```python
from services.ai_service import AIService
from services.integrated_midi_generator import IntegratedMidiGenerator

ai_service = AIService()
midi_gen = IntegratedMidiGenerator()

# User prompt
user_prompt = "Create an aggressive trap beat with rolling hi-hats"

# Extract parameters using AI
params = ai_service.extract_music_parameters(user_prompt)
# Returns: {
#   'description': 'aggressive trap beat',
#   'style': 'trap',
#   'instrument': 'hat',
#   'bpm': 140,
#   'density': 0.9,
#   'complexity': 0.8
# }

# Generate MIDI
midi_file = midi_gen.generate(**params)
midi_file.save("output/ai_generated.mid")
```

---

## Database Integration

### Store generation history

```python
from database import get_db
from models import MidiGeneration
from services.integrated_midi_generator import IntegratedMidiGenerator

midi_gen = IntegratedMidiGenerator()

def generate_and_save(user_id: int, description: str, **params):
    """Generate MIDI and save to database"""

    # Generate
    midi_file = midi_gen.generate(description=description, **params)

    # Save file
    file_path = f"storage/user_{user_id}/pattern_{timestamp}.mid"
    midi_file.save(file_path)

    # Save to database
    db = next(get_db())
    generation = MidiGeneration(
        user_id=user_id,
        description=description,
        parameters=params,
        file_path=file_path,
        created_at=datetime.now()
    )
    db.add(generation)
    db.commit()

    return generation
```

---

## Multi-Track Generation

### Generate complete arrangements

```python
from services.integrated_midi_generator import IntegratedMidiGenerator
import mido

def generate_full_arrangement(style="techno", bpm=130, bars=8):
    """Generate drums, bass, and melody"""

    gen = IntegratedMidiGenerator()

    # Generate each element
    kick = gen.generate(f"{style} kick", instrument="kick", style=style, bpm=bpm, bars=bars)
    snare = gen.generate(f"{style} snare", instrument="snare", style=style, bpm=bpm, bars=bars)
    hats = gen.generate(f"{style} hats", instrument="hat", style=style, bpm=bpm, bars=bars)
    bass = gen.generate(f"{style} bass", instrument="bass", style=style, bpm=bpm, bars=bars)

    # Combine into one file
    combined = mido.MidiFile()
    for midi in [kick, snare, hats, bass]:
        combined.tracks.extend(midi.tracks)

    return combined

# Use it
arrangement = generate_full_arrangement(style="techno", bpm=132, bars=8)
arrangement.save("output/full_arrangement.mid")
```

---

## Error Handling Best Practices

```python
from services.integrated_midi_generator import IntegratedMidiGenerator
import logging

logger = logging.getLogger(__name__)
midi_gen = IntegratedMidiGenerator()

def safe_generate(description: str, **params):
    """Generate MIDI with proper error handling"""

    try:
        # Attempt generation
        midi_file = midi_gen.generate(description, **params)

        logger.info(f"Successfully generated: {description}")
        return midi_file

    except ValueError as e:
        # Parameter validation errors
        logger.error(f"Invalid parameters: {e}")
        raise

    except Exception as e:
        # Unexpected errors
        logger.error(f"Generation failed: {e}", exc_info=True)
        # Could return a default/fallback pattern
        return midi_gen.generate("simple kick", instrument="kick", use_dna=False)
```

---

## Caching for Performance

```python
from functools import lru_cache
import hashlib
import json

class CachedMidiGenerator:
    """Wrapper with caching for repeated patterns"""

    def __init__(self):
        self.generator = IntegratedMidiGenerator()
        self.cache = {}

    def _generate_cache_key(self, description: str, **params) -> str:
        """Generate cache key from parameters"""
        cache_data = {"description": description, **params}
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.md5(cache_str.encode()).hexdigest()

    def generate(self, description: str, **params):
        """Generate with caching"""

        # Check cache
        cache_key = self._generate_cache_key(description, **params)

        if cache_key in self.cache:
            logger.info(f"Cache hit for: {description}")
            return self.cache[cache_key]

        # Generate
        midi_file = self.generator.generate(description, **params)

        # Cache
        self.cache[cache_key] = midi_file

        return midi_file

# Use it
cached_gen = CachedMidiGenerator()
midi1 = cached_gen.generate("techno kick", bpm=130)  # Generates
midi2 = cached_gen.generate("techno kick", bpm=130)  # Returns cached
```

---

## Real-Time Generation for UI

### WebSocket streaming

```python
from fastapi import WebSocket
from services.integrated_midi_generator import IntegratedMidiGenerator

midi_gen = IntegratedMidiGenerator()

@app.websocket("/ws/generate")
async def websocket_generate(websocket: WebSocket):
    """Stream generation progress"""

    await websocket.accept()

    try:
        # Receive request
        data = await websocket.receive_json()

        # Send progress updates
        await websocket.send_json({"status": "starting", "progress": 0})

        # Generate
        midi_file = midi_gen.generate(**data)

        await websocket.send_json({"status": "saving", "progress": 80})

        # Save
        file_path = f"output/{data['description']}.mid"
        midi_file.save(file_path)

        await websocket.send_json({
            "status": "complete",
            "progress": 100,
            "file_path": file_path
        })

    except Exception as e:
        await websocket.send_json({"status": "error", "message": str(e)})

    finally:
        await websocket.close()
```

---

## Batch Processing

```python
from services.integrated_midi_generator import IntegratedMidiGenerator
from concurrent.futures import ThreadPoolExecutor
import logging

def batch_generate(requests: list[dict]) -> list[str]:
    """Generate multiple patterns in parallel"""

    gen = IntegratedMidiGenerator()

    def generate_one(request: dict) -> str:
        """Generate single pattern"""
        try:
            midi = gen.generate(**request)
            path = f"output/{request['description']}.mid"
            midi.save(path)
            return path
        except Exception as e:
            logging.error(f"Failed to generate {request}: {e}")
            return None

    # Process in parallel
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(generate_one, requests))

    # Filter out failures
    return [r for r in results if r is not None]

# Use it
requests = [
    {"description": "techno kick", "style": "techno", "instrument": "kick"},
    {"description": "trap hats", "style": "trap", "instrument": "hat"},
    {"description": "house bass", "style": "house", "instrument": "bass"},
]

generated_files = batch_generate(requests)
print(f"Generated {len(generated_files)} patterns")
```

---

## Configuration Management

```python
from pydantic import BaseSettings
from services.integrated_midi_generator import IntegratedMidiGenerator

class MidiGeneratorConfig(BaseSettings):
    """Configuration for MIDI generator"""

    enable_humanization: bool = True
    default_bpm: int = 120
    default_bars: int = 4
    default_style: str = "techno"
    log_level: str = "INFO"

    class Config:
        env_prefix = "MIDI_GEN_"

# Load from environment
config = MidiGeneratorConfig()

# Initialize with config
midi_gen = IntegratedMidiGenerator(
    enable_humanization=config.enable_humanization
)

# Use defaults
def generate_with_defaults(description: str, **overrides):
    params = {
        "bpm": config.default_bpm,
        "bars": config.default_bars,
        "style": config.default_style,
        **overrides  # Allow overriding defaults
    }
    return midi_gen.generate(description, **params)
```

---

## Testing Integration

```python
import unittest
from services.integrated_midi_generator import IntegratedMidiGenerator

class TestMidiIntegration(unittest.TestCase):
    """Integration tests for MIDI generator"""

    def setUp(self):
        self.gen = IntegratedMidiGenerator(enable_humanization=False)

    def test_generates_valid_midi(self):
        """Test that output is valid MIDI"""
        midi = self.gen.generate("test", instrument="kick")

        self.assertIsNotNone(midi)
        self.assertGreater(len(midi.tracks), 0)

    def test_integrates_with_chord_generator(self):
        """Test integration with chord progression generator"""
        from services.chord_progression_generator import ChordProgressionGenerator

        chord_gen = ChordProgressionGenerator()
        chords = chord_gen.generate_progression("C", "minor", 4)

        drums = self.gen.generate(
            "drums",
            musical_key="C",
            musical_scale="minor",
            bars=4
        )

        # Should complete without errors
        self.assertIsNotNone(drums)

if __name__ == '__main__':
    unittest.main()
```

---

## Production Deployment Checklist

- [ ] Environment variables configured
- [ ] Logging properly set up
- [ ] Error handling in place
- [ ] Database integration tested
- [ ] API endpoints secured
- [ ] File storage configured
- [ ] Caching strategy implemented
- [ ] Rate limiting applied
- [ ] Monitoring set up
- [ ] Tests passing

---

## Common Patterns

### Pattern 1: User Request → AI → MIDI

```python
user_prompt = "Create a dark industrial techno track"
↓
ai_params = ai_service.extract_parameters(user_prompt)
↓
midi_file = midi_gen.generate(**ai_params)
↓
save_to_user_library(user_id, midi_file)
```

### Pattern 2: Template-Based Generation

```python
template = {
    "techno_kick": {"style": "techno", "instrument": "kick", "bpm": 130},
    "trap_hats": {"style": "trap", "instrument": "hat", "bpm": 140},
}

pattern_type = "techno_kick"
midi = midi_gen.generate(pattern_type, **template[pattern_type])
```

### Pattern 3: Progressive Enhancement

```python
# Start simple
basic = midi_gen.generate("kick", use_dna=False, humanize=False)

# Add DNA
with_dna = midi_gen.generate("kick", use_dna=True, humanize=False)

# Add humanization
humanized = midi_gen.generate("kick", use_dna=True, humanize=True)
```

---

## Resources

- [Main README](services/INTEGRATED_GENERATOR_README.md)
- [Quick Reference](services/QUICK_REFERENCE.md)
- [Architecture](services/ARCHITECTURE.md)
- [API Integration Example](examples/api_integration_example.py)
- [Full Track Example](examples/full_track_generation_example.py)

---

## Support

For integration questions or issues:
1. Check this guide
2. Review example scripts
3. Enable DEBUG logging
4. Check the Architecture documentation
