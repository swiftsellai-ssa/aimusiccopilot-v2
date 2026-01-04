import random
from typing import List, Dict

class RhythmEngine:
    """Complex rhythm generation"""
    
    def generate_polyrhythm(self, base_rhythm: List[Dict], overlay_ratio='3:2', total_bars=1) -> List[Dict]:
        """Create polyrhythmic patterns
        
        Args:
            base_rhythm: Existing events
            overlay_ratio: String like '3:2' (3 beats against 2)
        """
        try:
            numerator, denominator = map(int, overlay_ratio.split(':'))
        except ValueError:
            return base_rhythm

        # Simple implementation: Add accents at calculated intervals
        # Ideally this generates a new layer of events
        
        # Determine total duration
        if not base_rhythm:
            return []
            
        max_time = max(e['time'] for e in base_rhythm)
        step = max_time / numerator
        
        overlay_events = []
        for i in range(numerator):
            time = i * step
            overlay_events.append({
                'time': time,
                'duration': 0.1,
                'velocity': 90,
                'type': 'polyrhythm_accent'
            })
            
        # Combine? For now just return base, this is a placeholder for the logic
        # Real implementation needs to merge intelligentely
        return base_rhythm
    
    def add_ghost_notes(self, pattern: List[Dict], style: str) -> List[Dict]:
        """Add ghost notes for realism based on style"""
        # Tuned probabilities for better distinctness
        ghost_probability = {
            'jazz': 0.35,      # High ghost note usage
            'funk': 0.30,      # Busy snares
            'groove_bass': 0.25,
            'hip_hop': 0.20,   # Significant for boom-bap feel
            'trap': 0.15,      # Rolling hi-hats handle most, but some ghost snares
            'rock': 0.15,
            'electronic': 0.05, # Very clean
            'techno': 0.02,     # Machine precision
            'house': 0.05
        }.get(style, 0.1)
        
        enhanced = []
        for note in pattern:
            enhanced.append(note)
            
            # Only add ghost notes to drums usually, or percussive instruments
            # Assuming 'note' here is an event dict
            
            # Don't add ghost notes if duration is long (it's a melody/chord)
            if note.get('duration', 0) > 0.5:
                continue
                
            if random.random() < ghost_probability:
                ghost_event = note.copy()
                # Place ghost note slightly after main note (syncopated 1/16th)
                ghost_event['time'] = note['time'] + 0.125 
                # Velocity reduced to 30% for subtlety (User Request)
                ghost_event['velocity'] = max(1, int(note.get('velocity', 80) * 0.3)) 
                ghost_event['type'] = 'ghost'
                
                enhanced.append(ghost_event)
                
        return enhanced
