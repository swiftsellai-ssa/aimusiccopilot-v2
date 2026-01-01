# backend/services/recommendation_engine.py

from typing import Dict, List

class RecommendationEngine:
    def __init__(self):
        self.workflow_chains = {
            'kick': ['bass', 'hats', 'snare'],
            'bass': ['kick', 'melody', 'pads'],
            'drums': ['bass', 'melody', 'fx'],
            'melody': ['drums', 'bass', 'harmony'],
            'full_drums': ['bass', 'melody', 'vocals']
        }
        
        self.style_suggestions = {
            'techno': ['Add warehouse reverb', 'Try 909 percussion', 'Add acid bassline'],
            'trap': ['Add 808 slides', 'Try triplet hi-hats', 'Add vocal chops'],
            'house': ['Add disco strings', 'Try filtered loops', 'Add piano stabs'],
            'dnb': ['Add Amen break', 'Try reese bass', 'Add atmospheric pads'],
            'lofi': ['Add vinyl crackle', 'Try jazz chords', 'Add field recordings']
        }

    def get_suggestions(self, last_gen_context: Dict) -> List[Dict]:
        """
        Generate smart suggestions based on last generation
        """
        instrument = last_gen_context.get('instrument', 'drums')
        style = last_gen_context.get('style', 'techno')
        key = last_gen_context.get('key', 'C')
        scale = last_gen_context.get('scale', 'minor')
        bpm = last_gen_context.get('bpm', 120)
        
        suggestions = []
        
        # Get workflow chain suggestions
        next_instruments = self.workflow_chains.get(instrument, ['bass', 'melody'])
        
        # Essential next step
        if next_instruments:
            next_inst = next_instruments[0]
            suggestions.append({
                "type": "essential",
                "instrument": next_inst,
                "title": f"Add {next_inst.title()}",
                "description": f"Complete your {style} track with matching {next_inst}",
                "prompt": f"{style} {next_inst} in {key} {scale} at {bpm} BPM",
                "color": "border-green-500",
                "confidence": 0.9
            })
        
        # Creative variation
        if len(next_instruments) > 1:
            creative_inst = next_instruments[1]
            suggestions.append({
                "type": "creative",
                "instrument": creative_inst,
                "title": f"Try {creative_inst.title()}",
                "description": f"Add emotional depth with {creative_inst}",
                "prompt": f"atmospheric {style} {creative_inst} in {key} {scale}",
                "color": "border-purple-500",
                "confidence": 0.7
            })
        
        # Style-specific suggestion
        style_tips = self.style_suggestions.get(style, [])
        if style_tips:
            tip = style_tips[0]
            suggestions.append({
                "type": "technique",
                "instrument": "effect",
                "title": "Production Tip",
                "description": tip,
                "prompt": f"{style} with {tip.lower()}",
                "color": "border-blue-500",
                "confidence": 0.6
            })
        
        # Experimental suggestion
        opposite_mood = "major" if scale == "minor" else "minor"
        suggestions.append({
            "type": "experimental",
            "instrument": "melody",
            "title": "Break the Pattern",
            "description": f"Try {opposite_mood} scale for contrast",
            "prompt": f"unexpected {style} melody in {key} {opposite_mood}",
            "color": "border-yellow-500",
            "confidence": 0.4
        })
        
        # Tempo variation
        if bpm < 100:
            suggestions.append({
                "type": "variation",
                "instrument": instrument,
                "title": "Double Time Feel",
                "description": "Try a faster variation",
                "prompt": f"fast {style} {instrument} at {bpm * 2} BPM",
                "color": "border-red-500",
                "confidence": 0.5
            })
        
        return suggestions[:4]  # Return top 4 suggestions

    def get_completion_percentage(self, generated_elements: List[str]) -> int:
        """
        Calculate how complete a track is
        """
        essential_elements = ['kick', 'bass', 'hats', 'snare', 'melody']
        completed = len([e for e in essential_elements if e in generated_elements])
        return int((completed / len(essential_elements)) * 100)

    def suggest_next_action(self, track_elements: List[str]) -> str:
        """
        Suggest the most logical next action
        """
        if not track_elements:
            return "Start with a drum pattern"
        
        if 'drums' in track_elements and 'bass' not in track_elements:
            return "Add a bassline to complement your drums"
        
        if 'bass' in track_elements and 'melody' not in track_elements:
            return "Add a lead melody for the hook"
        
        if len(track_elements) >= 3:
            return "Mix and arrange your elements"
        
        return "Keep building your track"