import random
import math
from typing import List, Dict

class VelocityAutomation:
    """Realistic velocity patterns"""
    
    def __init__(self):
        self.CURVES = {
            'human_drummer': lambda t: 80 + 20 * math.sin(t * math.pi) + random.randint(-5, 5), # Added +/- 5 variance
            'machine_gun': lambda t: 127,
            'crescendo': lambda t: 20 + (107 * t),
            'diminuendo': lambda t: 127 - (107 * t),
            'accent_pattern': lambda t: 127 if int(t * 16) % 4 == 0 else 80,
            'jazz_brush': lambda t: 60 + 10 * math.sin(t * 2 * math.pi) + random.gauss(0, 3),
            'natural': lambda t: 90 + random.gauss(0, 5) # Default
        }
    
    def apply_velocity_curve(self, events: List[Dict], curve_type: str = 'natural', intensity: float = 1.0) -> List[Dict]:
        """Apply realistic velocity curves"""
        curve = self.CURVES.get(curve_type, self.CURVES['natural'])
        
        if not events:
            return []
            
        max_time = max((e['time'] for e in events), default=1)
        if max_time == 0: max_time = 1
        
        for event in events:
            t = event['time'] / max_time  # Normalized time 0-1
            
            # Calculate base velocity
            try:
                base_velocity = curve(t)
            except Exception:
                base_velocity = 90
                
            # Apply intensity scaling
            final_velocity = int(base_velocity * intensity)
            
            # Constrain to valid MIDI range (0-127). Note-on usually > 0
            final_velocity = max(1, min(127, final_velocity))
            
            event['velocity'] = final_velocity
            
        return events

class ArticulationEngine:
    """Add musical articulations"""
    
    def add_articulations(self, notes: List[Dict], style: str) -> List[Dict]:
        """Add staccato, legato, accents"""
        articulated = []
        
        for i, note in enumerate(notes):
            # Determine articulation
            if style == 'classical' or style == 'cinematic':
                if i % 4 == 0:  # Accent first beat of bar roughly
                    note['articulation'] = 'accent'
                    note['velocity'] = min(127, int(note.get('velocity', 90) * 1.2))
                    
            elif style == 'jazz':
                if random.random() < 0.3:
                    note['articulation'] = 'staccato'
                    note['duration'] = note.get('duration', 0.25) * 0.5
                    
            elif style in ['techno', 'house', 'electronic']:
                p = note.get('pitch') or (note.get('note') if isinstance(note.get('note'), int) else 0)
                if p in [36, 38]:  # Kick and snare
                    note['articulation'] = 'punch'
                    # note['attack'] = 0.001 # Not used in MIDI directly but conceptual
                    
            articulated.append(note)
            
        return articulated

class ProductionEngine:
    """Facade for production features"""
    def __init__(self):
        self.velocity = VelocityAutomation()
        self.articulation = ArticulationEngine()
