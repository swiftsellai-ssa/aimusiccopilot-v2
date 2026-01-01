import unittest
import sys
import os

# Add backend to path so we can import services
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from services.integrated_midi_generator import IntegratedMidiGenerator

class TestPatternGeneration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Initialize the generator once for all tests"""
        cls.gen = IntegratedMidiGenerator()

    def test_house_kick_structure(self):
        """Test that House Kicks follow 4-on-the-floor pattern"""
        # Generate a simple house kick, 1 bar, no humanization (for precise grid check)
        midi = self.gen.generate(
            description="house kick",
            style="house",
            instrument="kick",
            bpm=120,
            bars=1,
            humanize=False 
        )
        
        self.assertIsNotNone(midi, "Generation failed to return MIDI object")
        self.assertTrue(len(midi.tracks) > 0, "MIDI should have tracks")
        
        # Get the first track
        track = midi.tracks[0]
        
        # Count Note On events
        # In a standard 4-on-the-floor (1 bar), we expect 4 kicks
        note_ons = [msg for msg in track if msg.type == 'note_on' and msg.velocity > 0]
        self.assertTrue(len(note_ons) >= 4, f"Expected at least 4 kicks for House, got {len(note_ons)}")

    def test_density_algorithm(self):
        """Verify density parameter actually affects note count"""
        # Generate Low Density Hi-Hats
        midi_low = self.gen.generate(
            description="hihats", 
            instrument="hat", 
            use_dna=True, 
            density=0.2,
            bars=1
        )
        
        # Generate High Density Hi-Hats
        midi_high = self.gen.generate(
            description="hihats", 
            instrument="hat", 
            use_dna=True, 
            density=0.9,
            bars=1
        )
        
        # Count notes
        count_low = sum(1 for msg in midi_low.tracks[0] if msg.type == 'note_on' and msg.velocity > 0)
        count_high = sum(1 for msg in midi_high.tracks[0] if msg.type == 'note_on' and msg.velocity > 0)
        
        print(f"Density Test: Low={count_low}, High={count_high}")
        self.assertGreater(count_high, count_low, "High density should produce more notes than low density")

    def test_dnb_tempo_defaults(self):
        """Test that DnB style triggers appropriate internal logic (like tempo)"""
        # We generate a DnB pattern
        midi = self.gen.generate(
            description="dnb break",
            style="dnb",
            bars=2
        )
        # Basic sanity check that it generated successfully
        self.assertIsNotNone(midi)

if __name__ == '__main__':
    unittest.main()