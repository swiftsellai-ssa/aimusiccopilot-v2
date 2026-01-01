# backend/services/ai_service.py

import json
import os
from typing import Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class MusicIntelligence:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("⚠️ WARNING: No OpenAI API Key found in .env")
            self.client = None
        else:
            self.client = OpenAI(api_key=api_key)

    def analyze_request(self, description: str) -> Dict:
        """
        Transform user description into technical music parameters
        """
        if not self.client:
            return self._fallback_logic(description)

        print(f"🧠 AI Analyzing: {description}")

        prompt = f"""
        You are an expert electronic music producer. Analyze this request and output ONLY valid JSON.
        
        User request: "{description}"
        
        Return JSON with these exact fields:
        {{
            "bpm": integer between 60-180,
            "style": one of ["techno", "trap", "house", "dnb", "lofi", "ambient"],
            "key": music key like "C", "F#", "Bb",
            "scale": one of ["minor", "major", "phrygian", "dorian"],
            "instrument": one of ["drums", "bass", "melody", "kick", "full"],
            "complexity": float between 0.1-1.0,
            "velocity_feel": one of ["human", "robotic", "aggressive", "soft"],
            "mood": one of ["dark", "uplifting", "sad", "energetic", "chill"]
        }}
        
        Be smart about inferring parameters from context.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You output only valid JSON, no explanations."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )

            content = response.choices[0].message.content.strip()
            # Clean potential markdown formatting
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            
            result = json.loads(content)
            print(f"✅ AI Result: {result}")
            return result

        except Exception as e:
            print(f"❌ OpenAI Error: {e}")
            return self._fallback_logic(description)

    def _fallback_logic(self, text: str) -> Dict:
        """Smart fallback when AI is unavailable"""
        text_lower = text.lower()
        
        # Detect BPM
        bpm = 120
        if "fast" in text_lower or "dnb" in text_lower:
            bpm = 174
        elif "trap" in text_lower or "drill" in text_lower:
            bpm = 140
        elif "house" in text_lower:
            bpm = 128
        elif "techno" in text_lower:
            bpm = 130
        elif "slow" in text_lower or "lofi" in text_lower:
            bpm = 85
        
        # Detect style
        style = "techno"
        for s in ["techno", "trap", "house", "dnb", "lofi"]:
            if s in text_lower:
                style = s
                break
        
        # Detect mood and set key/scale accordingly
        if "dark" in text_lower or "evil" in text_lower:
            key, scale, mood = "F#", "phrygian", "dark"
        elif "sad" in text_lower or "melancholic" in text_lower:
            key, scale, mood = "A", "minor", "sad"
        elif "happy" in text_lower or "uplifting" in text_lower:
            key, scale, mood = "C", "major", "uplifting"
        else:
            key, scale, mood = "C", "minor", "energetic"
        
        # Detect instrument
        instrument = "drums"
        if "bass" in text_lower or "808" in text_lower:
            instrument = "bass"
        elif "melody" in text_lower or "lead" in text_lower:
            instrument = "melody"
        elif "kick" in text_lower:
            instrument = "kick"
        elif "full" in text_lower or "complete" in text_lower:
            instrument = "full"
        
        return {
            "bpm": bpm,
            "style": style,
            "key": key,
            "scale": scale,
            "instrument": instrument,
            "complexity": 0.7,
            "velocity_feel": "human",
            "mood": mood
        }

    def enhance_prompt(self, basic_prompt: str, context: Dict = None) -> str:
        """
        Enhance a basic prompt with musical context
        """
        enhanced = basic_prompt
        
        if context:
            if 'key' in context:
                enhanced += f" in {context['key']} {context.get('scale', 'minor')}"
            if 'bpm' in context:
                enhanced += f" at {context['bpm']} BPM"
            if 'style' in context:
                enhanced += f" {context['style']} style"
        
        return enhanced