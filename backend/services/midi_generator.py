# backend/services/midi_generator.py

import mido
from mido import MidiFile, MidiTrack, Message, MetaMessage
import random
from typing import Dict, List, Optional, Any
from .advanced_midi_generator import AdvancedPatternGenerator, PatternDNA

class MidiGenerator:
    def __init__(self):
        # Comprehensive drum mapping for electronic music
        self.drum_map = {
            'kick': 36,        # C1 - Bass Drum
            'snare': 38,       # D1 - Snare
            'clap': 39,        # D#1 - Hand Clap
            'rim': 37,         # C#1 - Side Stick
            'hat_closed': 42,  # F#1 - Closed Hi-Hat
            'hat_open': 46,    # A#1 - Open Hi-Hat
            'hat_pedal': 44,   # G#1 - Pedal Hi-Hat
            'crash': 49,       # C#2 - Crash Cymbal
            'ride': 51,        # D#2 - Ride Cymbal
            'tom_low': 41,     # F1 - Low Floor Tom
            'tom_mid': 43,     # G1 - Low Tom
            'tom_high': 45,    # A1 - Mid Tom
            'cowbell': 56,     # G#2 - Cowbell
            'perc': 60,        # C3 - Hi Bongo
            'shaker': 70       # A#3 - Maracas
        }
        
        # Style patterns for different genres
        self.style_patterns = {
            'techno': {
                'bpm': 130,
                'kick_pattern': [0, 4, 8, 12],  # 4-on-floor
                'hat_pattern': [2, 6, 10, 14],  # Off-beat
                'complexity': 0.7
            },
            'trap': {
                'bpm': 140,
                'kick_pattern': [0, 7, 10],
                'hat_pattern': list(range(16)),  # Rolling hi-hats
                'complexity': 0.9
            },
            'house': {
                'bpm': 128,
                'kick_pattern': [0, 4, 8, 12],
                'hat_pattern': [2, 4, 6, 8, 10, 12, 14],
                'complexity': 0.6
            },
            'dnb': {
                'bpm': 174,
                'kick_pattern': [0, 10],
                'snare_pattern': [4, 12],
                'complexity': 0.8
            },
            'lofi': {
                'bpm': 85,
                'kick_pattern': [0, 6, 8, 14],
                'complexity': 0.4
            }
        }
        
        # Initialize Advanced Generator
        self.advanced = AdvancedPatternGenerator()

    def generate_track(self, 
                      description: str = "techno beat",
                      musical_key: str = "C",
                      musical_scale: str = "minor",
                      instrument: str = None,
                      instrument_mode: str = None,
                      bpm: Optional[int] = None,
                      bars: int = 4,
                      **kwargs) -> MidiFile:
        """
        Main generation method with proper defaults and error handling
        """
        mid = MidiFile()
        track = MidiTrack()
        mid.tracks.append(track)
        
        # Determine style from description
        style = self._detect_style(description)
        
        # Set BPM (use provided or style default)
        if bpm is None:
            bpm = self.style_patterns.get(style, {}).get('bpm', 120)
        
        track.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm)))
        track.append(MetaMessage('track_name', name=f'{style.upper()} - {instrument or "Full"}'))
        
        # Determine what to generate
        target_instrument = instrument or instrument_mode or self._detect_instrument(description)
        
        # Generate based on instrument type
        if target_instrument in ['drums', 'drum', 'full_drums', 'percussion']:
            self._generate_drums(track, style, bars)
        elif target_instrument in ['bass', 'sub', '808']:
            self._generate_bass(track, musical_key, musical_scale, style, bars)
        elif target_instrument in ['melody', 'lead', 'synth']:
            self._generate_melody(track, musical_key, musical_scale, style, bars)
        elif target_instrument == 'kick':
            self._generate_kick_only(track, style, bars)
        elif target_instrument in ['hat', 'hats', 'hihat']:
            self._generate_hats_only(track, style, bars)
        else:
            # Generate full arrangement
            self._generate_full_pattern(track, musical_key, musical_scale, style, bars)
        
        return mid

    def _detect_style(self, description: str) -> str:
        """Detect music style from description"""
        desc_lower = description.lower()
        
        for style in self.style_patterns.keys():
            if style in desc_lower:
                return style
        
        # Additional keyword detection
        if any(word in desc_lower for word in ['dark', 'industrial', 'warehouse']):
            return 'techno'
        elif any(word in desc_lower for word in ['trap', 'drill', 'atlanta']):
            return 'trap'
        elif any(word in desc_lower for word in ['house', 'disco', 'funk']):
            return 'house'
        elif any(word in desc_lower for word in ['jungle', 'dnb', 'breakbeat']):
            return 'dnb'
        elif any(word in desc_lower for word in ['lofi', 'chill', 'relaxed']):
            return 'lofi'
        
        return 'techno'  # Default

    def _detect_instrument(self, description: str) -> str:
        """Detect instrument from description"""
        desc_lower = description.lower()
        
        if any(word in desc_lower for word in ['drum', 'beat', 'rhythm']):
            return 'drums'
        elif any(word in desc_lower for word in ['bass', '808', 'sub']):
            return 'bass'
        elif any(word in desc_lower for word in ['melody', 'lead', 'synth']):
            return 'melody'
        elif 'kick' in desc_lower:
            return 'kick'
        elif any(word in desc_lower for word in ['hat', 'hihat']):
            return 'hat'
        
        return 'drums'  # Default

    def _generate_drums(self, track: MidiTrack, style: str, bars: int):
        """Generate complete drum pattern"""
        # Use advanced generator for supported styles
        if style in self.advanced.pattern_templates:
            self._generate_advanced_drums(track, style, bars)
            return

        # Fallback to legacy generation for other styles
        pattern = self.style_patterns.get(style, self.style_patterns['techno'])
        ticks_per_step = 120  # 16th note resolution
        total_steps = 16 * bars
        
        for step in range(total_steps):
            step_in_bar = step % 16
            
            # Kick pattern
            if step_in_bar in pattern.get('kick_pattern', [0, 4, 8, 12]):
                velocity = 100 + random.randint(-5, 5)  # Humanization
                track.append(Message('note_on', note=self.drum_map['kick'], 
                                   velocity=velocity, time=0, channel=9))
                track.append(Message('note_off', note=self.drum_map['kick'], 
                                   velocity=0, time=ticks_per_step, channel=9))
            
            # Snare/Clap pattern
            elif step_in_bar in pattern.get('snare_pattern', [4, 12]):
                note = self.drum_map['snare'] if style != 'trap' else self.drum_map['clap']
                velocity = 90 + random.randint(-5, 5)
                track.append(Message('note_on', note=note, 
                                   velocity=velocity, time=0, channel=9))
                track.append(Message('note_off', note=note, 
                                   velocity=0, time=ticks_per_step, channel=9))
            
            # Hi-hat pattern
            elif step_in_bar in pattern.get('hat_pattern', []):
                # Add hat rolls for trap
                if style == 'trap' and random.random() < 0.3:
                    # Triplet roll
                    for i in range(3):
                        velocity = 60 + random.randint(0, 20)
                        track.append(Message('note_on', note=self.drum_map['hat_closed'],
                                           velocity=velocity, time=ticks_per_step//3, channel=9))
                        track.append(Message('note_off', note=self.drum_map['hat_closed'],
                                           velocity=0, time=0, channel=9))
                else:
                    velocity = 70 + random.randint(-10, 10)
                    track.append(Message('note_on', note=self.drum_map['hat_closed'],
                                       velocity=velocity, time=0, channel=9))
                    track.append(Message('note_off', note=self.drum_map['hat_closed'],
                                       velocity=0, time=ticks_per_step, channel=9))
            else:
                # Empty step
                track.append(Message('note_off', note=0, velocity=0, time=ticks_per_step, channel=9))

    def _generate_advanced_drums(self, track: MidiTrack, style: str, bars: int):
        """Generate drums using PatternDNA"""
        # Create DNA based on style
        dna = PatternDNA(
            density=0.6 if style == 'techno' else 0.7,
            complexity=0.7 if style == 'trap' else 0.5,
            groove=0.2 if style == 'house' else 0.0,
            velocity_curve='accent' if style == 'techno' else 'exponential',
            evolution=0.3
        )

        all_events = []
        
        # Generate events for each instrument
        instruments = {
            'kick': self.drum_map['kick'],
            'snare': self.drum_map['snare'] if style != 'trap' else self.drum_map['clap'],
            'hat': self.drum_map['hat_closed']
        }

        for instr_name, midi_note in instruments.items():
            events = self.advanced.generate_pattern_with_dna(style, instr_name, dna, bars)
            for e in events:
                e['note'] = midi_note
                all_events.append(e)

        # Convert to MIDI messages
        self._write_events_to_track(track, all_events)

    def _write_events_to_track(self, track, events, ticks_per_beat=480):
        """Convert absolute time events to delta-time MIDI messages"""
        messages = []
        for e in events:
            # Note On
            messages.append({
                'time_ticks': int(e['time'] * ticks_per_beat),
                'type': 'note_on',
                'note': e['note'],
                'velocity': e['velocity']
            })
            # Note Off
            messages.append({
                'time_ticks': int((e['time'] + e['duration']) * ticks_per_beat),
                'type': 'note_off',
                'note': e['note'],
                'velocity': 0
            })
        
        messages.sort(key=lambda x: x['time_ticks'])
        
        last_time = 0
        for msg in messages:
            delta = msg['time_ticks'] - last_time
            if delta < 0: delta = 0
            track.append(Message(msg['type'], note=msg['note'], velocity=msg['velocity'], time=delta, channel=9))
            last_time = msg['time_ticks']

    def _generate_bass(self, track: MidiTrack, key: str, scale: str, style: str, bars: int):
        """Generate bassline"""
        from .music_theory import MusicTheoryService
        theory = MusicTheoryService()
        
        root_midi = theory._note_to_midi(key, octave=2)  # Bass octave
        scale_notes = theory.SCALES.get(scale, theory.SCALES['minor'])
        
        ticks_per_step = 120
        total_steps = 16 * bars
        
        # Style-specific bass patterns
        if style == 'techno':
            # Rolling bass
            pattern = [0, 0, 1, 1, 2, 2, 1, 1] * 2
        elif style == 'trap':
            # 808 slides
            pattern = [0, -1, -1, 0, -1, -1, 3, 2]
        else:
            # Simple root notes
            pattern = [0, 0, 0, 0]
        
        for step in range(total_steps):
            if step % 4 == 0:  # Quarter notes for bass
                note_offset = pattern[step % len(pattern)]
                if note_offset >= 0:
                    note = root_midi + scale_notes[note_offset % len(scale_notes)]
                    velocity = 80 + random.randint(-5, 5)
                    track.append(Message('note_on', note=note, velocity=velocity, time=0, channel=0))
                    track.append(Message('note_off', note=note, velocity=0, time=ticks_per_step * 4, channel=0))
                else:
                    track.append(Message('note_off', note=0, velocity=0, time=ticks_per_step * 4, channel=0))

    def _generate_melody(self, track: MidiTrack, key: str, scale: str, style: str, bars: int):
        """Generate melodic pattern"""
        from .music_theory import MusicTheoryService
        theory = MusicTheoryService()
        
        root_midi = theory._note_to_midi(key, octave=4)  # Melody octave
        scale_notes = theory.SCALES.get(scale, theory.SCALES['minor'])
        
        ticks_per_step = 120
        total_steps = 16 * bars
        
        # Generate melodic phrase
        phrase = []
        for _ in range(8):
            note_index = random.choice([0, 2, 3, 4, 6])  # Pentatonic-ish
            phrase.append(scale_notes[note_index % len(scale_notes)])
        
        for step in range(total_steps):
            if step % 2 == 0 and random.random() > 0.3:  # Sparse melody
                note = root_midi + phrase[step % len(phrase)]
                velocity = 70 + random.randint(-10, 10)
                duration = ticks_per_step * random.choice([2, 4, 6])  # Variable length
                
                track.append(Message('note_on', note=note, velocity=velocity, time=0, channel=0))
                track.append(Message('note_off', note=note, velocity=0, time=duration, channel=0))
            else:
                track.append(Message('note_off', note=0, velocity=0, time=ticks_per_step, channel=0))

    def _generate_kick_only(self, track: MidiTrack, style: str, bars: int):
        """Generate only kick drum pattern"""
        pattern = self.style_patterns.get(style, self.style_patterns['techno'])
        ticks_per_step = 120
        total_steps = 16 * bars
        
        for step in range(total_steps):
            step_in_bar = step % 16
            if step_in_bar in pattern.get('kick_pattern', [0, 4, 8, 12]):
                velocity = 100 + random.randint(-5, 5)
                track.append(Message('note_on', note=self.drum_map['kick'], 
                                   velocity=velocity, time=0, channel=9))
                track.append(Message('note_off', note=self.drum_map['kick'], 
                                   velocity=0, time=ticks_per_step, channel=9))
            else:
                track.append(Message('note_off', note=0, velocity=0, time=ticks_per_step, channel=9))

    def _generate_hats_only(self, track: MidiTrack, style: str, bars: int):
        """Generate only hi-hat pattern"""
        pattern = self.style_patterns.get(style, self.style_patterns['techno'])
        ticks_per_step = 120
        total_steps = 16 * bars
        
        for step in range(total_steps):
            step_in_bar = step % 16
            if step_in_bar in pattern.get('hat_pattern', list(range(0, 16, 2))):
                # Vary between closed and open hats
                hat_type = 'hat_closed' if random.random() > 0.2 else 'hat_open'
                velocity = 60 + random.randint(0, 30)
                
                track.append(Message('note_on', note=self.drum_map[hat_type],
                                   velocity=velocity, time=0, channel=9))
                track.append(Message('note_off', note=self.drum_map[hat_type],
                                   velocity=0, time=ticks_per_step, channel=9))
            else:
                track.append(Message('note_off', note=0, velocity=0, time=ticks_per_step, channel=9))

    def _generate_full_pattern(self, track: MidiTrack, key: str, scale: str, style: str, bars: int):
        """Generate full arrangement with drums and bass"""
        # This would combine drums + bass + melody
        # For simplicity, just generate drums for now
        self._generate_drums(track, style, bars)

    def save_midi(self, midi_file: MidiFile, filename: str) -> str:
        """Save MIDI file and return path"""
        midi_file.save(filename)
        return filename