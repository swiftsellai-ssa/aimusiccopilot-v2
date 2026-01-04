import random

class GrooveEngine:
    """Add human feel to patterns"""
    
    # Template-uri definite în planul tău
    GROOVE_TEMPLATES = {
        'straight': {'swing': 0, 'humanize': 5},
        'shuffle': {'swing': 67, 'humanize': 10},  # Triplet swing
        'jazz_swing': {'swing': 60, 'humanize': 15},
        'drunk': {'swing': 30, 'humanize': 25},    # J Dilla style
        'robotic': {'swing': 0, 'humanize': 0}
    }

    def apply_groove(self, events, style: str, complexity: float, custom_swing: float = None):
        """Aplică swing și humanization evenimentelor MIDI"""
        
        # Alegem template-ul bazat pe stil
        groove_type = 'straight'
        if style in ['jazz', 'blues']:
            groove_type = 'jazz_swing'
        elif style in ['house', 'uk_garage']:
            groove_type = 'shuffle'
        elif style in ['lofi', 'hip_hop']:
            groove_type = 'drunk'
            
        settings = self.GROOVE_TEMPLATES.get(groove_type, self.GROOVE_TEMPLATES['straight'])
        
        # Factori de ajustare
        swing_amount = settings['swing'] / 100.0
        
        # [NEW] Custom swing override (0.0 - 1.0)
        if custom_swing is not None:
             swing_amount = custom_swing
             
        humanize_amount = settings['humanize']
        
        processed_events = []
        
        for event in events:
            # 1. Humanize Timing (Micșorăm precizia)
            # Adăugăm un mic decalaj aleatoriu (+/- câțiva tickși)
            timing_jitter = random.randint(-humanize_amount, humanize_amount) if humanize_amount > 0 else 0
            
            # 2. Apply Swing (Groove logic)
            # Check for off-beats (both 8ths and 16ths can be swung depending on style)
            # Typically:
            # - 8th Swing: Delays 0.5, 1.5, 2.5, 3.5
            # - 16th Swing: Delays 0.25, 0.75, 1.25...
            
            pos_in_beat = event['time'] % 1.0
            swing_offset = 0
            
            # Simple combined swing logic:
            # If we are on an "and" (0.5) OR "e/a" (0.25/0.75), we apply swing.
            # But usually Jazz swings 8ths significantly.
            
            is_off_beat_8th = abs(pos_in_beat - 0.5) < 0.01
            is_off_beat_16th = abs(pos_in_beat - 0.25) < 0.01 or abs(pos_in_beat - 0.75) < 0.01
            
            if swing_amount > 0:
                if is_off_beat_8th:
                    # Apply full swing to 8th notes
                    swing_offset = swing_amount * 0.15 # Stronger effect for 8ths
                elif is_off_beat_16th:
                    # Apply lighter swing to 16ths
                    swing_offset = swing_amount * 0.1
            
            new_time = max(0, event['time'] + swing_offset + (timing_jitter / 1000.0))
            
            # 3. Humanize Velocity (Nu lovim toba la fel de tare de fiecare dată)
            velo_jitter = random.randint(-humanize_amount, humanize_amount)
            new_velocity = max(1, min(127, event['velocity'] + velo_jitter))
            
            # Reconstruim evenimentul
            processed_event = event.copy()
            processed_event['time'] = new_time
            processed_event['velocity'] = new_velocity
            processed_events.append(processed_event)
            
        return processed_events
