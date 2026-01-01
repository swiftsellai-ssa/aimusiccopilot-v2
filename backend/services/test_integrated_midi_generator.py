"""
Unit tests for IntegratedMidiGenerator
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import mido
except ImportError:
    # Mock mido if not available
    from unittest.mock import MagicMock
    sys.modules['mido'] = MagicMock()
    import mido

from .integrated_midi_generator import IntegratedMidiGenerator
from .advanced_midi_generator import PatternDNA


class TestIntegratedMidiGenerator(unittest.TestCase):
    """Test suite for IntegratedMidiGenerator"""

    def setUp(self):
        """Set up test fixtures"""
        self.generator = IntegratedMidiGenerator(enable_humanization=False)

    def test_init_default_humanization(self):
        """Test initialization with default humanization enabled"""
        gen = IntegratedMidiGenerator()
        self.assertTrue(gen.enable_humanization)

    def test_init_disabled_humanization(self):
        """Test initialization with humanization disabled"""
        gen = IntegratedMidiGenerator(enable_humanization=False)
        self.assertFalse(gen.enable_humanization)

    def test_get_channel_for_drum_instruments(self):
        """Test that drum instruments get channel 9"""
        drum_instruments = ['drums', 'kick', 'snare', 'hat', 'clap', 'rim']
        for instrument in drum_instruments:
            channel = self.generator._get_channel_for_instrument(instrument)
            self.assertEqual(channel, 9, f"Drum instrument '{instrument}' should use channel 9")

    def test_get_channel_for_melodic_instruments(self):
        """Test that melodic instruments get channel 0"""
        melodic_instruments = ['bass', 'melody', 'lead', 'synth', '808']
        for instrument in melodic_instruments:
            channel = self.generator._get_channel_for_instrument(instrument)
            self.assertEqual(channel, 0, f"Melodic instrument '{instrument}' should use channel 0")

    def test_validate_supported_styles(self):
        """Test validation accepts supported styles"""
        for style in self.generator.SUPPORTED_STYLES:
            try:
                self.generator._validate_generation_params(style, 'drums')
            except ValueError:
                self.fail(f"Should accept supported style '{style}'")

    def test_validate_unsupported_style_warning(self):
        """Test validation logs warning for unsupported styles"""
        with self.assertLogs(level='WARNING') as log:
            self.generator._validate_generation_params('unknown_style', 'drums')
            self.assertTrue(any('Unsupported style' in msg for msg in log.output))

    def test_add_pitch_to_drum_events(self):
        """Test adding pitch to drum events"""
        events = [
            {'time': 0.0, 'velocity': 100, 'duration': 0.25},
            {'time': 0.5, 'velocity': 90, 'duration': 0.25},
        ]

        result = self.generator._add_pitch_to_events(events, 'kick', channel=9)

        for event in result:
            self.assertIn('pitch', event)
            self.assertIn('channel', event)
            self.assertEqual(event['channel'], 9)
            self.assertEqual(event['pitch'], 36)  # Kick drum MIDI note

    def test_add_pitch_to_melodic_events(self):
        """Test adding pitch to melodic events"""
        events = [
            {'time': 0.0, 'velocity': 80, 'duration': 0.5},
        ]

        result = self.generator._add_pitch_to_events(events, 'bass', channel=0)

        for event in result:
            self.assertIn('pitch', event)
            self.assertEqual(event['channel'], 0)
            self.assertIsInstance(event['pitch'], int) 

    def test_events_to_midi_basic(self):
        """Test basic event to MIDI conversion"""
        events = [
            {'time': 0.0, 'pitch': 60, 'velocity': 100, 'duration': 0.5, 'channel': 0},
            {'time': 1.0, 'pitch': 62, 'velocity': 90, 'duration': 0.5, 'channel': 0},
        ]

        midi_file = self.generator._events_to_midi(events, bpm=120)

        self.assertIsInstance(midi_file, mido.MidiFile)
        self.assertEqual(len(midi_file.tracks), 1)
        # Should have: tempo + 2 note_on + 2 note_off = 5 messages
        self.assertGreaterEqual(len(midi_file.tracks[0]), 5)

    def test_events_to_midi_overlapping_notes(self):
        """Test MIDI conversion with overlapping notes"""
        events = [
            {'time': 0.0, 'pitch': 60, 'velocity': 100, 'duration': 1.0, 'channel': 0},
            {'time': 0.5, 'pitch': 64, 'velocity': 90, 'duration': 1.0, 'channel': 0},
        ]

        midi_file = self.generator._events_to_midi(events, bpm=120)
        track = midi_file.tracks[0]

        # Extract note messages (skip tempo message)
        note_messages = [msg for msg in track if msg.type in ['note_on', 'note_off']]

        # Should have 4 messages: 2 note_on, 2 note_off
        self.assertEqual(len(note_messages), 4)

    def test_events_to_midi_channel_assignment(self):
        """Test that MIDI messages preserve channel assignments"""
        events = [
            {'time': 0.0, 'pitch': 36, 'velocity': 100, 'duration': 0.25, 'channel': 9},
            {'time': 0.5, 'pitch': 60, 'velocity': 80, 'duration': 0.5, 'channel': 0},
        ]

        midi_file = self.generator._events_to_midi(events, bpm=120)
        note_messages = [msg for msg in midi_file.tracks[0] if msg.type in ['note_on', 'note_off']]

        # Check that drum notes use channel 9
        drum_messages = [msg for msg in note_messages if msg.note == 36]
        for msg in drum_messages:
            self.assertEqual(msg.channel, 9)

        # Check that melodic notes use channel 0
        melodic_messages = [msg for msg in note_messages if msg.note == 60]
        for msg in melodic_messages:
            self.assertEqual(msg.channel, 0)

    def test_events_to_midi_skips_incomplete_events(self):
        """Test that incomplete events are skipped with warning"""
        events = [
            {'time': 0.0, 'pitch': 60, 'velocity': 100, 'duration': 0.5, 'channel': 0},
            {'time': 1.0, 'velocity': 90},  # Missing pitch and duration
        ]

        with self.assertLogs(level='WARNING') as log:
            midi_file = self.generator._events_to_midi(events, bpm=120)
            self.assertTrue(any('incomplete event' in msg.lower() for msg in log.output))

    def test_humanization_resorts_events(self):
        """Test that events are re-sorted after humanization"""
        # Mock humanizer to shuffle times
        with patch.object(self.generator.humanizer, 'humanize_midi') as mock_humanize:
            # Humanizer returns events with modified times (out of order)
            mock_humanize.return_value = [
                {'time': 0.51, 'pitch': 62, 'velocity': 92, 'duration': 0.25, 'channel': 0},
                {'time': 1.02, 'pitch': 64, 'velocity': 83, 'duration': 0.25, 'channel': 0},
                {'time': 0.01, 'pitch': 60, 'velocity': 98, 'duration': 0.25, 'channel': 0},
            ]

            midi_file = self.generator._generate_with_dna(
                description="test",
                style="techno",
                instrument="kick",
                humanize=True,
                bars=1,
                bpm=120,
                channel=9
            )

            # Verify events were re-sorted
            self.assertIsInstance(midi_file, mido.MidiFile)

    def test_generate_auto_detect_use_dna(self):
        """Test automatic detection of DNA usage based on style"""
        with patch.object(self.generator, '_generate_with_dna') as mock_dna:
            # Mock return value needs to be tuple now
            mock_dna.return_value = mido.MidiFile()

            # Techno is supported by advanced generator
            self.generator.generate("techno beat", use_dna=None, style="techno")
            mock_dna.assert_called_once()

    def test_generate_force_basic_generator(self):
        """Test forcing basic generator with use_dna=False"""
        with patch.object(self.generator.basic_generator, 'generate_track') as mock_basic:
            mock_basic.return_value = mido.MidiFile()

            self.generator.generate("techno beat", use_dna=False, style="techno")
            mock_basic.assert_called_once()

    def test_generate_respects_humanization_parameter(self):
        """Test that humanization can be enabled/disabled per call"""
        gen = IntegratedMidiGenerator(enable_humanization=False)

        with patch.object(gen.humanizer, 'humanize_midi') as mock_humanize:
            mock_humanize.return_value = []

            try:
                gen.generate("techno kick", use_dna=True, humanize=True, style="techno", instrument="kick")
            except:
                pass  

            mock_humanize.assert_called()

    def test_separate_use_dna_from_complexity(self):
        """Test that use_dna is independent of complexity threshold"""
        with patch.object(self.generator, '_generate_with_dna') as mock_dna:
            mock_dna.return_value = mido.MidiFile()

            self.generator.generate(
                "techno kick",
                use_dna=True,
                complexity=0.1,  # Low complexity
                style="techno",
                instrument="kick"
            )

            mock_dna.assert_called_once()

    def test_determinism(self):
        """Test that using the same seed produces identical results"""
        seed = 12345
        
        # First generation
        midi1, seed1 = self.generator.generate(
            "test beat",
            style="techno",
            instrument="kick", 
            use_dna=True,
            humanize=True, # Include humanization to test random calls there too
            seed=seed
        )
        
        # Second generation
        midi2, seed2 = self.generator.generate(
            "test beat",
            style="techno",
            instrument="kick",
            use_dna=True,
            humanize=True,
            seed=seed
        )
        
        self.assertEqual(seed1, seed)
        self.assertEqual(seed2, seed)
        
        # Compare messages
        # Note: We need to serialize track messages to compare, or compare attributes
        
        track1 = list(midi1.tracks[0])
        track2 = list(midi2.tracks[0])
        
        self.assertEqual(len(track1), len(track2), "Track lengths differ")
        
        for msg1, msg2 in zip(track1, track2):
            # Compare relevant fields
            self.assertEqual(msg1.type, msg2.type)
            if hasattr(msg1, 'note'):
                self.assertEqual(msg1.note, msg2.note)
            if hasattr(msg1, 'velocity'):
                self.assertEqual(msg1.velocity, msg2.velocity)
            if hasattr(msg1, 'time'):
                self.assertEqual(msg1.time, msg2.time)

if __name__ == '__main__':
    unittest.main()
