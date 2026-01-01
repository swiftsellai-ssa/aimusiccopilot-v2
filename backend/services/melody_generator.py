# backend/services/melody_generator.py

class MelodyGenerator:
    def __init__(self, theory_service):
        self.theory = theory_service
        
        # Melodic patterns and shapes
        self.melodic_shapes = {
            'ascending': [0, 1, 2, 3, 4, 5, 6, 7],
            'descending': [7, 6, 5, 4, 3, 2, 1, 0],
            'arch': [0, 2, 4, 5, 4, 2, 1, 0],
            'wave': [0, 2, 1, 3, 2, 4, 3, 1],
            'leap': [0, 4, 2, 5, 1, 5, 3, 0],
            'pedal': [0, 0, 1, 0, 2, 0, 3, 0]
        }
        
        # Rhythm patterns for different styles
        self.rhythm_patterns = {
            'flowing': [1, 1, 1, 1, 2, 2],  # Mix of quarters and halfs
            'staccato': [0.5, 0.5, 0.5, 0.5, 1, 1, 1, 1],  # Short notes
            'syncopated': [0.75, 0.25, 1, 0.5, 0.5, 1],
            'triplet': [0.33, 0.33, 0.34, 1, 1],
            'legato': [4, 2, 2]  # Long notes
        }
    
    def generate_melody(self,
                       key: str,
                       scale: str,
                       chord_progression: List[Dict],
                       style: str = 'flowing',
                       shape: str = 'arch',
                       bars: int = 8) -> List[Dict]:
        """Generate melody that follows chord progression"""
        
        scale_notes = self.theory.get_scale_notes(key, scale, octave=5)
        melody_shape = self.melodic_shapes.get(shape, self.melodic_shapes['arch'])
        rhythm_pattern = self.rhythm_patterns.get(style, self.rhythm_patterns['flowing'])
        
        melody = []
        current_time = 0
        
        # Analyze chord progression to find strong tones
        for bar_idx in range(bars):
            current_chord = self._get_current_chord(chord_progression, bar_idx * 4)
            chord_tones = current_chord['notes'] if current_chord else [60, 64, 67]
            
            # Generate melodic phrase
            phrase = self._generate_phrase(
                scale_notes,
                chord_tones,
                melody_shape,
                rhythm_pattern
            )
            
            # Add phrase to melody
            for note in phrase:
                melody.append({
                    'time': current_time,
                    'pitch': note['pitch'],
                    'velocity': note['velocity'],
                    'duration': note['duration']
                })
                current_time += note['duration']
        
        # Add ornamentations
        melody = self._add_ornamentations(melody, style)
        
        return melody
    
    def _generate_phrase(self, scale_notes, chord_tones, shape, rhythm):
        """Generate a melodic phrase"""
        phrase = []
        shape_index = 0
        
        for rhythm_value in rhythm:
            # Pick note based on shape and chord tones
            scale_degree = shape[shape_index % len(shape)]
            base_note = scale_notes[scale_degree % len(scale_notes)]
            
            # Prefer chord tones on strong beats
            if shape_index % 2 == 0:  # Strong beat
                # Find closest chord tone
                distances = [abs(base_note - ct) for ct in chord_tones]
                if min(distances) < 3:  # Within minor third
                    base_note = chord_tones[distances.index(min(distances))]
            
            # Add passing tones and neighbor notes
            if rhythm_value < 0.5 and random.random() > 0.7:
                # Add passing tone
                phrase.append({
                    'pitch': base_note - 1,
                    'velocity': 60,
                    'duration': rhythm_value / 2
                })
                phrase.append({
                    'pitch': base_note,
                    'velocity': 80,
                    'duration': rhythm_value / 2
                })
            else:
                phrase.append({
                    'pitch': base_note,
                    'velocity': 70 + random.randint(-10, 20),
                    'duration': rhythm_value
                })
            
            shape_index += 1
        
        return phrase
    
    def _add_ornamentations(self, melody, style):
        """Add grace notes, slides, and other ornamentations"""
        if style == 'staccato':
            # Add grace notes
            ornamented = []
            for note in melody:
                if random.random() > 0.8 and note['duration'] > 0.25:
                    # Add grace note
                    ornamented.append({
                        'time': note['time'] - 0.0625,
                        'pitch': note['pitch'] - 1,
                        'velocity': 50,
                        'duration': 0.0625
                    })
                ornamented.append(note)
            return ornamented
            
        elif style == 'flowing':
            # Add slides between notes
            ornamented = []
            for i, note in enumerate(melody):
                ornamented.append(note)
                if i < len(melody) - 1:
                    next_note = melody[i + 1]
                    pitch_diff = abs(next_note['pitch'] - note['pitch'])
                    if pitch_diff > 2 and pitch_diff < 7:
                        # Add slide
                        ornamented.append({
                            'time': note['time'] + note['duration'] - 0.125,
                            'pitch': (note['pitch'] + next_note['pitch']) // 2,
                            'velocity': 40,
                            'duration': 0.125
                        })
            return ornamented
            
        return melody
    
    def _get_current_chord(self, progression, time):
        """Find which chord is playing at given time"""
        for chord in progression:
            if chord['time'] <= time < chord['time'] + chord.get('duration', 4):
                return chord
        return None