# Setup Instructions - IntegratedMidiGenerator

## Quick Setup

### 1. Install Dependencies

From the `backend` directory:

```bash
# Activate virtual environment
venv\Scripts\activate

# Install/update dependencies (including mido)
pip install -r requirements.txt
```

**Note**: The `mido` library has been added to `requirements.txt` for MIDI file handling.

### 2. Verify Installation

```bash
python -c "import mido; print('mido installed:', mido.__version__)"
```

Expected output:
```
mido installed: 1.x.x
```

### 3. Run Tests (Optional)

```bash
python test_runner.py
```

### 4. Run Demo

```bash
# Option A: Using batch script
run_demo.bat

# Option B: Manual
python examples/integrated_generator_demo.py
```

## Full Installation from Scratch

If starting fresh:

### Windows

```bash
# 1. Navigate to backend
cd backend

# 2. Create virtual environment (if not exists)
python -m venv venv

# 3. Activate
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Verify
python -c "from services.integrated_midi_generator import IntegratedMidiGenerator; print('✓ Setup complete!')"

# 6. Run demo
run_demo.bat
```

### Linux/Mac

```bash
# 1. Navigate to backend
cd backend

# 2. Create virtual environment (if not exists)
python3 -m venv venv

# 3. Activate
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Verify
python -c "from services.integrated_midi_generator import IntegratedMidiGenerator; print('✓ Setup complete!')"

# 6. Run demo
python examples/integrated_generator_demo.py
```

## Dependencies Added

The following dependency has been added to `requirements.txt`:

- **mido** - MIDI file I/O library (used by IntegratedMidiGenerator)

Existing dependencies used:
- **numpy** - Mathematical operations (for PatternDNA)
- **midiutil** - Alternative MIDI library (already present)

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'mido'`

**Solution**:
```bash
cd backend
venv\Scripts\activate
pip install mido
```

Or reinstall all dependencies:
```bash
pip install -r requirements.txt
```

### Issue: Virtual environment not found

**Solution**:
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Issue: Permission errors on Windows

**Solution**: Run as administrator or check antivirus settings.

### Issue: Import errors in tests

**Solution**: Run tests from the `backend` directory:
```bash
cd backend
python test_runner.py
```

## Verify Everything Works

Run this comprehensive check:

```bash
cd backend
venv\Scripts\activate

# Test imports
python -c "from services.integrated_midi_generator import IntegratedMidiGenerator; print('✓ Imports work')"

# Test generation
python -c "from services.integrated_midi_generator import IntegratedMidiGenerator; gen = IntegratedMidiGenerator(); midi = gen.generate('test'); print('✓ Generation works')"

# Run demo
python examples\integrated_generator_demo.py
```

If all steps complete without errors, you're ready to go!

## Next Steps

1. ✅ Dependencies installed
2. ✅ Demo runs successfully
3. ⏭️ Review [Quick Reference](services/QUICK_REFERENCE.md)
4. ⏭️ Read [Main README](services/INTEGRATED_GENERATOR_README.md)
5. ⏭️ Integrate into your API using [API Integration Example](examples/api_integration_example.py)

## Development Workflow

For ongoing development:

```bash
# Always activate venv first
cd backend
venv\Scripts\activate

# Make changes to code
# ...

# Run tests
python test_runner.py

# Test your changes
python examples/integrated_generator_demo.py

# Deactivate when done
deactivate
```

## IDE Setup

### VS Code

Add to `.vscode/settings.json`:
```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/backend/venv/Scripts/python.exe",
  "python.testing.unittestEnabled": true,
  "python.testing.unittestArgs": [
    "-v",
    "-s",
    "./backend",
    "-p",
    "test_*.py"
  ]
}
```

### PyCharm

1. File → Settings → Project → Python Interpreter
2. Add Interpreter → Existing Environment
3. Select `backend/venv/Scripts/python.exe`

## Common Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Update single package
pip install --upgrade mido

# List installed packages
pip list

# Check for outdated packages
pip list --outdated

# Run tests
python test_runner.py

# Run demo
python examples/integrated_generator_demo.py

# Run specific test
python -m unittest services.test_integrated_midi_generator.TestIntegratedMidiGenerator.test_get_channel_for_drum_instruments -v
```

## Production Deployment

For production environments:

```bash
# Install production dependencies only (if you separate them)
pip install -r requirements.txt --no-dev

# Or use pip-tools for dependency locking
pip install pip-tools
pip-compile requirements.txt
pip-sync requirements.txt
```

## Docker (Optional)

If using Docker, add to your `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app/backend

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Support

If you encounter issues:

1. Check [Troubleshooting](#troubleshooting) section above
2. Review [Examples README](examples/README.md)
3. Enable debug logging: `logging.basicConfig(level=logging.DEBUG)`
4. Check that virtual environment is activated
5. Verify dependencies: `pip list`

Happy generating! 🎵
