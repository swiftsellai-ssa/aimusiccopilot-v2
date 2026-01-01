# backend/services/chord_progression_generator.py

class ChordProgressionGenerator:
    def __init__(self, music_theory_service):
        self.theory = music_theory_service
        
        # Emotional chord progression mappings
        self.emotion_progressions = {
            'sad': {
                'progression': ['i', 'VI', 'III', 'VII'],
                'rhythm': [4, 4, 4, 4],  # Beats per chord
                'inversions': [0, 1, 0, 0],  # Which inversion to use
                'extensions': ['', '', 'add9', '']  # Add extensions
            },
            'uplifting': {
                'progression': ['I', 'V', 'vi', 'IV'],
                'rhythm': [4, 4, 4, 4],
                'inversions': [0, 0, 1, 0],
                'extensions': ['', 'sus4', '', 'add9']
            },
            'dark': {
                'progression': ['i', 'bII', 'v', 'i'],
                'rhythm': [4, 2, 2, 4],
                'inversions': [0, 0, 1, 0],
                'extensions': ['', 'maj7', 'dim', '']
            },
            'energetic': {
                'progression': ['I', 'I', 'IV', 'V'],
                'rhythm': [2, 2, 2, 2],
                'inversions': [0, 2, 1, 0],
                'extensions': ['', '', 'sus2', '7']
            }
        }
        
        # Voice leading rules
        self.voice_leading_rules = {
            'smooth': 'minimize_movement',
            'dramatic': 'maximize_contrast',
            'classical': 'avoid_parallels'
        }
    
    def generate_chord_progression(self,
                                  key: str,
                                  scale: str,
                                  emotion: str,
                                  bars: int = 8) -> List[Dict]:
        """Generate sophisticated chord progression"""
        
        root_midi = self.theory.get_midi_root(key, octave=3)
        progression_template = self.emotion_progressions.get(emotion, self.emotion_progressions['uplifting'])
        
        chords = []
        current_time = 0
        
        for idx, (chord_symbol, rhythm, inversion, extension) in enumerate(zip(
            progression_template['progression'],
            progression_template['rhythm'],
            progression_template['inversions'],
            progression_template['extensions']
        )):
            # Parse chord symbol
            chord_notes = self._build_chord(root_midi, scale, chord_symbol, inversion, extension)
            
            # Apply voice leading
            if idx > 0 and chords:
                chord_notes = self._apply_voice_leading(
                    chords[-1]['notes'], 
                    chord_notes,
                    'smooth'
                )
            
            # Add rhythmic pattern to chord
            chord_rhythm = self._generate_chord_rhythm(rhythm)
            
            for hit in chord_rhythm:
                chords.append({
                    'time': current_time + hit['time'],
                    'notes': chord_notes,
                    'velocity': hit['velocity'],
                    'duration': hit['duration']
                })
            
            current_time += rhythm
        
        return chords
    
    def _build_chord(self, root, scale, chord_symbol, inversion, extension):
        """Build chord with inversions and extensions"""
        # Parse roman numeral
        is_minor = chord_symbol[0].islower()
        degree = self._roman_to_degree(chord_symbol.upper().strip('B'))
        
        # Get scale notes
        scale_notes = self.theory.get_scale_notes(root, scale)
        
        # Build basic triad
        chord_root = scale_notes[degree - 1]
        third = chord_root + (3 if is_minor else 4)
        fifth = chord_root + 7
        
        notes = [chord_root, third, fifth]
        
        # Add extensions
        if 'add9' in extension:
            notes.append(chord_root + 14)  # Add 9th
        elif '7' in extension:
            notes.append(chord_root + 10 if is_minor else 11)  # Add 7th
        elif 'sus2' in extension:
            notes[1] = chord_root + 2  # Replace 3rd with 2nd
        elif 'sus4' in extension:
            notes[1] = chord_root + 5  # Replace 3rd with 4th
            
        # Apply inversion
        for _ in range(inversion):
            notes[0] += 12  # Move lowest note up octave
            notes.sort()
            
        return notes
    
    def _apply_voice_leading(self, prev_chord, next_chord, style):
        """Smart voice leading between chords"""
        if style == 'smooth':
            # Minimize movement between chords
            optimized = []
            for next_note in next_chord:
                # Find closest previous note
                distances = [abs(next_note - prev) for prev in prev_chord]
                closest_prev = prev_chord[distances.index(min(distances))]
                
                # Move by smallest interval
                if abs(next_note - closest_prev) > 6:  # More than tritone
                    # Try octave displacement
                    if next_note > closest_prev:
                        next_note -= 12
                    else:
                        next_note += 12
                        
                optimized.append(next_note)
            return optimized
        
        return next_chord
    
    def _generate_chord_rhythm(self, beats):
        """Generate rhythmic pattern for chord"""
        patterns = {
            1: [{'time': 0, 'duration': 0.25, 'velocity': 100}],
            2: [
                {'time': 0, 'duration': 0.25, 'velocity': 100},
                {'time': 1, 'duration': 0.25, 'velocity': 80}
            ],
            4: [
                {'time': 0, 'duration': 1, 'velocity': 100},
                {'time': 2, 'duration': 0.5, 'velocity': 70},
                {'time': 3, 'duration': 0.5, 'velocity': 70}
            ]
        }
        return patterns.get(beats, patterns[4])
    
    def _roman_to_degree(self, roman):
        """Convert roman numeral to scale degree"""
        numerals = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5, 'VI': 6, 'VII': 7}
        return numerals.get(roman, 1)