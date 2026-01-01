# Examples - IntegratedMidiGenerator

This directory contains example scripts demonstrating the IntegratedMidiGenerator.

## Prerequisites

1. **Activate Virtual Environment**:
   ```bash
   # Windows
   cd backend
   venv\Scripts\activate

   # Linux/Mac
   cd backend
   source venv/bin/activate
   ```

2. **Install Dependencies** (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

## Running Examples

### Option 1: Using Batch Script (Windows)

From the `backend` directory:
```bash
run_demo.bat
```

This automatically activates the virtual environment and runs the demo.

### Option 2: Manual Execution

From the `backend` directory with venv activated:
```bash
python examples/integrated_generator_demo.py
```

### Option 3: From Examples Directory

```bash
cd backend/examples
..\venv\Scripts\activate
python integrated_generator_demo.py
```

## Available Examples

### 1. integrated_generator_demo.py

Comprehensive demo showing:
- Auto-detection of style and instrument
- Explicit DNA parameter control
- Humanization on/off comparison
- Basic vs DNA generator comparison
- Various style examples (techno, trap, house, dnb)
- DNA parameter tuning

**Output**: Generates 6 MIDI files in `backend/output/demo/`

### 2. api_integration_example.py

Shows how to integrate IntegratedMidiGenerator with FastAPI:
- Request/response models
- Endpoint implementation
- Error handling
- Metadata tracking

**Usage**:
- Review the code for integration patterns
- Can be run standalone to test logic
- Copy patterns into your main API

## Troubleshooting

### ModuleNotFoundError: No module named 'mido'

**Problem**: Virtual environment not activated or dependencies not installed.

**Solution**:
```bash
cd backend
venv\Scripts\activate
pip install -r requirements.txt
```

### ImportError: attempted relative import with no known parent package

**Problem**: Running from wrong directory or incorrect Python path.

**Solution**: Run from the `backend` directory:
```bash
cd backend
python examples/integrated_generator_demo.py
```

### No output files created

**Problem**: Check console for errors.

**Solution**:
- Ensure `backend/output/demo/` directory can be created
- Check file permissions
- Enable logging to see what's happening

## Output

All examples save MIDI files to:
```
backend/output/demo/
backend/output/api_generated/
```

These directories are created automatically if they don't exist.

## Next Steps

After running the examples:

1. **Open MIDI files in your DAW** to hear the results
2. **Compare different generations**:
   - DNA vs Basic
   - Humanized vs Quantized
   - Different styles and parameters
3. **Experiment with parameters** by modifying the demo script
4. **Integrate into your API** using the API integration example

## Example Output

When you run `integrated_generator_demo.py`, you should see:

```
============================================================
Integrated MIDI Generator Demo
============================================================

1. Generating techno kick (auto DNA)...
INFO: Auto-detected use_dna=True for style=techno
INFO: Generating: style=techno, instrument=kick, use_dna=True, humanize=True, channel=9
   ✓ Saved to output/demo/techno_kick.mid

2. Generating trap hi-hats with DNA...
   ✓ Saved to output/demo/trap_hats.mid

...

============================================================
Demo complete! Generated 6 MIDI files in output/demo/
============================================================
```

## Customization

Feel free to modify the demo scripts to test your own patterns:

```python
# Add your own test
midi = generator.generate(
    description="your custom description",
    style="techno",
    bpm=132,
    bars=8,
    density=0.8,
    complexity=0.7
)
midi.save("output/demo/my_custom_pattern.mid")
```

## Resources

- [Main README](../services/INTEGRATED_GENERATOR_README.md) - Complete documentation
- [Quick Reference](../services/QUICK_REFERENCE.md) - Parameter reference
- [Architecture](../services/ARCHITECTURE.md) - System design
- [API Integration](api_integration_example.py) - FastAPI example
