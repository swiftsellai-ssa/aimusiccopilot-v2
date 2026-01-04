
import sys
import os
import logging
import statistics

sys.path.append(os.path.join(os.path.dirname(__file__)))

from services.integrated_midi_generator import IntegratedMidiGenerator
from services.advanced_midi_generator import MUSIC_STYLES

# Mock logging
logging.basicConfig(level=logging.ERROR)

def check_swing(style_name, expected_swing):
    print(f"\n--- Testing usage of Swing for {style_name} (Expected > {expected_swing}) ---")
    gen = IntegratedMidiGenerator()
    
    # Generate Ride for Jazz (more 8ths), Hat for others
    instr = 'ride' if style_name == 'jazz' else 'hat'
    midi, seed = gen.generate(
        description=f"{style_name} beat",
        style=style_name,
        instrument=instr,
        complexity=0.5, # triggers default complexity
        bars=1
    )
    
    events = []
    
    track = midi.tracks[0]
    current_time = 0
    timings = []
    
    for msg in track:
        current_time += msg.time
        if msg.type == 'note_on' and msg.velocity > 0:
            timings.append(current_time)
            
    # Analyze off-beat timings
    # 16th notes: 0, 120, 240, 360...
    # 8th notes (offbeat): 240
    # 16th notes (offbeat): 120, 360
    
    ticks_per_beat = 480
    
    offsets = []
    for t in timings:
        rem = t % ticks_per_beat
        
        # Check 16th offbeats
        if 100 < rem < 140: # Near 120
            diff = rem - 120
            if diff > 0: offsets.append(diff)
        elif 340 < rem < 380: # Near 360
            diff = rem - 360
            if diff > 0: offsets.append(diff)
            
        # Check 8th offbeat (240)
        elif 220 < rem < 260: # Near 240
            diff = rem - 240
            if diff > 0: offsets.append(diff)
                 
    avg_offset = statistics.mean(offsets) if offsets else 0
    print(f"Average Off-Beat Delay (Ticks): {avg_offset:.2f}")
    
    is_swinging = avg_offset > 5 # Significant delay
    if expected_swing > 0.1 and is_swinging:
        print("✅ SUCCESS: Swing detected.")
    elif expected_swing < 0.1 and not is_swinging:
        print("✅ SUCCESS: Straight beat detected (as expected).")
    else:
        print(f"⚠️ WARNING: Swing mismatch. Expected {expected_swing}, got avg offset {avg_offset}")

if __name__ == "__main__":
    check_swing('jazz', 0.35)
    check_swing('techno', 0.1) # Has small swing in definition
    check_swing('metal', 0.0)
