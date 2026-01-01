import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
import random

@dataclass
class PatternDNA:
    """Musical DNA that defines pattern characteristics"""
    density: float  # 0-1 (sparse to dense)
    complexity: float  # 0-1 (simple to complex)
    groove: float  # 0-1 (straight to swung)
    velocity_curve: str  # 'linear', 'exponential', 'random', 'accent'
    evolution: float  # 0-1 (static to evolving)
    
class AdvancedPatternGenerator:
    def __init__(self):
        self.pattern_templates = {
            'techno': {
                'kick': {
                    'base': [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
                    'variations': [
                        [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0],  # Extra kick
                        [1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],  # Syncopated
                        [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0],  # Double kick
                    ]
                },
                'hat': {
                    'base': [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0],
                    'variations': [
                        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],  # 16ths
                        [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],  # Off-beat
                    ]
                },
                'snare': {
                    'base': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                    'variations': [
                        [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],  # Ghost snare
                    ]
                },
                'bass': {
                    'base': [1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0],  # Groove bass
                    'variations': [
                        [1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0],  # Busier
                        [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],  # 4-on-floor bass
                    ],
                    'melodic': True
                },
                'melody': {
                    'base': [1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0],  # Melodic rhythm
                    'variations': [
                        [1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0],  # Variation
                    ],
                    'melodic': True
                }
            },
            'trap': {
                'kick': {
                    'base': [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
                    'variations': [
                        [1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0],
                        [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0],
                    ]
                },
                'hat': {
                    'base': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                    'triplet_rolls': True,
                    'velocity_pattern': 'exponential'
                },
                'snare': {
                    'base': [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                    'variations': [
                        [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],  # Double snare
                    ]
                },
                'bass': {
                    'base': [1, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 0],  # 808 pattern
                    'variations': [
                        [1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0],  # Busy 808
                    ],
                    'melodic': True
                }
            },
            'house': {
                'kick': {
                    'base': [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],  # 4-on-floor
                    'variations': [
                        [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0],  # Slight variation
                        [1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0],  # Double kick
                    ]
                },
                'hat': {
                    'base': [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1],  # Off-beat (classic house)
                    'variations': [
                        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # 16ths
                        [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0],  # Sparse
                    ]
                },
                'snare': {
                    'base': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],  # Clap on 2 & 4
                    'variations': [
                        [0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0],  # Extra clap
                    ]
                },
                'bass': {
                    'base': [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0],  # House bassline
                    'variations': [
                        [1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 0],  # Syncopated
                        [1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0],  # Groovier
                    ],
                    'melodic': True
                },
                'melody': {
                    'base': [1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0],  # Piano riff
                    'variations': [
                        [1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0],  # Busier
                    ],
                    'melodic': True
                }
            },
            'dnb': {
                'kick': {
                    'base': [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],  # Sparse kick
                    'variations': [
                        [1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0],  # Double
                        [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],  # Extra
                    ]
                },
                'hat': {
                    'base': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],  # Fast 16ths
                    'variations': [
                        [1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1],  # Breakbeat
                    ]
                },
                'snare': {
                    'base': [0, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0],  # Breakbeat snare
                    'variations': [
                        [0, 0, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0],  # Busier break
                    ]
                },
                'bass': {
                    'base': [1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0],  # Reese bass
                    'variations': [
                        [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0],  # Wobble
                    ],
                    'melodic': True
                }
            },
            'lofi': {
                'kick': {
                    'base': [1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0],  # Laid back
                    'variations': [
                        [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0],  # Variation
                    ]
                },
                'hat': {
                    'base': [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0],  # Lazy hats
                    'variations': [
                        [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0],  # Jazzy
                    ]
                },
                'snare': {
                    'base': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],  # Simple
                    'variations': [
                        [0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],  # Ghost
                    ]
                },
                'bass': {
                    'base': [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0],  # Minimal bass
                    'variations': [
                        [1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],  # Slightly busier
                    ],
                    'melodic': True
                },
                'melody': {
                    'base': [1, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0],  # Jazzy melody
                    'variations': [
                        [1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],  # Variation
                    ],
                    'melodic': True
            },
            'modern_trap': {
                'kick': {
                    'base': [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0], # Sparse hard kick
                    'variations': [
                        [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0],
                    ]
                },
                'hat': {
                    'base': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                    'triplet_rolls': True,
                    'velocity_pattern': 'random' # Rolling feel
                },
                'snare': {
                    'base': [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0], # Clap on 3
                    'variations': [
                         [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
                    ]
                },
                'bass': {
                    'base': [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0], # 808 glide match
                    'melodic': True
                }
            },
            'cinematic': {
                'kick': {
                    'base': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # Very sparse impact
                    'variations': []
                },
                'hat': {
                    'base': [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0], # Slow ticks
                    'variations': []
                },
                'snare': {
                    'base': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # Often no snare or very soft
                    'variations': []
                },
                'melody': {
                    'base': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], # Long evolving pads
                    'melodic': True
                }
            },
            'deep_house': {
                'kick': {
                    'base': [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0], # Softer 4/4
                    'variations': []
                },
                'hat': {
                    'base': [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0], # Open hat
                    'variations': []
                },
                'snare': {
                    'base': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                    'variations': []
                },
                'bass': {
                    'base': [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0], # Offbeat bass
                    'melodic': True
                },
                'melody': { # Jazzy chords
                    'base': [1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                    'melodic': True
                }
            },
            'liquid_dnb': {
                'kick': {
                    'base': [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0], # Typical DnB break
                    'variations': [
                        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0]
                    ]
                },
                'hat': {
                    'base': [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0], # Shakers/Hats
                    'variations': []
                },
                'snare': {
                    'base': [0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
                    'variations': []
                },
                'bass': {
                    'base': [1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0], # Smooth reese
                    'melodic': True
                }
            }
            }
        }
    
    def generate_pattern_with_dna(self,
                                  style: str,
                                  instrument: str,
                                  dna: PatternDNA,
                                  bars: int = 4) -> List[Dict]:
        """Generate pattern using DNA characteristics"""

        # Get style data with fallback
        style_data = self.pattern_templates.get(style, self.pattern_templates['techno'])

        # Get instrument data - try to find better fallbacks
        instr_data = self._get_instrument_data(style_data, instrument, style)

        # Select base pattern based on complexity
        base_pattern = self._select_pattern_variation(instr_data, dna.complexity)

        # Check if melodic instrument
        is_melodic = instr_data.get('melodic', False)

        events = []
        
        for bar in range(bars):
            for step in range(16):
                position = bar * 16 + step
                
                # Probability of hit based on density
                hit_probability = self._calculate_hit_probability(
                    base_pattern[step % 16],
                    dna.density,
                    position,
                    dna.evolution
                )
                
                if random.random() < hit_probability:
                    # Calculate velocity with humanization
                    velocity = self._calculate_velocity(
                        position, 
                        dna.velocity_curve,
                        dna.complexity
                    )
                    
                    # Apply groove/swing
                    time_offset = self._apply_groove(position, dna.groove)
                    
                    events.append({
                        'time': position * 0.25 + time_offset,  # Convert to beats
                        'velocity': velocity,
                        'duration': 0.125 if instrument == 'hat' else 0.25,
                        'probability': hit_probability
                    })
                    
                    # Add ghost notes for complexity
                    if dna.complexity > 0.7 and random.random() < 0.3:
                        events.append({
                            'time': position * 0.25 + 0.125 + time_offset,  # 16th after
                            'velocity': int(velocity * 0.5),  # Quieter
                            'duration': 0.0625,
                            'probability': 0.5
                        })
        
        return events
    
    def _calculate_hit_probability(self, base_value, density, position, evolution):
        """
        Calculate hit probability based on DNA parameters.

        Improved algorithm:
        - Low density (0-0.3): Removes weaker beats, keeps strong beats
        - Medium density (0.3-0.7): Uses base pattern as-is
        - High density (0.7-1.0): Adds syncopation and fills
        """
        prob = float(base_value)

        if density < 0.3:
            # Low density: only keep strong beats (downbeats)
            is_strong_beat = (position % 4 == 0)  # Every quarter note
            if is_strong_beat:
                prob *= (0.7 + density * 0.3)  # Keep most strong beats
            else:
                prob *= (density * 2)  # Reduce weak beats significantly
        elif density < 0.7:
            # Medium density: use base pattern with slight variation
            prob *= (0.5 + density * 0.7)
        else:
            # High density: add fills and syncopation
            prob *= (0.8 + density * 0.2)
            # Add probability for off-beats
            is_offbeat = (position % 2 == 1)
            if is_offbeat and base_value == 0:
                prob += (density - 0.7) * 0.5  # Add syncopation

        # Apply evolution (gradual changes over time)
        if evolution > 0:
            time_factor = (position / 64)
            prob += evolution * 0.2 * np.sin(time_factor * np.pi * 2)

        return np.clip(prob, 0, 1)
    
    def _calculate_velocity(self, position, curve_type, complexity):
        base_velocity = 100
        if curve_type == 'accent':
            base_velocity = 120 if (position % 16) in [0, 8] else (100 if position % 4 == 0 else 80)
        elif curve_type == 'exponential':
            base_velocity = 60 + (position % 16) * 3
        elif curve_type == 'random':
            base_velocity = random.randint(60, 120)
        humanization = random.randint(-int(10 * complexity + 1), int(10 * complexity + 1))
        return int(np.clip(base_velocity + humanization, 1, 127))
    
    def _apply_groove(self, position, groove_amount):
        if groove_amount == 0: return 0
        return groove_amount * 0.05 if position % 2 == 1 else 0

    def _get_instrument_data(self, style_data: Dict, instrument: str, style: str) -> Dict:
        """
        Get instrument data with intelligent fallbacks.

        Fallback priority:
        1. Exact match (e.g., 'bass')
        2. Similar instrument (e.g., 'bass' -> 'melody' for melodic)
        3. Generic fallback (kick for drums, bass for melodic)
        """
        # Direct match
        if instrument in style_data:
            return style_data[instrument]

        # Normalize instrument names
        normalized = instrument.lower().replace('_', '')

        # Melodic instrument fallbacks
        melodic_instruments = {'bass', 'melody', 'lead', 'synth', 'chord', 'chords', 'keys', 'piano'}
        drum_instruments = {'kick', 'snare', 'hat', 'hats', 'hihat', 'clap', 'percussion', 'drums'}

        if normalized in melodic_instruments or 'bass' in normalized or 'melody' in normalized:
            # Try to find any melodic pattern
            for key in ['bass', 'melody', 'lead']:
                if key in style_data:
                    return style_data[key]
            # Fallback to basic melodic pattern
            return {
                'base': [1, 0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0, 0, 0],
                'variations': [],
                'melodic': True
            }

        # Drum instrument fallbacks
        if 'kick' in normalized or 'bd' in normalized:
            return style_data.get('kick', style_data.get('kick', {}))
        elif 'snare' in normalized or 'sd' in normalized or 'clap' in normalized:
            return style_data.get('snare', style_data.get('snare', {}))
        elif 'hat' in normalized or 'hh' in normalized or 'cymbal' in normalized:
            return style_data.get('hat', style_data.get('hat', {}))

        # Final fallback
        return style_data.get('kick', {
            'base': [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
            'variations': []
        })

    def _select_pattern_variation(self, instr_data: Dict, complexity: float) -> List[int]:
        """
        Select base pattern or variation based on complexity.

        Args:
            instr_data: Instrument data dictionary
            complexity: Complexity value (0-1)

        Returns:
            List of 16 integers representing the pattern
        """
        base = instr_data.get('base', [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0])
        variations = instr_data.get('variations', [])

        if not variations:
            return base

        # Use complexity to decide which variation
        if complexity < 0.3:
            # Low complexity: use base pattern
            return base
        elif complexity < 0.7:
            # Medium complexity: use first variation
            return variations[0] if len(variations) > 0 else base
        else:
            # High complexity: use more advanced variation or random
            if len(variations) > 1:
                return random.choice(variations)
            elif len(variations) == 1:
                return variations[0]
            else:
                return base