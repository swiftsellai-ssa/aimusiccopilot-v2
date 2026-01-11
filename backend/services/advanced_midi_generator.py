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
    
    def _get_phrase_start_offset(self, style: str) -> float:
        """
        Dan Update: Calculate phrase start offset to avoid 'Downbeat Bias'.
        Returns offset in beats (quarter notes).
        """
        roll = random.random()
        if style in ['jazz', 'neo_soul', 'lofi']:
            if roll < 0.30: return 0.0      # Downbeat (Beat 1)
            elif roll < 0.60: return 3.5    # Pickup (And of 4 of previous bar - functionally -0.5 or push to end) -> interpreted as shift
            else: return 1.0                # Backbeat (Beat 2)
        elif style == 'latin':
            return 0.0 if roll < 0.5 else 0.5 # Tumbao offset (And of 1)
        return 0.0 # Default for Techno/Pop

    def generate_pattern_with_dna(self,
                                  style: str,
                                  instrument: str,
                                  dna: PatternDNA,
                                  bars: int = 4,
                                  phrase_offset: float = None) -> List[Dict]:
        """
        Generate pattern using detailed style definitions and DNA parameters.
        Handles 'full_kit' by compositing patterns.
        """
        events = []
        
        # Determine global offset if not provided (for coherence)
        if phrase_offset is None:
            phrase_offset = self._get_phrase_start_offset(style)

        # --- Handle Aggregate Instruments ---
        if instrument in ['full_kit', 'full_drums', 'drums']:
            # Generate kit components recursively with SAME offset
            for component in ['kick', 'snare', 'hat']:
                component_events = self.generate_pattern_with_dna(style, component, dna, bars, phrase_offset)
                events.extend(component_events)
            
            # Sort composite events
            events.sort(key=lambda x: x['time'])
            
            # [Fix] Do NOT apply groove here. IntegratedMidiGenerator applies it globally.
            # This prevents "Double Swing" and ensures coherence.
            return events

        # --- Base Logic for Single Instruments ---
        
        # 1. Get Base Pattern from StylePatterns
        base_pattern = StylePatterns.get_pattern(style, instrument)
        
        # SAFETY FIX: If pattern is missing (or all zeros/empty), default to quarter notes
        if not base_pattern or not any(base_pattern):
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
                
                # [Dan Update] Syncopation Logic: Force rests on strong beats for Jazz
                if style in ['jazz', 'neo_soul'] and instrument not in ['kick']: # Keep kick anchoring? Or loosen it too. Let's loosen all.
                     if step_in_pattern in [0, 8]: # Beats 1 and 3
                         # Drastically reduce probability to force "dancing" around the beat
                         hit_probability *= 0.3 
                
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
                    
                    # [Dan Update] Apply Phrase Start Offset
                    raw_time = position * 0.25 + phrase_offset
                    
                    event = {
                        'time': raw_time, 
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
                            events.append({
                                'time': raw_time + 0.125,  # Straight + 1/32
                                'velocity': int(velocity * 0.4),  # Quiet
                                'duration': 0.0625,
                                'probability': 0.5,
                                'instrument_type': instrument
                            })
                            
        # Apply Groove locally for single instrument if not part of a kit
        # NOTE: If we are here, we are likely a single instrument OR a leaf in the recursion.
        # But wait, if we are a leaf called by full_kit, full_kit WILL apply groove again on the combined list.
        # We should NOT apply groove here if we are part of a full_kit generation to avoid "Double Swing".
        # But this function doesn't know if it was called recursively.
        # However, `full_kit` logic expects *ungrooved* events to composite.
        # So we should RETURN raw events here.
        # But what if I call this function for just 'snare'? I want groove.
        # Solution: The caller (`IntegratedMidiGenerator`) uses this for 'full_kit' mostly?
        # Or does it call for single instruments?
        # IntegratedMidiGenerator calls `generate_pattern_with_dna` for `instrument`.
        # If instrument is 'full_kit', the recursion handles it.
        # If instrument is 'snare', we reach here.
        # To support single instrument groove, we SHOULD apply groove here.
        # To avoid double groove for full_kit:
        # We can pass `apply_groove=False` in recursive calls?
        # Let's add that to signature? No, simpler:
        # `full_kit` logic applies groove. We can make `full_kit` logic NOT apply groove, and rely on this?
        # But then cross-channel groove (e.g. kick influencing hi-hat perception) isn't possible (though my engine is channel-independent currently).
        # Actually, simpler: Use `phrase_offset` as a flag? No.
        # Let's add `apply_output_groove` arg.
        
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