import random
from typing import List, Dict, Any

class PhraseStructure:
    """Create musical sentences, not just patterns"""
    
    STRUCTURES = {
        'AABA': [0, 0, 1, 0],  # Classic pop/jazz
        'ABAB': [0, 1, 0, 1],  # Verse-chorus
        'ABAC': [0, 1, 0, 2],  # Through-composed
        'AAAB': [0, 0, 0, 1],  # Build tension
    }
    
    def apply_structure(self, base_pattern: List[Dict], structure: str = 'AABA', variation_engine=None) -> List[Dict]:
        """Apply musical form to patterns.
        
        Args:
            base_pattern: The initial 1-bar pattern (Section A)
            structure_type: The form to use (AABA, etc.)
            variation_engine: Instance of PatternIntelligence to create variations
            
        Returns:
            List[Dict]: Combined events for the entire structure
        """
        structure_indices = self.STRUCTURES.get(structure, [0, 0, 0, 0])
        full_structure_events = []
        beats_per_bar = 4
        
        # Cache generated sections to ensure 'A' is always 'A', 'B' is always 'B'
        sections_cache = {}

        for bar_idx, section_id in enumerate(structure_indices):
            # Generate or retrieve section content
            if section_id not in sections_cache:
                if section_id == 0:
                    # Section A - Base Pattern
                    sections_cache[section_id] = [e.copy() for e in base_pattern]
                else:
                    # Section B/C - Variations
                    # If variation engine provided, use it, otherwise simple mutation
                    if variation_engine:
                        sections_cache[section_id] = variation_engine.generate_variation(base_pattern, intensity=0.3 * section_id)
                    else:
                        sections_cache[section_id] = [e.copy() for e in base_pattern] # Fallback
            
            # Add time offset for this bar
            bar_events = [e.copy() for e in sections_cache[section_id]]
            time_offset = bar_idx * beats_per_bar
            
            for event in bar_events:
                event['time'] += time_offset
                full_structure_events.extend(bar_events)
                
        # Remove duplicates if any (though logic above shouldn't create them per event object)
        # Note: full_structure_events.extend adds the list elements, so we are good.
        # Wait, inside the loop: for event in bar_events -> event['time']+=... -> extend.
        # Logic error in my thought above: I shouldn't loop inside the append loop.
        
        # Corrected Logic:
        final_events = []
        for bar_idx, section_id in enumerate(structure_indices):
            if section_id not in sections_cache:
                if section_id == 0:
                    sections_cache[section_id] = [e.copy() for e in base_pattern]
                else:
                    if variation_engine:
                        sections_cache[section_id] = variation_engine.generate_variation(base_pattern, intensity=0.3 * section_id)
                    else:
                         # Simple fallback variation: Shift time slightly or drop events
                        fallback_var = [e.copy() for e in base_pattern if random.random() > 0.2]
                        sections_cache[section_id] = fallback_var

            bar_events = [e.copy() for e in sections_cache[section_id]]
            time_offset = bar_idx * beats_per_bar
            
            for event in bar_events:
                event['time'] = event['time'] + time_offset # Reset time to relative bar start + offset
                # Note: event['time'] in sections_cache should be 0-4.
                
            final_events.extend(bar_events)
            
        return final_events


class PatternIntelligence:
    """Advanced pattern generation with musical intelligence"""
    
    def __init__(self):
        self.pattern_memory = {}  # Remember what was generated
        self.phrase_structure = PhraseStructure()
        
    def generate_variation(self, pattern: List[Dict], intensity: float = 0.2) -> List[Dict]:
        """Generate a variation of the given pattern."""
        variation = []
        for event in pattern:
            new_event = event.copy()
            
            # 1. Pruning (Remove events)
            if random.random() < (intensity * 0.5):
                continue
                
            # 2. Shift (Timing variation)
            if random.random() < (intensity * 0.3):
                shift = random.choice([-0.125, 0.125])
                new_event['time'] = max(0, new_event['time'] + shift)
                
            variation.append(new_event)
            
        # 3. Add fills (Ghost notes or extra hits)
        # (Simple implementation for now)
        return variation

    def generate_intelligent_pattern(self, base_pattern: List[Dict], context: Dict[str, Any]) -> List[Dict]:
        """Generate patterns that relate to each other"""
        
        # 1. Phrase Structure (Default to 4 bars AABA if bars=4)
        bars = context.get('bars', 4)
        if bars >= 4:
            return self.phrase_structure.apply_structure(base_pattern, 'AABA', self)
            
        # Fallback for short patterns: Simple Loop
        full_events = []
        for i in range(bars):
             offset = i * 4 # Assuming 4/4
             for evt in base_pattern:
                  new_evt = evt.copy()
                  new_evt['time'] += offset
                  full_events.append(new_evt)
        return full_events

    def _generate_response_to(self, call_pattern):
        # Placeholder for Call & Response logic
        return call_pattern
