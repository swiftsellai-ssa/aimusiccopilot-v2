import random
import numpy as np

class GrooveEngine:
    """
    Engine for generating micro-timing adjustments to simulate 'human feel'.
    """

    TEMPLATES = {
        'straight': lambda pos: 0,
        'shuffle': lambda pos: 0.08 if pos % 2 == 1 else 0, # Late 8th note
        'swing_jazz': lambda pos: 0.16 if pos % 2 == 1 else 0, # Triplet feel
        'drunk': lambda pos: random.uniform(-0.05, 0.05), # Sloppy
        'robotic': lambda pos: 0, # Perfect quantization
        'rushed': lambda pos: -0.02, # Just ahead of the beat
        'laid_back': lambda pos: 0.03, # Just behind the beat
    }
    
    @classmethod
    def get_timing_offset(cls, position: int, template_name: str = 'straight', intensity: float = 1.0) -> float:
        """
        Calculate timing offset in beats.
        
        Args:
            position: Step position (0-15)
            template_name: Name of groove template
            intensity: Multiplier for the effect (0.0 to 1.0+)
            
        Returns:
            Float representing offset in beats (e.g., 0.05 is late)
        """
        func = cls.TEMPLATES.get(template_name, cls.TEMPLATES['straight'])
        
        # Calculate raw offset
        offset = func(position)
        
        # Apply intensity
        return offset * intensity

    @classmethod
    def apply_humanization_velocity(cls, base_velocity: int, amount: float = 0.1) -> int:
        """Randomize velocity slightly"""
        variation = random.randint(-int(127 * amount), int(127 * amount))
        return int(np.clip(base_velocity + variation, 1, 127))
