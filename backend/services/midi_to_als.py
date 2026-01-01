# Save this as: backend/services/midi_to_als.py

from typing import List, Dict

class MIDIToAbletonConverter:
    """
    Converts MIDI data to Ableton clip format
    """
    
    # MIDI note names for drums (General MIDI)
    DRUM_MAP = {
        'kick': 36,      # C1
        'snare': 38,     # D1  
        'hihat_closed': 42,  # F#1
        'hihat_open': 46,    # A#1
        'clap': 39,      # D#1
        'rim': 37,       # C#1
        'tom_low': 41,   # F1
        'tom_mid': 43,   # G1
        'tom_high': 45,  # A1
        'crash': 49,     # C#2
        'ride': 51,      # D#2
    }
    
    @staticmethod
    def pattern_to_notes(pattern: Dict, bars: int = 4) -> List[Dict]:
        """
        Convert pattern dictionary to Ableton note format
        """
        notes = []
        
        if not pattern:
            return notes
            
        for instrument, positions in pattern.items():
            if instrument in MIDIToAbletonConverter.DRUM_MAP:
                pitch = MIDIToAbletonConverter.DRUM_MAP[instrument]
            else:
                try:
                    pitch = int(instrument)
                except:
                    continue
            
            for pos in positions:
                time = pos * 0.25  # Each 16th note is 0.25 beats
                
                note = {
                    'pitch': pitch,
                    'time': time,
                    'duration': 0.25,
                    'velocity': 100
                }
                
                notes.append(note)
        
        return notes