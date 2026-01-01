# backend/services/music_theory.py

class MusicTheoryService:
    def __init__(self):
        # Complete note mapping with all enharmonics
        self.NOTE_MAP = {
            'C': 0, 'B#': 0,
            'C#': 1, 'Db': 1,
            'D': 2,
            'D#': 3, 'Eb': 3,
            'E': 4, 'Fb': 4,
            'F': 5, 'E#': 5,
            'F#': 6, 'Gb': 6,
            'G': 7,
            'G#': 8, 'Ab': 8,
            'A': 9,
            'A#': 10, 'Bb': 10,
            'B': 11, 'Cb': 11
        }

        # Scales with proper intervals
        self.SCALES = {
            'minor': [0, 2, 3, 5, 7, 8, 10],        # Natural Minor
            'major': [0, 2, 4, 5, 7, 9, 11],        # Major
            'dorian': [0, 2, 3, 5, 7, 9, 10],       # Dorian Mode
            'phrygian': [0, 1, 3, 5, 7, 8, 10],     # Phrygian Mode
            'lydian': [0, 2, 4, 6, 7, 9, 11],       # Lydian Mode
            'mixolydian': [0, 2, 4, 5, 7, 9, 10],   # Mixolydian Mode
            'harmonic_minor': [0, 2, 3, 5, 7, 8, 11], # Harmonic Minor
            'pentatonic': [0, 2, 4, 7, 9],          # Pentatonic
            'blues': [0, 3, 5, 6, 7, 10],           # Blues Scale
            'chromatic': list(range(12))             # All notes
        }

        # Chord progressions for different moods
        self.PROGRESSIONS = {
            'sad': [1, 6, 3, 7],          # i - VI - III - VII
            'dark_trap': [1, 1, 6, 5],    # i - i - VI - v
            'uplifting': [1, 4, 5, 1],    # I - IV - V - I
            'epic': [1, 6, 7, 1],         # i - VI - VII - i
            'jazz': [2, 5, 1, 6],         # ii - V - I - vi
            'pop': [1, 5, 6, 4],          # I - V - vi - IV
            'edm': [1, 1, 6, 7],          # i - i - VI - VII
            'tension': [1, 2, 5, 1]       # i - ii° - V - i
        }
        
        # Chord types
        self.CHORD_TYPES = {
            'triad': [0, 2, 4],           # Root, 3rd, 5th
            'seventh': [0, 2, 4, 6],      # Add 7th
            'ninth': [0, 2, 4, 6, 1],     # Add 9th
            'sus2': [0, 1, 4],            # Suspended 2nd
            'sus4': [0, 3, 4],            # Suspended 4th
            'power': [0, 4]               # Power chord (no 3rd)
        }

    def get_midi_root(self, note_name: str, octave: int = 3) -> int:
        """
        Convert note name to MIDI number
        C4 = 60 (Middle C)
        """
        # Handle invalid input
        if not note_name or note_name not in self.NOTE_MAP:
            return 60  # Default to C4
            
        base_val = self.NOTE_MAP[note_name]
        # MIDI calculation: octave starts at -1
        # C4 = 60, so (4+1)*12 + 0 = 60
        return (octave + 1) * 12 + base_val

    def get_scale_notes(self, root: str, scale_name: str, octave: int = 3) -> list:
        """Get all MIDI notes in a scale"""
        root_midi = self.get_midi_root(root, octave)
        intervals = self.SCALES.get(scale_name, self.SCALES['major'])
        
        return [root_midi + interval for interval in intervals]

    def get_chord(self, root: str, chord_type: str = 'triad', octave: int = 3) -> list:
        """Get MIDI notes for a chord"""
        root_midi = self.get_midi_root(root, octave)
        chord_intervals = self.CHORD_TYPES.get(chord_type, self.CHORD_TYPES['triad'])
        
        # Map to scale degrees
        scale = self.SCALES['major']  # Default to major scale
        chord_notes = []
        
        for interval in chord_intervals:
            note = root_midi + scale[interval % len(scale)]
            chord_notes.append(note)
            
        return chord_notes

    def get_progression(self, key: str, progression_type: str = 'pop', octave: int = 3) -> list:
        """Get chord progression as MIDI notes"""
        degrees = self.PROGRESSIONS.get(progression_type, self.PROGRESSIONS['pop'])
        scale = self.SCALES['major'] if progression_type in ['pop', 'uplifting'] else self.SCALES['minor']
        root_midi = self.get_midi_root(key, octave)
        
        chords = []
        for degree in degrees:
            # Get root note of chord from scale degree
            chord_root = root_midi + scale[(degree - 1) % len(scale)]
            # Build triad from that root
            chord = [chord_root, chord_root + 3, chord_root + 7]  # Simple major/minor triad
            chords.append(chord)
            
        return chords