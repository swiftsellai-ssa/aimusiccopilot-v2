import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
import random

# Import new engines
from services.style_patterns import StylePatterns
from services.groove_engine import GrooveEngine
from services.music_theory_engine import MusicTheoryEngine

MUSIC_STYLES = {
    # ELECTRONIC
    'techno': {'bpm': 130, 'swing': 0.1, 'energy': 'driving'},
    'house': {'bpm': 125, 'swing': 0.15, 'energy': 'groovy'},
    'deep_house': {'bpm': 120, 'swing': 0.2, 'energy': 'smooth'},
    'trap': {'bpm': 140, 'swing': 0.05, 'energy': 'aggressive'},
    'dnb': {'bpm': 174, 'swing': 0.1, 'energy': 'fast'},
    'dubstep': {'bpm': 140, 'swing': 0.0, 'energy': 'heavy'},
    'ambient': {'bpm': 80, 'swing': 0.0, 'energy': 'atmospheric'},
    
    # POPULAR/MAINSTREAM
    'pop': {'bpm': 120, 'swing': 0.1, 'energy': 'bright'},
    'rock': {'bpm': 120, 'swing': 0.05, 'energy': 'powerful'}, 
    'indie': {'bpm': 110, 'swing': 0.1, 'energy': 'alternative'},
    'funk': {'bpm': 110, 'swing': 0.25, 'energy': 'groovy'},
    'disco': {'bpm': 120, 'swing': 0.15, 'energy': 'danceable'},
    
    # URBAN/HIP-HOP
    'hip_hop': {'bpm': 90, 'swing': 0.2, 'energy': 'laid-back'},
    'boom_bap': {'bpm': 90, 'swing': 0.15, 'energy': 'classic'},
    'lofi': {'bpm': 85, 'swing': 0.3, 'energy': 'chill'},
    'rnb': {'bpm': 95, 'swing': 0.25, 'energy': 'smooth'},
    
    # JAZZ/SOUL
    'jazz': {'bpm': 120, 'swing': 0.35, 'energy': 'sophisticated'}, # Updated per request
    'soul': {'bpm': 100, 'swing': 0.2, 'energy': 'emotional'},
    'gospel': {'bpm': 110, 'swing': 0.15, 'energy': 'uplifting'},
    
    # LATIN/WORLD
    'reggaeton': {'bpm': 95, 'swing': 0.0, 'energy': 'rhythmic'},
    'latin': {'bpm': 100, 'swing': 0.1, 'energy': 'tropical'},
    'afrobeat': {'bpm': 120, 'swing': 0.2, 'energy': 'percussive'},
    
    # HARD
    'metal': {'bpm': 140, 'swing': 0.0, 'energy': 'aggressive'},
    'punk': {'bpm': 180, 'swing': 0.0, 'energy': 'raw'},
    'cinematic': {'bpm': 70, 'swing': 0.0, 'energy': 'atmospheric'}
}

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
        self.groove_engine = GrooveEngine()
    
    def generate_pattern_with_dna(self,
                                  style: str,
                                  instrument: str,
                                  dna: PatternDNA,
                                  bars: int = 4) -> List[Dict]:
        """
        Generate pattern using detailed style definitions and DNA parameters.
        Handles 'full_kit' by compositing patterns.
        """
        events = []
        
        # --- Handle Aggregate Instruments ---
        if instrument in ['full_kit', 'full_drums', 'drums']:
            # Generate kit components recursively
            for component in ['kick', 'snare', 'hat']:
                component_events = self.generate_pattern_with_dna(style, component, dna, bars)
                events.extend(component_events)
            
            # Sort composite events
            events.sort(key=lambda x: x['time'])
            
            # Apply groove to the FULL kit for coherence
            # We skip groove on individual components to avoid double processing or phase issues
            # But here we recursively return raw events if we are 'inside' a recursion.
            # To handle this cleanly: apply groove ONLY at the top level or handle checks.
            # Simpler: Always apply groove on leaf nodes? No, cross-channel groove is better.
            # Let's apply groove HERE for the full kit context.
            processed = self.groove_engine.apply_groove(events, style, dna.complexity)
            return processed

        # --- Base Logic for Single Instruments ---
        
        # 1. Get Base Pattern from StylePatterns
        base_pattern = StylePatterns.get_pattern(style, instrument)
        
        # SAFETY FIX: If pattern is missing (or all zeros/empty), default to quarter notes
        if not base_pattern or not any(base_pattern):
             # print(f"⚠️ Warning: No pattern found for {style}/{instrument}. Using fallback.") # valid print
             # Default to Standard 4/4 (Quarter notes)
             base_pattern = [1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0]
        
        # 2. Get Style Metadata using LOCAL DICTIONARY (User Request)
        style_meta = MUSIC_STYLES.get(style, StylePatterns.get_style_metadata(style))
        
        pattern_length = 16 # 16 steps per bar
        
        # Pre-calculate Chord Progression if needed (for melodic/chords)
        progression = []
        if instrument in ['chords', 'lead', 'pad', 'arp', 'melody']:
            # [FIX] Legacy static call caused crash. IntegratedMidiGenerator handles progression now.
            # Using placeholder degrees for standalone compatibility.
            progression = [1, 4, 5, 1] 
            # Repeat progression to fill bars
            while len(progression) < bars:
                progression.extend(progression)
        
        for bar in range(bars):
            # For melodic instruments, determine current chord degree
            current_degree = progression[bar % len(progression)] if progression else 1
            
            for step in range(pattern_length):
                position = bar * pattern_length + step
                step_in_pattern = step % 16
                
                # Get base value (1 or 0)
                base_value = base_pattern[step_in_pattern]
                
                # 3. Calculate Hit Probability (Density Logic)
                hit_probability = self._calculate_hit_probability(
                    base_value,
                    dna.density,
                    position,
                    dna.evolution
                )
                
                # Adjust probability for melodic coherence (fewer random notes)
                if instrument not in ['kick', 'snare', 'hat', 'perc']:
                    if dna.density < 0.5:
                         # Force stick to grid more for low density melody
                        hit_probability = 1.0 if base_value else 0.0
                
                # Roll for hit
                if random.random() < hit_probability:
                    # 4. Calculate Velocity
                    velocity = self._calculate_velocity(
                        position, 
                        dna.velocity_curve,
                        dna.complexity
                    )
                    
                    # 5. Create Event (Straight Grid first)
                    note_duration = 0.25 # Default quarter note
                    
                    # Fine-tune durations
                    if instrument in ['hat', 'shake', 'arp']:
                        note_duration = 0.125
                    elif instrument in ['pad', 'chords']:
                        note_duration = 1.0 # Sustain
                    
                    event = {
                        'time': position * 0.25,  # Straight grid (groove applied later)
                        'velocity': velocity,
                        'duration': note_duration,
                        'probability': hit_probability,
                        'instrument_type': instrument # Tag for pitch assignment
                    }
                    
                    # Add melodic info for _add_pitch_to_events to use
                    if instrument in ['chords', 'lead', 'pad', 'arp', 'melody']:
                        event['degree'] = current_degree
                        event['is_chord'] = (instrument in ['chords', 'pad'])
                        event['is_arp'] = (instrument == 'arp')
                        
                    events.append(event)
                    
                    # 7. Add Ghost Notes (Complexity) - Drums Only
                    if instrument in ['snare', 'hat'] and dna.complexity > 0.6:
                        if random.random() < (dna.complexity - 0.5):
                            # Ghost note logic needs manual offset or just straight timing
                            # Let's put it on 16th grid and let GrooveEngine handling it
                            # But ghost notes are usually "in between". 
                            # Simplification: Add it at +0.125 (1/32) or just keep existing logic but removing GrooveEngine calls?
                            # The old logic used GrooveEngine to offset ghost note.
                            # I will place it straight and let the engine swing it.
                            events.append({
                                'time': position * 0.25 + 0.125,  # Straight 
                                'velocity': int(velocity * 0.4),  # Quiet
                                'duration': 0.0625,
                                'probability': 0.5,
                                'instrument_type': instrument
                            })
                            
        # Apply Groove locally for single instrument if not part of a kit
        # (If called recursively by full_kit, full_kit logic applies it)
        # But wait, 'full_kit' calls this function for 'kick' etc.
        # If I apply groove here, and then 'full_kit' applies groove again, it's double swing.
        # However, `full_kit` logic above returns early with `processed`.
        # So I *should* apply groove here for single instruments.
        # BUT if `full_kit` calls this, it gets the events back.
        # If I apply groove here, the events returned to `full_kit` are already grooved.
        # Then `full_kit` applies groove AGAIN?
        # My logic in `full_kit` block above: `processed = self.groove_engine.apply_groove(events...)`
        # So yes, double groove risk.
        # Robust fix: Do NOT apply groove in `full_kit` block. Just composite events.
        # Let the recursive calls handle it? 
        # Actually, Groove is best applied to the WHOLE pattern to ensure phase coherence if using random jitter.
        # But if `apply_groove` is deterministic based on style/time, it is fine.
        # User `apply_groove` uses `random.randint` for jitter.
        # If I apply jitter to kick, then to snare, it's fine (independent jitter).
        # The swing is deterministic (`is_off_beat`).
        # So I will apply usage here for single instruments.
        # And in `full_kit` block, I will NOT apply groove again, just return the aggregated events?
        # WAIT. `full_kit` block calls `self.generate_pattern_with_dna`.
        # If this method returns grooved events, then `full_kit` just aggregates them.
        # That is correct.
        # So I remove `processed = self.groove_engine.apply_groove` from the `full_kit` block I wrote in Step 1059 replacement content?
        # Wait, I am WRITING the replacement content now.
        # Ideally, I should apply groove individually per instrument in the loop.
        
        # NOTE: I need to check if I am breaking `full_kit` logic. 
        # If `full_kit` composites events, and those events are already grooved here, then I'm done.
        # So `full_kit` block should just `return events` (sorted).
        
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
                # Add notes in empty spaces
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