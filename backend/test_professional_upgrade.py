from services.advanced_midi_generator import AdvancedPatternGenerator, PatternDNA
from services.style_patterns import StylePatterns
from services.groove_engine import GrooveEngine

def test_upgrade():
    print("Testing Backend Professional Upgrade...")
    
    # 1. Test Style Patterns Loading
    print("\n[1] Testing Style Patterns...")
    style = 'funk'
    kick_pattern = StylePatterns.get_pattern(style, 'kick')
    print(f"Funk Kick Pattern: {kick_pattern}")
    assert len(kick_pattern) == 16, "Pattern length wrong"
    if 1 in kick_pattern:
        print("PASS: Funk kick pattern loaded.")
    else:
        print("FAIL: Funk kick pattern empty/wrong.")

    # 2. Test Groove Engine
    print("\n[2] Testing Groove Engine...")
    offset_straight = GrooveEngine.get_timing_offset(1, 'straight')
    offset_swing = GrooveEngine.get_timing_offset(1, 'swing_jazz')
    print(f"Straight Offset (pos 1): {offset_straight}")
    print(f"Swing Offset (pos 1): {offset_swing}")
    
    assert offset_straight == 0, "Straight groove should be 0"
    assert offset_swing > 0, "Swing should add offset to odd notes"
    print("PASS: Groove engine offsets correct.")

    # 3. Test Generator Integration
    print("\n[3] Testing Integration...")
    gen = AdvancedPatternGenerator()
    dna = PatternDNA(density=0.8, complexity=0.5, groove=0.6, velocity_curve='accent', evolution=0.2)
    
    events = gen.generate_pattern_with_dna('jazz', 'ride', dna, bars=1)
    print(f"Generated {len(events)} events for Jazz Ride with swing.")
    
    # Check if we have micro-timing
    has_microtiming = False
    for evt in events:
        # Check if time is not perfectly quantized (e.g. x.0, x.25, x.50, x.75)
        # Swing usually adds something like 0.16
        remainder = evt['time'] % 0.25
        if remainder > 0.01:
            has_microtiming = True
            break
            
    if has_microtiming:
        print("PASS: Generator output contains micro-timing/groove.")
    else:
        print("WARNING: Events appear fully quantized, swing might not be applied correctly.")
        print(events[:3])

if __name__ == "__main__":
    test_upgrade()
