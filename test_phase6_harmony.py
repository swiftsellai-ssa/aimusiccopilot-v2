
import sys
import os
import logging
from typing import List, Dict

# Setup path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from services.integrated_midi_generator import IntegratedMidiGenerator
from services.music_theory_engine import MusicTheoryEngine

def test_harmony_integration():
    print("--- Testing Harmony Engine Integration ---")
    
    # 1. Test Engine Directly
    engine = MusicTheoryEngine()
    prog_pop = engine.generate_progression('pop', 60, 'major')
    print(f"Pop Progression (C Major): {[c['name'] for c in prog_pop]}")
    
    prog_jazz = engine.generate_progression('jazz', 60, 'major')
    print(f"Jazz Progression (C Major): {[c['name'] for c in prog_jazz]}")
    
    prog_trap = engine.generate_progression('trap', 60, 'minor') # C Minor
    print(f"Trap Progression (C Minor): {[c['name'] for c in prog_trap]}")

    # 2. Test Integrated Generator
    generator = IntegratedMidiGenerator()
    
    print("\n--- Generating Jazz Track ---")
    try:
        mid, seed = generator.generate(
            description="smooth jazz",
            style="jazz", 
            instrument="chords", # Melodic instrument triggers harmony logic
            sub_option="chords",
            key="C",
            scale_type="major",
            bpm=120,
            use_dna=True
        )
        print("✅ Jazz Generation Success")
    except Exception as e:
        print(f"❌ Jazz Generation FAILED: {e}")
        import traceback
        traceback.print_exc()

    print("\n--- Generating Trap Bass (checking progression usage) ---")
    try:
        mid, seed = generator.generate(
            description="dark trap",
            style="trap",
            instrument="bass",
            sub_option="808",
            key="Cm",
            scale_type="minor",
            bpm=140,
            complexity=0.9
        )
        print("✅ Trap Bass Generation Success")
    except Exception as e:
        print(f"❌ Trap Bass Generation FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_harmony_integration()
