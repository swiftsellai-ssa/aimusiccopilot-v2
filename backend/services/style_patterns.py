from typing import Dict, List, Optional
import random

class StylePatterns:
    """
    Central repository for musical style patterns and definitions.
    Includes explicit drum patterns and instrument behaviors for various genres.
    """
    
    PATTERNS: Dict[str, Dict] = {
        # --- Electronic Genres ---
        'techno': {
            'kick': {'base': [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]}, # Four-on-the-floor
            'hat':  {'base': [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0]}, # Off-beat
            'snare':{'base': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]}, # Claps on 2 & 4
            'perc': {'base': [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]},
            'bass': {'base': [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0]}, # Off-beat rumble
            'chords': {'base': [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0]}, # Off-beat stabs (Techno)
        },
        'house': {
            'kick': {'base': [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]},
            'hat':  {'base': [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0]},
            'snare':{'base': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]}, # Clap
            'shake':{'base': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]}, # Shaker
            'bass': {'base': [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0]}, # Classic House Off-beat
            'chords': {'base': [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0]}, # House Stabs
        },
        'trap': {
            'kick': {'base': [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0]}, # Syncopated
            'hat':  {'base': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]}, # 16ths (often rolled)
            'snare':{'base': [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]}, # Snare on 3
            'bass': {'base': [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0]}, # Sparse 808
            'chords': {'base': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}, # Trap long sustain (1 per bar)
        },
        'dnb': {
            'kick': {'base': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]}, # Breakbeat
            'hat':  {'base': [1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1]},
            'snare':{'base': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]},
        },
        
        # --- Acoustic / Band Genres ---
        'pop': {
            'kick': {'base': [1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0]}, # Pop groove
            'hat':  {'base': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]}, # 8ths
            'snare':{'base': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]}, # 2 & 4
            'tom':  {'base': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0]}, # Simple fill
            'bass': {'base': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]}, # Root Pulse
            'chords': {'base': [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]}, # Pop half notes
        },
        'rock': {
            'kick': {'base': [1, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 1, 0, 0, 0]}, # Driving rock
            'hat':  {'base': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]}, # Open/Closed interplay
            'snare':{'base': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]}, # Hard 2 & 4
            'crash':{'base': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}, # Crash on 1
            'bass': {'base': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]}, # Driving 8ths
        },
        'indie': {
            'kick': {'base': [1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0]}, # Syncopated indie
            'hat':  {'base': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]}, # 16ths on hi-hat/shaker
            'snare':{'base': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]},
            'bass': {'base': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]},
            'chords': {'base': [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]},
        },
        'funk': {
            'kick': {'base': [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0]}, # Funky syncopation (the "One")
            'hat':  {'base': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]},
            'snare':{'base': [0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 1]}, # Ghost notes
            'shake':{'base': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]},
        },
        'disco': {
            'kick': {'base': [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]}, # Four-on-the-floor
            'hat':  {'base': [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0]}, # Open hat offbeat
            'snare':{'base': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]},
            'perc': {'base': [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0]},
        },
        
        # --- Urban / Soul ---
        'hip_hop': {
            'kick': {'base': [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0]}, # Boom Bap
            'hat':  {'base': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]}, # Loose 8ths
            'snare':{'base': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]},
            'bass': {'base': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]},
            'chords': {'base': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
        },
        'boom_bap': {
            'kick': {'base': [1, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0, 0]},
            'snare': {'base': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]},
            'hat': {'base': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]},
            'bass': {'base': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]},
            'chords': {'base': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
        },
        'soul': {
            'kick': {'base': [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]}, # Sparse
            'hat':  {'base': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]}, # Gentle
            'snare':{'base': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]}, # Laid back rimshot
        },
        'jazz': {
            'kick': {'base': [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0]}, # Feathering
            'hat':  {'base': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]}, # Pedal hat on 2 & 4
            'ride': {'base': [1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 1, 0, 0, 1, 1, 0]}, # Typical Swing Ride Pattern
            'snare':{'base': [0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0]}, # Comping
            'bass': {'base': [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]}, # Walking Bass (Quarter notes)
            'chords': {'base': [0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]}, # Jazz Comping (Syncopated)
        },
        'latin': {
            'kick': {'base': [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0]}, # Tresillo rhythm
            'snare':{'base': [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]}, # Cross-stick rar
            'hat':  {'base': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]},
            'perc': {'base': [1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0]}, # Clave (Son)
            'bass': {'base': [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1]}, # Tumbao (User Verified)
            'chords': {'base': [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0]}, # Pian montuno pe off-beat
        },
        
        # --- Heavy ---
        'metal': {
            'kick': {'base': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]}, # Double bass
            'hat':  {'base': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]},
            'snare':{'base': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]},
            'crash':{'base': [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0]},
            'bass': {'base': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]},
            'chords': {'base': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]},
        },
        'punk': {
            'kick': {'base': [1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0]}, # Fast
            'hat':  {'base': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]},
            'snare':{'base': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]},
        },
        'cinematic': {
            'kick': {'base': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0]}, # Very sparse
            'hat':  {'base': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}, # Minimal
            'snare':{'base': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}, # None or generic rim
            'perc': {'base': [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0]}, # Orchestral/processed perc
        },

        
        # --- Latin / Global ---
        'reggaeton': {
            'kick': {'base': [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]}, # Four on floor usually
            'snare':{'base': [0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0]}, # Dembow rhythm (3-3-2 feel)
            'hat':  {'base': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]},
        },
        'afrobeat': {
            'kick': {'base': [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0]}, # Clave feel
            'snare':{'base': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]},
            'hat':  {'base': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]},
            'perc': {'base': [0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0]}, # Poly
        },
        'lofi': {
            'kick': {'base': [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0]}, # Laid back
            'snare':{'base': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]}, # Hard 2 & 4 but swung
            'hat':  {'base': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]}, 
            'perc': {'base': [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1]}, # Vinyl crackle or foley
            'chords': {'base': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}, # Lofi Pad Sustain
        },
        'dubstep': {
             # Half-time feel
            'kick': {'base': [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]},
            'snare': {'base': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]},
            'hat': {'base': [1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1]},
            'bass': {'base': [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]}, # Wobble placeholder
            'chords': {'base': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
        },
        'ambient': {
            'kick': {'base': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}, # Rare pulse
            'snare': {'base': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
            'hat': {'base': [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]},
            'pad': {'base': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]}, # Drone
            'chords': {'base': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]},
        },
        'gospel': {
            'kick': {'base': [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0]}, # Soulful
            'snare': {'base': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]},
            'hat': {'base': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]},
            'bass': {'base': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]},
            'chords': {'base': [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]},
        },
        'deep_house': {
             # Similar to house
            'kick': {'base': [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]},
            'snare': {'base': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0]},
            'hat': {'base': [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0]},
            'bass': {'base': [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0]},
            'chords': {'base': [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0]},
        }
    }

    @classmethod
    def get_pattern(cls, style: str, instrument: str) -> List[int]:
        """
        Retrieve pattern for a specific style and instrument.
        Uses fallback logic if specific pattern is missing.
        """
        style_key = style.lower()
        if style_key not in cls.PATTERNS:
            style_key = 'techno' # Default fallback
            
        style_data = cls.PATTERNS[style_key]
        
        # Direct match
        if instrument in style_data:
            return style_data[instrument]['base']
            
        # Fallbacks
        normalized_instr = instrument.lower()
        if 'kick' in normalized_instr:
            return style_data.get('kick', cls.PATTERNS['techno']['kick'])['base']
        elif 'snare' in normalized_instr or 'clap' in normalized_instr:
            return style_data.get('snare', cls.PATTERNS['techno']['snare'])['base']
        elif 'hat' in normalized_instr or 'hh' in normalized_instr:
            return style_data.get('hat', cls.PATTERNS['techno']['hat'])['base']
        elif 'ride' in normalized_instr:
            return style_data.get('ride', style_data.get('hat', cls.PATTERNS['jazz']['hat']))['base']
            
        # Generic silence
        return [0] * 16

    @classmethod
    def get_style_metadata(cls, style: str) -> Dict:
        """Returns recommended BPM and swing for a style"""
        meta = {
            'techno': {'bpm': 130, 'swing': 0.0},
            'house':  {'bpm': 124, 'swing': 0.1},
            'trap':   {'bpm': 140, 'swing': 0.0},
            'dnb':    {'bpm': 174, 'swing': 0.0},
            'pop':    {'bpm': 100, 'swing': 0.0},
            # Rock updated as requested
            'rock':   {'bpm': 130, 'swing': 0.05, 'energy': 'high', 'velocity_range': (90, 127)},
            'indie':  {'bpm': 120, 'swing': 0.1},
            'funk':   {'bpm': 105, 'swing': 0.25},
            'disco':  {'bpm': 120, 'swing': 0.05},
            'hiphop': {'bpm': 90,  'swing': 0.2},
            'soul':   {'bpm': 80,  'swing': 0.3},
            # Jazz with Energy
            'jazz':   {'bpm': 120, 'swing': 0.6, 'energy': 'medium'}, 
            'latin':  {'bpm': 100, 'swing': 0.0},
            'metal':  {'bpm': 160, 'swing': 0.0},
            'punk':   {'bpm': 180, 'swing': 0.0},
            # Cinematic added
            'cinematic': {'bpm': 70, 'swing': 0.0, 'energy': 'low'},
        }
        return meta.get(style.lower(), {'bpm': 120, 'swing': 0.0})
