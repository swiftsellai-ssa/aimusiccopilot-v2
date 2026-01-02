
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.advanced_midi_generator import AdvancedPatternGenerator, PatternDNA
from backend.services.integrated_midi_generator import IntegratedMidiGenerator
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestWiring")

def test_wiring():
    print("--- Starting Dry Run for Backend Wiring ---")
    
    # 1. Test AdvancedGenerator Directly
    adv_gen = AdvancedPatternGenerator()
    dna = PatternDNA(density=0.8, complexity=0.8, groove=0.5, velocity_curve="accent", evolution=0.2)
    
    # Test 'full_kit' composite generation
    print("\n[Test 1] Generating full_kit pattern...")
    events = adv_gen.generate_pattern_with_dna("techno", "full_kit", dna, bars=4)
    print(f"Generated {len(events)} events for full_kit.")
    if len(events) == 0:
        print("FAIL: No events generated for full_kit")
        return
    
    # Check if events have instrument_type
    sample_evt = events[0]
    print(f"Sample Event: {sample_evt}")
    if 'instrument_type' not in sample_evt:
        print("FAIL: 'instrument_type' missing from event")
    else:
        print(f"PASS: Found instrument_type='{sample_evt['instrument_type']}'")

    # 2. Test Music Theory Support (Chords)
    print("\n[Test 2] Generating Chords pattern...")
    chord_events = adv_gen.generate_pattern_with_dna("pop", "chords", dna, bars=4)
    print(f"Generated {len(chord_events)} events for chords.")
    
    if not chord_events:
        print("FAIL: No events for chords")
    else:
        sample_chord = chord_events[0]
        if not sample_chord.get('is_chord'):
            print("FAIL: 'is_chord' flag missing or false")
        else:
            print("PASS: is_chord=True verified")
            
    # 3. Test IntegratedMidiGenerator (End-to-End Logic)
    print("\n[Test 3] IntegratedMidiGenerator Pitch Mapping...")
    int_gen = IntegratedMidiGenerator(enable_humanization=False)
    
    # Simulate a request
    # Pass 'full_kit' as instrument
    # use_dna=True forced
    try:
        midi_file, seed = int_gen.generate(
            description="test full kit",
            style="techno", 
            instrument="full_kit", 
            use_dna=True,
            complexity=0.8
        )
        print(f"PASS: Integrated generation successful. Tracks: {len(midi_file.tracks)}")
        
        # Verify tracks contain notes on channel 9 for drums
        has_drums = False
        for track in midi_file.tracks:
            for msg in track:
                if msg.type == 'note_on' and msg.channel == 9:
                    has_drums = True
                    break
        
        if has_drums:
             print("PASS: Found drum notes on channel 9")
        else:
             print("FAIL: No drum notes on channel 9 found")

    except Exception as e:
        print(f"FAIL: Integrated generation threw exception: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_wiring()
