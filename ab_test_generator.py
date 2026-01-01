import sys
import os
import argparse

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.integrated_midi_generator import IntegratedMidiGenerator

def run_ab_test(description, style, instrument):
    """
    Generates two variations (A and B) with different DNA settings
    to allow for direct comparison.
    """
    gen = IntegratedMidiGenerator()
    
    print(f"🎧 Running A/B Test for: '{description}' ({style} - {instrument})")
    
    # Configuration A: Safe / Standard
    # Good for establishing a baseline
    config_a = {
        "density": 0.5,
        "complexity": 0.4,
        "groove": 0.2,
        "evolution": 0.2,
        "velocity_curve": "natural"
    }
    
    # Configuration B: Experimental / Complex
    # Pushes the algorithms to be more creative
    config_b = {
        "density": 0.8,
        "complexity": 0.9,
        "groove": 0.6,
        "evolution": 0.7,
        "velocity_curve": "exponential"
    }

    print("   Generating Variation A (Standard)...")
    midi_a = gen.generate(
        description=description,
        style=style,
        instrument=instrument,
        use_dna=True,
        **config_a
    )
    filename_a = f"ab_test_A_{style}_{instrument}.mid"
    midi_a.save(filename_a)
    print(f"   ✅ Saved {filename_a}")

    print("   Generating Variation B (Experimental)...")
    midi_b = gen.generate(
        description=description,
        style=style,
        instrument=instrument,
        use_dna=True,
        **config_b
    )
    filename_b = f"ab_test_B_{style}_{instrument}.mid"
    midi_b.save(filename_b)
    print(f"   ✅ Saved {filename_b}")
    
    print("\nCompare the two files in your DAW to see how DNA parameters affect the output!")

if __name__ == "__main__":
    # Example usage
    run_ab_test("driving techno beat", "techno", "kick")