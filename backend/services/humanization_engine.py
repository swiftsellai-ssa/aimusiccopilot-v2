from typing import List, Dict
import random

class HumanizationEngine:
    """
    Engine for adding human feel to quantized MIDI patterns.
    """
    def __init__(self):
        pass

    def humanize_midi(self, midi_events: List[Dict]) -> List[Dict]:
        """
        Apply timing and velocity humanization to a sequence of events.
        """
        humanized = []
        for event in midi_events:
            # Create a copy to avoid modifying the original dictionary
            e = event.copy()
            
            # 1. Velocity Humanization
            if 'velocity' in e:
                # Random fluctuation +/- 5
                fluctuation = random.randint(-5, 5)
                e['velocity'] = max(1, min(127, e['velocity'] + fluctuation))
            
            # 2. Timing Humanization (Micro-timing)
            if 'time' in e:
                # Random offset +/- 0.01 beats (approx 5-10ms depending on BPM)
                # This creates a "loose" feel without breaking the rhythm
                offset = random.uniform(-0.01, 0.01)
                e['time'] = max(0, e['time'] + offset)
                
            humanized.append(e)
            
        return humanized