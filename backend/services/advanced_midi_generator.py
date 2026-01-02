import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
import random

# Import new engines
from services.style_patterns import StylePatterns
from services.groove_engine import GrooveEngine
from services.music_theory_engine import MusicTheoryEngine

@dataclass
class PatternDNA:
    """Musical DNA that defines pattern characteristics"""
    density: float  # 0-1 (sparse to dense)
    complexity: float  # 0-1 (simple to complex)
    groove: float  # 0-1 (straight to swung)
    velocity_curve: str  # 'linear', 'exponential', 'random', 'accent'
    evolution: float  # 0-1 (static to evolving)
    
class AdvancedPatternGenerator:
    """
    Advanced MIDI Pattern Generator (v2 Professional Upgrade)
    Integrates StylePatterns, GrooveEngine, and MusicTheoryEngine.
    """
    
    def __init__(self):
        # Cache for style metadata
        self.style_patterns = StylePatterns()
    
    def generate_pattern_with_dna(self,
                                  style: str,
                                  instrument: str,
                                  dna: PatternDNA,
                                  bars: int = 4) -> List[Dict]:
        """
        Generate pattern using detailed style definitions and DNA parameters.
        """
        # 1. Get Base Pattern from StylePatterns
        base_pattern = StylePatterns.get_pattern(style, instrument)
        
        # 2. Get Style Metadata (for recommended groove/swing)
        style_meta = StylePatterns.get_style_metadata(style)
        
        # Determine Groove Template
        groove_template = 'straight'
        if dna.groove > 0.1:
            if style_meta['swing'] > 0.4:
                groove_template = 'swing_jazz'
            elif style_meta['swing'] > 0:
                groove_template = 'shuffle'
            else:
                groove_template = 'laid_back' # Default subtle humanization
        
        events = []
        pattern_length = 16 # 16 steps per bar
        
        for bar in range(bars):
            for step in range(pattern_length):
                position = bar * pattern_length + step
                step_in_pattern = step % 16
                
                # Get base value (1 or 0)
                base_value = base_pattern[step_in_pattern]
                
                # 3. Calculate Hit Probability (Density Logic)
                # If instrument is melodic, density acts differently (handled later or via MusicTheory)
                # For drums:
                hit_probability = self._calculate_hit_probability(
                    base_value,
                    dna.density,
                    position,
                    dna.evolution
                )
                
                # Roll for hit
                if random.random() < hit_probability:
                    # 4. Calculate Velocity
                    velocity = self._calculate_velocity(
                        position, 
                        dna.velocity_curve,
                        dna.complexity
                    )
                    
                    # 5. Apply Groove (Timing Offset)
                    groove_amount = dna.groove
                    # Use style default swing if DNA groove is high
                    if dna.groove > 0.5 and style_meta['swing'] > 0:
                        groove_amount = max(dna.groove, style_meta['swing'])
                        
                    time_offset = GrooveEngine.get_timing_offset(
                        step, 
                        template_name=groove_template, 
                        intensity=groove_amount
                    )
                    
                    # 6. Create Event
                    note_duration = 0.125 if instrument in ['hat', 'shake'] else 0.25
                    
                    events.append({
                        'time': position * 0.25 + time_offset,  # Convert to beats
                        'velocity': velocity,
                        'duration': note_duration,
                        'probability': hit_probability
                    })
                    
                    # 7. Add Ghost Notes (Complexity)
                    if dna.complexity > 0.6 and instrument in ['snare', 'hat']:
                        if random.random() < (dna.complexity - 0.5):
                            ghost_offset = GrooveEngine.get_timing_offset(
                                step, 
                                template_name=groove_template, 
                                intensity=groove_amount * 0.8
                            )
                            events.append({
                                'time': position * 0.25 + 0.125 + ghost_offset,  # 16th after
                                'velocity': int(velocity * 0.4),  # Quiet
                                'duration': 0.0625,
                                'probability': 0.5
                            })
                            
        return events
    
    def _calculate_hit_probability(self, base_value, density, position, evolution):
        """
        Calculate hit probability based on DNA parameters.
        Same algorithm as v1 but cleaner.
        """
        prob = float(base_value)

        if density < 0.3:
            # Low density: only keep strong beats
            is_strong_beat = (position % 4 == 0)
            prob *= (0.7 + density * 0.3) if is_strong_beat else (density * 2)
        elif density < 0.7:
            # Medium: mostly faithful
            prob *= (0.5 + density * 0.7)
        else:
            # High: add fills
            prob *= (0.8 + density * 0.2)
            if position % 2 == 1 and base_value == 0:
                prob += (density - 0.7) * 0.5

        # Evolution
        if evolution > 0:
            time_factor = (position / 64)
            prob += evolution * 0.2 * np.sin(time_factor * np.pi * 2)

        return np.clip(prob, 0, 1)
    
    def _calculate_velocity(self, position, curve_type, complexity):
        # Use GrooveEngine or local logic for base velocity
        base_velocity = 100
        if curve_type == 'accent':
            base_velocity = 120 if (position % 16) in [0, 8] else 90
        elif curve_type == 'exponential':
            base_velocity = 60 + (position % 16) * 3
        elif curve_type == 'random':
            base_velocity = random.randint(70, 110)
            
        # Add humanization via GrooveEngine helper logic
        # We manually apply random variation here as in v1
        humanization = random.randint(-int(10 * complexity + 1), int(10 * complexity + 1))
        return int(np.clip(base_velocity + humanization, 1, 127))