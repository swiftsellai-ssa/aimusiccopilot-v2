import random

class MusicTheoryService:
    def __init__(self):
        self.NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        # DEFINIȚII ACORDURI (Intervale)
        self.CHORD_INTERVALS = {
            'maj': [0, 4, 7],
            'min': [0, 3, 7],
            'dim': [0, 3, 6],
            'aug': [0, 4, 8],
            '7': [0, 4, 7, 10],
            'maj7': [0, 4, 7, 11],
            'min7': [0, 3, 7, 10],
            'sus4': [0, 5, 7],
            'power': [0, 7]
        }

        # PROGRESII SPECIFICE GENURILOR (Din Planul Tau)
        self.STYLE_PROGRESSIONS = {
            'pop':  ['I', 'V', 'vi', 'IV'],          # Classic Pop
            'rock': ['I', 'IV', 'V', 'IV'],          # Classic Rock
            'jazz': ['ii', 'V', 'I', 'vi'],          # ii-V-I
            'blues': ['I', 'IV', 'I', 'V'],          # Simplified Blues
            'trap': ['i', 'VI', 'III', 'VII'],       # Dark/Epic
            'house': ['i', 'III', 'VII', 'i'],       # Deep House Loop
            'techno': ['i', 'i', 'i', 'i'],          # Static / Hypnotic
            'lofi': ['ii', 'V', 'I', 'I'],           # Chill
            'cinematic': ['i', 'VI', 'i', 'VI']      # Dramatic
        }

    def get_progression(self, style: str, key: str, scale_type: str = 'minor'):
        """Returnează o listă de acorduri (ex: ['Cmaj', 'Gmaj', 'Amin', 'Fmaj'])"""
        
        # 1. Alegem șablonul (Roman Numerals)
        style_key = style.lower() if style.lower() in self.STYLE_PROGRESSIONS else 'pop'
        roman_progression = self.STYLE_PROGRESSIONS.get(style_key)
        
        # 2. Calculăm notele gamei
        scale_notes = self._get_scale_notes(key, scale_type)
        
        # 3. Traducem Cifre Romane -> Acorduri Reale
        chord_progression = []
        for roman in roman_progression:
            # Check if we have enough notes for the degree
            # (Basic safe-guard)
            chord_name = self._roman_to_chord(roman, scale_notes)
            chord_progression.append(chord_name)
            
        return chord_progression

    def get_chord_notes(self, root_note: str, chord_type: str, octave: int = 4):
        """Returnează notele MIDI"""
        # Curățare input
        clean_type = 'maj'
        # Basic parsing
        if 'min' in chord_type.lower() or 'm' == chord_type: clean_type = 'min'
        elif 'dim' in chord_type.lower(): clean_type = 'dim'
        elif '7' in chord_type: clean_type = '7'
        elif 'aug' in chord_type.lower(): clean_type = 'aug'
        elif 'sus' in chord_type.lower(): clean_type = 'sus4'
        elif 'pow' in chord_type.lower(): clean_type = 'power'
        
        intervals = self.CHORD_INTERVALS.get(clean_type, [0, 4, 7])
        base_midi = self._note_to_midi(root_note, octave)
        
        return [base_midi + interval for interval in intervals]
    
    # --- COMPATIBILITY LAYER ---
    def get_scale_notes(self, root: str, scale_type: str, octave: int = 3) -> list:
        """
        Public method to get MIDI notes for a scale.
        Used by IntegratedMidiGenerator.
        """
        note_names = self._get_scale_notes(root, scale_type)
        midi_notes = []
        for n in note_names:
            midi_notes.append(self._note_to_midi(n, octave))
        return midi_notes

    # --- HELPERS ---

    def _get_scale_notes(self, root: str, scale_type: str):
        """Generează toate notele dintr-o gamă"""
        start_idx = self._note_to_index(root)
        
        # Intervale (Major vs Minor)
        if scale_type == 'major':
            intervals = [2, 2, 1, 2, 2, 2, 1]
        else: # minor
            intervals = [2, 1, 2, 2, 1, 2, 2]
            
        notes = []
        current_idx = start_idx
        notes.append(self.NOTES[current_idx])
        
        for interval in intervals[:-1]: # Putem sări peste ultima
            current_idx = (current_idx + interval) % 12
            notes.append(self.NOTES[current_idx])
            
        return notes

    def _roman_to_chord(self, roman: str, scale_notes: list):
        """Convertește 'vi' în 'Amin' (dacă suntem în C Major)"""
        # Harta simplificată a gradelor (0-indexed)
        # I=0, ii=1, iii=2, IV=3, V=4, vi=5, vii=6
        degree_map = {'i': 0, 'ii': 1, 'iii': 2, 'iv': 3, 'v': 4, 'vi': 5, 'vii': 6}
        
        clean_roman = roman.lower()
        degree_idx = degree_map.get(clean_roman, 0)
        
        # Luăm nota rădăcină din gamă
        if not scale_notes: return "Cmaj" # Fallback
        
        root = scale_notes[degree_idx % len(scale_notes)]
        
        # Determinăm dacă e major (Uppercase 'V') sau minor (Lowercase 'v')
        is_major = roman[0].isupper()
        quality = 'maj' if is_major else 'min'
        
        return f"{root}{quality}"

    def _note_to_midi(self, note: str, octave: int) -> int:
        idx = self._note_to_index(note)
        return (octave + 1) * 12 + idx

    def _note_to_index(self, note: str):
        note = note.upper().replace('VB', 'B')
        if note not in self.NOTES and '#' in note:
             # Logică simplă pentru diez
             base = note[0]
             if base in self.NOTES:
                 return (self.NOTES.index(base) + 1) % 12
        return self.NOTES.index(note) if note in self.NOTES else 0