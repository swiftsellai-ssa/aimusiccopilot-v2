import random

class MusicTheoryEngine:
    """
    The Harmonic Brain of amc.
    Translates musical styles into intelligent chord progressions and voice leading.
    """

    # 🎼 Style-Specific Progression Templates (Roman Numerals)
    PROGRESSIONS = {
        'pop': [
            ['I', 'V', 'vi', 'IV'],   # The "Axis of Awesome"
            ['I', 'vi', 'IV', 'V'],   # 50s Progression
            ['vi', 'IV', 'I', 'V']    # Emotional Pop
        ],
        'jazz': [
            ['ii', 'V', 'I', 'vi'],   # Standard Turnaround
            ['ii7', 'V7', 'Imaj7'],   # Classic ii-V-I
            ['Imaj7', 'vi7', 'ii7', 'V7'] # 1-6-2-5
        ],
        'trap': [
            ['i', 'VI', 'III', 'VII'], # Dark Minor
            ['i', 'iv', 'v', 'i'],     # Harmonic Minor feel
            ['i', 'VI', 'iv', 'V']     # Creepy Trap
        ],
        'lofi': [
            ['Imaj7', 'IVmaj7'],       # Chill 2-chord loop
            ['ii9', 'V13', 'Imaj7'],   # Extended Jazz-Hop
            ['vi9', 'ii9', 'V7', 'Imaj7']
        ],
        'house': [
            ['i', 'VII', 'VI', 'VII'], # Deep House Walk
            ['i', 'iii', 'iv', 'v'],   # Minor groove
            ['i', 'i', 'VI', 'VII']
        ],
        'rnb': [
            ['IVmaj7', 'iii7', 'ii7', 'Imaj7'], # Descending Soul
            ['ii9', 'Imaj7', 'ii9', 'Imaj7']    # Neo-Soul vamp
        ],
        'generic': [['I', 'IV', 'V', 'I']] # Fallback
    }

    # 🎹 Roman Numeral to Scale Degree & Chord Type Map
    ROMAN_MAP = {
        # Major Scale
        'I': (0, 'maj'), 'ii': (2, 'min'), 'iii': (4, 'min'), 
        'IV': (5, 'maj'), 'V': (7, 'dom'), 'vi': (9, 'min'), 'vii': (11, 'dim'),
        'Imaj7': (0, 'maj7'), 'IVmaj7': (5, 'maj7'),
        
        # Minor Scale (Natural/Harmonic context)
        'i': (0, 'min'), 'III': (3, 'maj'), 'iv': (5, 'min'), 
        'v': (7, 'min'), 'VI': (8, 'maj'), 'VII': (10, 'maj'),
        
        # Extended/Jazz
        'ii7': (2, 'min7'), 'V7': (7, 'dom7'), 'iii7': (4, 'min7'), 
        'vi7': (9, 'min7'), 'ii9': (2, 'min9'), 'V13': (7, 'dom13')
    }

    # 🧮 Interval Definitions
    CHORD_INTERVALS = {
        'maj': [0, 4, 7],
        'min': [0, 3, 7],
        'dim': [0, 3, 6],
        'dom': [0, 4, 7], # Basic major for simple
        'maj7': [0, 4, 7, 11],
        'min7': [0, 3, 7, 10],
        'dom7': [0, 4, 7, 10],
        'min9': [0, 3, 7, 10, 14],
        'dom13': [0, 4, 7, 10, 14, 21]
    }

    def generate_progression(self, style: str, root_key_midi: int, scale_type: str = 'major'):
        """
        Returns a list of chord objects: [{'root': 60, 'intervals': [0, 4, 7], 'type': 'I'}, ...]
        """
        # 1. Select Template
        # Alias Map for styles not explicitly defined
        style_map = {
             'boom_bap': 'trap', # Dark/Minor
             'hip_hop': 'trap',
             'indie': 'pop',
             'metal': 'rock', 
             'punk': 'rock',
             'deep_house': 'house',
             'soul': 'rnb',
             'latin': 'pop', # or jazz? Let's go with pop/major for now
             'reggaeton': 'pop',
             'afrobeat': 'pop',
             'funk': 'pop',
             'disco': 'pop',
             'dubstep': 'trap', # Dark/Minor
             'ambient': 'lofi', # Chill/Atmospheric
             'gospel': 'rnb',   # Soulful
             'cinematic': 'trap' # Dramatic/Minor
        }
        
        search_style = style_map.get(style.lower(), style.lower())
        templates = self.PROGRESSIONS.get(search_style, self.PROGRESSIONS['generic'])
        selected_progression = random.choice(templates)
        
        full_progression = []

        # 2. Translate Roman Numerals to MIDI
        for roman in selected_progression:
            # Parse Roman Numeral
            degree_offset, chord_type = self._parse_roman(roman)
            
            # Calculate actual root note
            chord_root = root_key_midi + degree_offset
            
            # Get intervals
            intervals = self.CHORD_INTERVALS.get(chord_type, [0, 4, 7])
            
            full_progression.append({
                'root': chord_root,
                'intervals': intervals,
                'name': roman,
                'absolute_notes': [chord_root + interval for interval in intervals]
            })
            
        return full_progression

    def get_chord_tones(self, chord_obj):
        """Helper to extract playable notes for Arpeggiators/Melodies"""
        return chord_obj['absolute_notes']

    def _parse_roman(self, roman):
        """Safe lookup for Roman numerals"""
        if roman in self.ROMAN_MAP:
            return self.ROMAN_MAP[roman]
        # Default fallback if unknown
        return (0, 'maj')