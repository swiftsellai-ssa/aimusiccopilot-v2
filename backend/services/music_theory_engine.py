from typing import List, Dict, Tuple

class MusicTheoryEngine:
    """
    Handles musical theory logic, specifically chord progressions and scale mapping.
    """

    # Note mapping
    NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    
    # Scale Intervals
    SCALES = {
        'major': [0, 2, 4, 5, 7, 9, 11],
        'minor': [0, 2, 3, 5, 7, 8, 10], 
        'dorian': [0, 2, 3, 5, 7, 9, 10],
        'phrygian': [0, 1, 3, 5, 7, 8, 10],
        'lydian': [0, 2, 4, 6, 7, 9, 11],
        'mixolydian': [0, 2, 4, 5, 7, 9, 10],
        'locrian': [0, 1, 3, 5, 6, 8, 10],
        'blues': [0, 3, 5, 6, 7, 10], # Hexatonic
    }

    # Common Progressions (Scale Degrees)
    PROGRESSIONS = {
        'pop':      [1, 5, 6, 4], # I-V-vi-IV
        'jazz':     [2, 5, 1, 6], # ii-V-I-vi
        'blues':    [1, 4, 1, 5], # 12-bar simple
        'rock':     [1, 4, 5, 4], # Power chords
        'edm':      [6, 4, 1, 5], # vi-IV-I-V (Emotional)
        'sad':      [6, 4, 5, 6],
        'heroic':   [1, 5, 4, 1],
    }

    @classmethod
    def get_chord_notes(cls, root_note: str, scale_type: str, degree: int, extension: int = 3) -> List[int]:
        """
        Generate MIDI note numbers for a chord.
        
        Args:
            root_note: e.g., 'C', 'F#'
            scale_type: e.g., 'major', 'minor'
            degree: Scale degree (1-based, e.g., 1 for tonic)
            extension: 3 for triad, 4 for 7th chord
            
        Returns:
            List of MIDI note numbers for the middle octave.
        """
        try:
            root_idx = cls.NOTES.index(root_note)
        except ValueError:
            root_idx = 0 # Default to C
            
        interval_pattern = cls.SCALES.get(scale_type, cls.SCALES['major'])
        
        # Calculate scale notes (spanning 2 octaves to handle overflow)
        scale_midi = []
        base_octave = 60 # C4
        
        # Build scale relative to root
        for octave in range(3):
            for interval in interval_pattern:
                scale_midi.append(base_octave + root_idx + interval + (octave * 12))
                
        # Select notes for the chord
        # degree 1 = index 0 in scale_midi
        base_index = degree - 1
        
        chord_notes = []
        for i in range(extension):
            # Take every other note (tertiary harmony)
            note_index = base_index + (i * 2)
            if note_index < len(scale_midi):
                chord_notes.append(scale_midi[note_index])
                
        return chord_notes

    @classmethod
    def get_progression(cls, genre: str) -> List[int]:
        """Returns list of scale degrees for a genre"""
        return cls.PROGRESSIONS.get(genre.lower(), cls.PROGRESSIONS['pop'])
