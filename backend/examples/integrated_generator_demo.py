"""
Demo script for IntegratedMidiGenerator

This script demonstrates various features of the integrated MIDI generator.

Usage:
  From backend directory: python examples/integrated_generator_demo.py
  With venv: backend\\venv\\Scripts\\activate && python examples/integrated_generator_demo.py
"""
import sys
import os

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

# Check if running in virtual environment
if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
    venv_path = os.path.join(backend_dir, 'venv', 'Scripts', 'python.exe')
    if os.path.exists(venv_path):
        print("WARNING: Virtual environment not activated!")
        print(f"   Please run: {os.path.join(backend_dir, 'venv', 'Scripts', 'activate')}")
        print("   Then try again.")
        sys.exit(1)

try:
    from services.integrated_midi_generator import IntegratedMidiGenerator
    import logging
except ImportError as e:
    print(f"[ERROR] Import Error: {e}")
    print("\nMake sure you have installed dependencies:")
    print("  cd backend")
    print("  venv\\Scripts\\activate")
    print("  pip install -r requirements.txt")
    sys.exit(1)

# Enable logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

def main():
    print("=" * 60)
    print("Integrated MIDI Generator Demo")
    print("=" * 60)

    # Create generator with humanization enabled
    generator = IntegratedMidiGenerator(enable_humanization=True)

    # Create output directory if it doesn't exist
    output_dir = "output/demo"
    os.makedirs(output_dir, exist_ok=True)

    # Example 1: Basic techno kick with auto DNA detection
    print("\n1. Generating techno kick (auto DNA)...")
    midi1 = generator.generate(
        description="dark techno kick",
        style="techno",
        instrument="kick",
        bpm=130,
        bars=4
    )
    path1 = f"{output_dir}/techno_kick.mid"
    midi1.save(path1)
    print(f"   [OK] Saved to {path1}")

    # Example 2: Complex trap hi-hats with explicit DNA
    print("\n2. Generating trap hi-hats with DNA...")
    midi2 = generator.generate(
        description="rolling trap hats",
        use_dna=True,
        style="trap",
        instrument="hat",
        density=0.9,
        complexity=0.8,
        groove=0.2,
        velocity_curve='exponential',
        evolution=0.3,
        bpm=140,
        bars=8
    )
    path2 = f"{output_dir}/trap_hats.mid"
    midi2.save(path2)
    print(f"   [OK] Saved to {path2}")

    # Example 3: Simple house pattern without humanization
    print("\n3. Generating house drums (no humanization)...")
    midi3 = generator.generate(
        description="house drums",
        humanize=False,
        style="house",
        instrument="drums",
        bpm=128,
        bars=4
    )
    path3 = f"{output_dir}/house_drums_quantized.mid"
    midi3.save(path3)
    print(f"   [OK] Saved to {path3}")

    # Example 4: DnB pattern with basic generator
    print("\n4. Generating DnB with basic generator...")
    midi4 = generator.generate(
        description="drum and bass breakbeat",
        use_dna=False,
        style="dnb",
        instrument="drums",
        bpm=174,
        bars=4
    )
    path4 = f"{output_dir}/dnb_basic.mid"
    midi4.save(path4)
    print(f"   [OK] Saved to {path4}")

    # Example 5: Low complexity with DNA (demonstrating separation)
    print("\n5. Generating simple pattern with DNA...")
    midi5 = generator.generate(
        description="minimal techno",
        use_dna=True,
        style="techno",
        instrument="kick",
        complexity=0.2,  # Low complexity
        density=0.5,     # Sparse
        evolution=0.1,   # Little variation
        bpm=125,
        bars=8
    )
    path5 = f"{output_dir}/minimal_techno_dna.mid"
    midi5.save(path5)
    print(f"   [OK] Saved to {path5}")

    # Example 6: Full drum pattern
    print("\n6. Generating full drum arrangement...")
    midi6 = generator.generate(
        description="full techno drums",
        style="techno",
        instrument="drums",
        density=0.7,
        complexity=0.6,
        groove=0.15,
        bpm=132,
        bars=8
    )
    path6 = f"{output_dir}/full_techno_drums.mid"
    midi6.save(path6)
    print(f"   [OK] Saved to {path6}")

    print("\n" + "=" * 60)
    print(f"Demo complete! Generated 6 MIDI files in {output_dir}/")
    print("=" * 60)
    print("\nTips:")
    print("  - Open the MIDI files in your DAW to hear the results")
    print("  - Compare quantized vs humanized versions")
    print("  - Compare DNA vs basic generator outputs")
    print("  - Try different DNA parameters for variation")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
