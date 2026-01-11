
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.integrated_midi_generator import IntegratedMidiGenerator
import mido

def test_context_generation():
    print("--- Testing Context Awareness (Phase 7) ---")
    
    generator = IntegratedMidiGenerator()
    
    # Mock Context: 2 Bars. Bar 1: C Major (C-E-G), Bar 2: F Major (F-A-C)
    # Notes are pitch classes: C=0, E=4, G=7, F=5, A=9
    context_chords = [
        {'bar': 1, 'chord': 'C maj', 'notes': [0, 4, 7]},
        {'bar': 2, 'chord': 'F maj', 'notes': [5, 9, 0]}
    ]
    
    # Generate Chords Track
    print("\n1. Generating Chords with Context...")
    mid, _ = generator.generate(
        description="test context",
        style="house", # House - Supported by Advanced Generator
        instrument="melody",
        sub_option="chords",
        bars=2,
        forced_context=context_chords, # FORCE CONTEXT (New Param)
        key='C',
        bpm=120
    )
    
    # Analyze Output
    # Analyze Output
    # IntegratedMidiGenerator usually produces Type 0 (Single Track) or Type 1 with just 1 track for patterns.
    # Let's check track count
    print(f"Total Tracks: {len(mid.tracks)}")
    track = mid.tracks[0]
    
    # Collect notes by bar
    bar1_notes = []
    bar2_notes = []
    
    ticks_per_beat = 480
    ticks_per_bar = ticks_per_beat * 4
    
    current_ticks = 0
    for msg in track:
        current_ticks += msg.time
        if msg.type == 'note_on' and msg.velocity > 0:
            if current_ticks < ticks_per_bar:
                bar1_notes.append(msg.note)
            elif current_ticks < ticks_per_bar * 2:
                bar2_notes.append(msg.note)
                
    print(f"Bar 1 Notes: {bar1_notes}")
    print(f"Bar 2 Notes: {bar2_notes}")
    
    # Verify Bar 1 (Should be C Major: 60, 64, 67...)
    # Check if any note aligns with C Major
    # We expect 60, 64, 67 to be present.
    # Note: Generator might repeat notes or add octaves, but pitch classes should match.
    bar1_pcs = sorted(list(set([n % 12 for n in bar1_notes])))
    bar2_pcs = sorted(list(set([n % 12 for n in bar2_notes])))
    
    print(f"Bar 1 Pitch Classes: {bar1_pcs} (Expect [0, 4, 7])")
    print(f"Bar 2 Pitch Classes: {bar2_pcs} (Expect [0, 5, 9])")
    
    if set([0, 4, 7]).issubset(set(bar1_pcs)):
        print("✅ Bar 1 matches C Major")
    else:
        print("❌ Bar 1 Mismatch")
        
    if set([0, 5, 9]).issubset(set(bar2_pcs)):
        print("✅ Bar 2 matches F Major")
    else:
        print("❌ Bar 2 Mismatch")

if __name__ == "__main__":
    test_context_generation()
