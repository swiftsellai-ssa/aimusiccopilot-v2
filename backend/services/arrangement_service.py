import mido
import logging
from typing import List, Dict, Optional
from services.integrated_midi_generator import IntegratedMidiGenerator

logger = logging.getLogger(__name__)

class ArrangementService:
    def __init__(self):
        self.generator = IntegratedMidiGenerator()
        
    def generate_arrangement(
        self,
        structure: List[Dict],
        style: str,
        key: str = "C",
        scale: str = "minor",
        bpm: int = 120,
        instrument: str = "full_kit" # Legacy arg, ignored for full arrangement
    ) -> mido.MidiFile:
        """
        Generates a Multi-Track MIDI Arrangement (Type 1).
        Tracks: Drums, Bass, Chords, Melody.
        """
        
        # 1. Container (Type 1)
        final_mid = mido.MidiFile(type=1, ticks_per_beat=480)
        
        # 2. Tracks Configuration
        # (Instrument Category, SubOption/Role, Channel, Track Name)
        tracks_config = [
            ('drums', 'full_kit', 9, 'Drums'),   # Ch 10
            ('bass', 'groove_bass', 0, 'Bass'),  # Ch 1
            ('melody', 'chords', 1, 'Chords'),   # Ch 2
            ('melody', 'lead', 2, 'Melody')      # Ch 3
        ]
        
        ticks_per_beat = 480
        ticks_per_bar = ticks_per_beat * 4

        # 3. Iterate Instruments/Tracks
        for inst_cat, inst_sub, channel, track_name in tracks_config:
            track = mido.MidiTrack()
            final_mid.tracks.append(track)
            
            # Track Header
            track.append(mido.MetaMessage('track_name', name=track_name, time=0))
            if track_name == 'Drums': # Tempo typically on track 0 (or all)
                track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm), time=0))
            
            current_track_ticks = 0
            
            # 4. Stitch Blocks
            for block in structure:
                block_type = block.get('type') # intro, verse...
                bars = block.get('bars', 4)
                
                # Determine precise sub_option
                # If drums, we might want 'intro' kit vs 'verse' kit etc.
                # Currently IntegratedMidiGenerator takes `sub_option` as context.
                # But for 'bass'/'melody', 'sub_option' argument usually defines the ROLE (bass vs chords).
                # The 'description' helps the DNA logic know it's an 'intro'.
                # To support 'Chords' vs 'Lead', we must pass that as `sub_option` if logic relies on it.
                # BUT logic relies on `sub_option` for context too?
                # Let's verify IntegratedMidiGenerator logic.
                # It uses sub_option for DNA mapping. 
                # Ideally we pass 'sub_option' as the ROLE (e.g. 'groove_bass') and rely on description/bars for structure?
                # OR AdvancedPatternGenerator handles block_type inside?
                # Actually, `IntegratedMidiGenerator` maps `sub_option` to `dn_type`.
                # If we pass 'intro', it looks for 'intro' DNA.
                # If we want Chords, we need 'chords' DNA.
                # Conflict: We can't pass both 'intro' and 'chords' into one `sub_option` arg.
                # Solution: We pass `sub_option=inst_sub` (e.g. 'chords') so it generates chords.
                # And we put `block_type` (intro) into the `description` string, hoping `_detect_style` or internal logic picks it up 
                # OR we modify generator to accept explicit `fragment_type`?
                # For now, let's stick to passing `sub_option=inst_sub`. 
                # The intensity/density is mostly controlled by DNA found for that sub-option.
                # Intro/Verse differentiation might be weak if DNA doesn't vary by block type.
                # However, `AdvancedPatternGenerator` does use `sub_option` primarily.
                # If we want 'intro' drums, we must pass 'intro' as sub_option.
                # But then we get drums.
                # What if we want 'intro' chords?
                # We need to trust the generator interprets `description` or `intensity`.
                # Let's pass `sub_option=inst_sub` (role) and hope Intensity controls the "Intro-ness" (low intensity).
                
                # Intensity Mapping
                # block['intensity'] -> 'low', 'medium', 'high'
                # Map directly to float for AdvancedPatternGenerator math
                block_intensity = block.get('intensity', 'medium')
                complexity_map = {'low': 0.3, 'medium': 0.6, 'high': 0.9}
                complexity = complexity_map.get(block_intensity, 0.6)
                
                # Generate
                block_mid, _ = self.generator.generate(
                    description=f"{style} {block_type} {track_name}",
                    style=style,
                    instrument=inst_cat,       # drums, bass, melody
                    sub_option=inst_sub,       # full_kit, groove_bass, chords, lead
                    bpm=bpm,
                    bars=bars,
                    key=key,
                    scale_type=scale,
                    complexity=complexity,     # Use block intensity for dynamics
                    humanize=True
                )
                
                # Extract events
                source_track = block_mid.tracks[0]
                block_ticks = 0
                
                for msg in source_track:
                    if msg.type in ['set_tempo', 'end_of_track', 'track_name']: continue
                    
                    new_msg = msg.copy()
                    
                    # Force Channel
                    if hasattr(new_msg, 'channel'):
                        new_msg.channel = channel
                        
                    track.append(new_msg)
                    block_ticks += new_msg.time
                    
                # Pad
                expected_ticks = bars * ticks_per_bar
                if block_ticks < expected_ticks:
                    gap = expected_ticks - block_ticks
                    # Use a meta event to bridge the gap in delta time
                    # But we need an event to carry the delta time.
                    # Text/Marker is safe.
                    track.append(mido.MetaMessage('marker', text=f"End {block_type}", time=int(gap)))
                elif block_ticks > expected_ticks:
                    logger.warning(f"{track_name} Block {block_type} overflow.")
                    
        return final_mid
