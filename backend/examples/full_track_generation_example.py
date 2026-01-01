"""
Full Track Generation Example

This demonstrates how to use IntegratedMidiGenerator together with
other generators (chord progression, melody) to create complete tracks.

Usage:
  cd backend
  venv\\Scripts\\activate
  python examples/full_track_generation_example.py
"""
import sys
import os

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

try:
    from services.integrated_midi_generator import IntegratedMidiGenerator
    from services.chord_progression_generator import ChordProgressionGenerator
    from services.melody_generator import MelodyGenerator
    import mido
    import logging
except ImportError as e:
    print(f"[ERROR] Import Error: {e}")
    print("\nMake sure you have installed dependencies:")
    print("  cd backend")
    print("  venv\\Scripts\\activate")
    print("  pip install -r requirements.txt")
    sys.exit(1)

# Enable logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)


def combine_midi_tracks(*midi_files):
    """
    Combine multiple MIDI files into one multi-track file.

    Args:
        *midi_files: Variable number of mido.MidiFile objects

    Returns:
        mido.MidiFile: Combined MIDI file
    """
    combined = mido.MidiFile()

    for midi_file in midi_files:
        for track in midi_file.tracks:
            combined.tracks.append(track)

    return combined


def generate_full_track(style="techno", bpm=128, bars=8):
    """
    Generate a complete track with drums, bass, chords, and melody.

    Args:
        style: Music style (techno, trap, house, etc.)
        bpm: Tempo
        bars: Number of bars

    Returns:
        mido.MidiFile: Complete multi-track MIDI file
    """
    print(f"\nGenerating full {style} track at {bpm} BPM, {bars} bars...")
    print("=" * 60)

    # Initialize generators
    midi_gen = IntegratedMidiGenerator(enable_humanization=True)
    chord_gen = ChordProgressionGenerator()
    melody_gen = MelodyGenerator()

    tracks = []

    # 1. Generate drums
    print("\n1. Generating drums...")
    drums = midi_gen.generate(
        description=f"{style} drums",
        style=style,
        instrument="drums",
        bpm=bpm,
        bars=bars,
        density=0.7,
        complexity=0.6
    )
    tracks.append(drums)
    print("   [OK] Drums generated")

    # 2. Generate kick (separate track for layering)
    print("\n2. Generating kick...")
    kick = midi_gen.generate(
        description=f"{style} kick",
        style=style,
        instrument="kick",
        bpm=bpm,
        bars=bars,
        use_dna=True
    )
    tracks.append(kick)
    print("   [OK] Kick generated")

    # 3. Generate hi-hats (separate track)
    print("\n3. Generating hi-hats...")
    hats = midi_gen.generate(
        description=f"{style} hats",
        style=style,
        instrument="hat",
        bpm=bpm,
        bars=bars,
        density=0.8,
        complexity=0.7
    )
    tracks.append(hats)
    print("   [OK] Hi-hats generated")

    # 4. Generate bass
    print("\n4. Generating bass...")
    bass = midi_gen.generate(
        description=f"{style} bass",
        style=style,
        instrument="bass",
        bpm=bpm,
        bars=bars,
        musical_key="A",
        musical_scale="minor"
    )
    tracks.append(bass)
    print("   [OK] Bass generated")

    # 5. Generate chord progression (if chord generator available)
    try:
        print("\n5. Generating chords...")
        # Note: Adapt this to your actual ChordProgressionGenerator API
        # This is a placeholder - adjust based on your implementation
        chords = chord_gen.generate_progression(
            key="A",
            scale="minor",
            bars=bars
        ) if hasattr(chord_gen, 'generate_progression') else None

        if chords:
            tracks.append(chords)
            print("   [OK] Chords generated")
        else:
            print("   [SKIP] Chord generator not available")
    except Exception as e:
        print(f"   [SKIP] Chord generation: {e}")

    # 6. Generate melody (if melody generator available)
    try:
        print("\n6. Generating melody...")
        # Note: Adapt this to your actual MelodyGenerator API
        melody = melody_gen.generate_melody(
            key="A",
            scale="minor",
            bars=bars
        ) if hasattr(melody_gen, 'generate_melody') else None

        if melody:
            tracks.append(melody)
            print("   [OK] Melody generated")
        else:
            print("   [SKIP] Melody generator not available")
    except Exception as e:
        print(f"   [SKIP] Melody generation: {e}")

    # Combine all tracks
    print(f"\n7. Combining {len(tracks)} tracks...")
    combined = combine_midi_tracks(*tracks)
    print(f"   [OK] Combined into {len(combined.tracks)} MIDI tracks")

    return combined


def main():
    print("=" * 60)
    print("Full Track Generation Example")
    print("=" * 60)

    # Create output directory
    output_dir = "output/full_tracks"
    os.makedirs(output_dir, exist_ok=True)

    # Example 1: Techno track
    print("\n" + "=" * 60)
    print("EXAMPLE 1: Techno Track")
    print("=" * 60)
    techno_track = generate_full_track(
        style="techno",
        bpm=132,
        bars=8
    )
    techno_path = f"{output_dir}/techno_full_track.mid"
    techno_track.save(techno_path)
    print(f"\n[OK] Saved to {techno_path}")

    # Example 2: Trap track
    print("\n" + "=" * 60)
    print("EXAMPLE 2: Trap Track")
    print("=" * 60)
    trap_track = generate_full_track(
        style="trap",
        bpm=140,
        bars=8
    )
    trap_path = f"{output_dir}/trap_full_track.mid"
    trap_track.save(trap_path)
    print(f"\n[OK] Saved to {trap_path}")

    # Example 3: House track
    print("\n" + "=" * 60)
    print("EXAMPLE 3: House Track")
    print("=" * 60)
    house_track = generate_full_track(
        style="house",
        bpm=125,
        bars=8
    )
    house_path = f"{output_dir}/house_full_track.mid"
    house_track.save(house_path)
    print(f"\n[OK] Saved to {house_path}")

    print("\n" + "=" * 60)
    print("Full Track Generation Complete!")
    print("=" * 60)
    print(f"\nGenerated 3 full tracks in {output_dir}/")
    print("\nTips:")
    print("  - Import MIDI files into your DAW")
    print("  - Each track is on a separate MIDI track")
    print("  - Assign different instruments to each track")
    print("  - Adjust mix levels and add effects")
    print("  - Export as audio when satisfied")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
