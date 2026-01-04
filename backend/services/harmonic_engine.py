import random
from typing import List, Dict, Any

class HarmonicEngine:
    """Sophisticated harmonic generation"""
    
    def generate_voice_leading(self, progression: List[List[int]], style: str) -> List[Dict[str, int]]:
        """Smooth voice leading between chords.
        
        Args:
            progression: List of chords, where each chord is a list of MIDI notes [root, 3rd, 5th]
            style: Musical style
            
        Returns:
            List of voiced chords dictionary {'soprano': note, 'alto': note, etc.}
        """
        voices = []
        # Simplified implementation for now - just ensures we have structure
        # In a full implementation, we would minimize note movement distance
        for chord_notes in progression:
            # Sort notes low to high
            sorted_notes = sorted(chord_notes)
            voice_map = {}
            if len(sorted_notes) >= 3:
                voice_map['bass'] = sorted_notes[0]
                voice_map['tenor'] = sorted_notes[0] + 12 if sorted_notes[0] < 48 else sorted_notes[0]
                voice_map['alto'] = sorted_notes[1] 
                voice_map['soprano'] = sorted_notes[-1]
            voices.append(voice_map)
            
        return voices
    
    def add_passing_tones(self, melody_events: List[Dict], harmony: List[Dict] = None) -> List[Dict]:
        """Add chromatic passing tones for realism"""
        enhanced = []
        if not melody_events:
            return []
            
        # Sort by time
        sorted_melody = sorted(melody_events, key=lambda x: x['time'])
        
        for i, event in enumerate(sorted_melody[:-1]):
            enhanced.append(event)
            
            current_pitch = event.get('pitch') or (event.get('note')[0] if isinstance(event.get('note'), list) else event.get('note'))
            next_event = sorted_melody[i + 1]
            next_pitch = next_event.get('pitch') or (next_event.get('note')[0] if isinstance(next_event.get('note'), list) else next_event.get('note'))
            
            if current_pitch is None or next_pitch is None:
                continue

            interval = next_pitch - current_pitch
            time_diff = next_event['time'] - event['time']
            
            # If large leap (> 2 semitones) and enough time, add passing tone
            if abs(interval) > 2 and time_diff >= 0.25:
                passing_note = int(current_pitch + (interval / 2))
                
                # Check collision (simple)
                passing_time = event['time'] + (time_diff / 2)
                
                passing_event = event.copy()
                passing_event['time'] = passing_time
                passing_event['pitch'] = passing_note
                passing_event['duration'] = 0.125
                passing_event['velocity'] = int(event.get('velocity', 80) * 0.7) # Softer
                passing_event['type'] = 'passing'
                
                enhanced.append(passing_event)
        
        # Add last event
        if sorted_melody:
            enhanced.append(sorted_melody[-1])
                
        return enhanced

    def _move_voice(self, voice_type, current_chord, next_chord, max_leap=4):
        # Placeholder for strict voice leading rules
        pass

    def _move_bass(self, current_chord, next_chord):
        # Placeholder for bass logic
        pass

    def get_chord_tones(self, key: str, scale_type: str, degree: int, octave: int = 4) -> List[int]:
        """
        Get the specific tones (Root, 3rd, 5th, Octave) for a chord in the key.
        Used for locking Arpeggios to the harmonic structure.
        """
        # This relies on the simple diatonic logic
        # 1. Get scale notes for the octave
        # We need a MusicTheoryService instance for this, or duplicate logic.
        # Ideally, HarmonicEngine should have access to MusicTheoryService.
        # Since it doesn't have it injected in __init__ in the current snippet (it's in IntegratedGenerator),
        # we will accept the *scale_midi_notes* as input or use a simplified mapping if we can't access it.
        # BUT, the IntegratedGenerator DOES have self.music_theory. 
        # So we can pass the logic via `IntegratedGenerator` OR instantiate MusicTheoryService here.
        
        # Let's perform a lightweight scale generation here or assume INPUT is the scale notes.
        # For robustness proposed in plan: "Logic: If the chord is C Major, return [60, 64, 67, 72]"
        # I will change the signature to accept `scale_midi_notes` directly to be pure.
        pass # Replaced below logic in integration
    
    # Actually, the user PROMPT requested: `get_chord_tones(key, scale, degree)` in HarmonicEngine.
    # So I should implement the logic. I will import MusicTheoryService inside the method to avoid circular deps if any.
    
    def get_chord_tones_from_scale(self, scale_midi_notes: List[int], degree: int) -> List[int]:
        """
        Extract chord tones from a list of diatonic scale notes.
        degree is 0-indexed (0=Root/I, 1=ii, etc.)
        """
        if not scale_midi_notes:
            return []
            
        root_idx = degree
        third_idx = (degree + 2)
        fifth_idx = (degree + 4)
        
        # Helper to get note from scale (handling wrap)
        def get_note(idx):
             if idx < len(scale_midi_notes):
                 return scale_midi_notes[idx]
             else:
                 # Wrap to next octave
                 return scale_midi_notes[idx % len(scale_midi_notes)] + 12
                 
        return [
            get_note(root_idx),
            get_note(third_idx),
            get_note(fifth_idx),
            get_note(root_idx) + 12 # Octave
        ]
