import sys
import os
import random

# Add the parent directory to sys.path to allow imports from backend
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from backend.services.pattern_intelligence import PatternIntelligence, PhraseStructure
    from backend.services.harmonic_engine import HarmonicEngine
    from backend.services.rhythm_engine import RhythmEngine
    from backend.services.production_engine import ProductionEngine, VelocityAutomation
    print("✅ All Advanced Engine Modules Imported Successfully.\n")
except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("Make sure your service files are in 'backend/services/' and named correctly.")
    sys.exit(1)

def test_pattern_intelligence():
    print("--- Testing Pattern Intelligence (Structure) ---")
    try:
        pi = PatternIntelligence()
        # Mocking a request for a 16-bar structure
        structure_type = "AABA"
        print(f"Testing Structure Generation: {structure_type}")
        
        # NOTE: Assuming PhraseStructure logic exists as per your roadmap
        ps = PhraseStructure()
        dummy_pattern = [
            {'time': 0, 'velocity': 100},
            {'time': 0.25, 'velocity': 0},
            {'time': 0.5, 'velocity': 0},
            {'time': 0.75, 'velocity': 100}
        ]
        
        # Verify AABA logic (A, A, B, A)
        full_structure = ps.apply_structure(dummy_pattern, structure=structure_type)
        
        print(f"Input Pattern length: {len(dummy_pattern)}")
        print(f"Output Structure length: {len(full_structure)} (Should be 4x input for AABA)")
        
        if len(full_structure) == len(dummy_pattern) * 4:
            print("✅ Pattern Structure expanded correctly.")
        else:
            print("⚠️ Length mismatch in structure generation.")
            
    except Exception as e:
        print(f"❌ Pattern Intelligence Failed: {e}")
    print("\n")

def test_harmonic_engine():
    print("--- Testing Harmonic Engine (Passing Tones) ---")
    try:
        he = HarmonicEngine()
        # Mock simple melody: C4, E4 (Major 3rd interval)
        melody = [
            {'pitch': 60, 'duration': 1.0, 'time': 0.0},
            {'pitch': 64, 'duration': 1.0, 'time': 1.0}
        ]
        
        print(f"Original Melody: {[n['pitch'] for n in melody]}")
        
        enhanced_melody = he.add_passing_tones(melody, harmony=[])
        
        print(f"Enhanced Melody: {[n['pitch'] for n in enhanced_melody]}")
        
        if len(enhanced_melody) > len(melody):
            print("✅ Passing tones added successfully.")
        else:
            print("⚠️ No passing tones added (check interval logic).")
            
    except Exception as e:
        print(f"❌ Harmonic Engine Failed: {e}")
    print("\n")

def test_rhythm_engine():
    print("--- Testing Rhythm Engine (Ghost Notes) ---")
    try:
        re = RhythmEngine()
        # Mock a simple Hi-Hat pattern
        pattern = [
            {'pitch': 42, 'velocity': 100, 'time': 0.0},
            {'pitch': 42, 'velocity': 100, 'time': 0.5},
            {'pitch': 42, 'velocity': 100, 'time': 1.0}
        ]
        
        print(f"Original Events: {len(pattern)}")
        
        # Test with 'jazz' style which has high ghost note probability
        enhanced_pattern = re.add_ghost_notes(pattern, style='jazz')
        
        print(f"Enhanced Events: {len(enhanced_pattern)}")
        
        ghost_notes = [n for n in enhanced_pattern if n.get('velocity', 0) < 50]
        if ghost_notes:
            print(f"✅ Generated {len(ghost_notes)} Ghost Notes (Low Velocity).")
        else:
            print("⚠️ No ghost notes generated (might be probability based, try running again).")

    except Exception as e:
        print(f"❌ Rhythm Engine Failed: {e}")
    print("\n")

def test_production_engine():
    print("--- Testing Production Engine (Velocity Automation) ---")
    try:
        pe = ProductionEngine() # Or VelocityAutomation class directly
        va = VelocityAutomation()
        
        # Mock 16 hi-hats with flat velocity
        events = [{'pitch': 42, 'velocity': 100, 'time': i*0.25} for i in range(16)]
        
        print("Applying 'Human Drummer' Curve...")
        humanized = va.apply_velocity_curve(events, curve_type='human_drummer')
        
        velocities = [e['velocity'] for e in humanized]
        print(f"Velocities: {velocities[:8]}...")
        
        # Check if velocities are no longer all 100
        if any(v != 100 for v in velocities):
            print("✅ Velocity curve applied successfully (dynamics added).")
        else:
            print("⚠️ Velocities remained static.")
            
    except Exception as e:
        print(f"❌ Production Engine Failed: {e}")
    print("\n")

if __name__ == "__main__":
    print("🎹 STARTING ADVANCED ENGINE DIAGNOSTICS 🎹\n")
    test_pattern_intelligence()
    test_harmonic_engine()
    test_rhythm_engine()
    test_production_engine()
    print("🏁 DIAGNOSTICS COMPLETE")