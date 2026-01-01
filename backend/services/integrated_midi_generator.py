# backend/services/integrated_midi_generator.py
from .midi_generator import MidiGenerator
from .advanced_midi_generator import AdvancedPatternGenerator, PatternDNA
from .humanization_engine import HumanizationEngine
from .music_theory import MusicTheoryService
import mido
import logging
import mido
import logging
import random
from typing import Optional, Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


class IntegratedMidiGenerator:
    """
    Combines both generators for maximum flexibility.

    Event Structure:
    ---------------
    Events are dictionaries with the following keys:
    - time: float - Time in beats (quarter notes) from start
    - velocity: int - MIDI velocity (1-127)
    - duration: float - Note duration in beats
    - pitch: int - MIDI note number (0-127)
    - channel: int - MIDI channel (0-15, where 9 = drums)

    Supported Styles:
    ----------------
    - techno, trap, house, dnb, lofi

    Supported Instruments:
    ---------------------
    - drums, kick, snare, hat (use channel 9)
    - bass, melody, lead, synth (use channel 0)
    """

    # Drum instruments that should use MIDI channel 9 (drums)
    DRUM_INSTRUMENTS = {
        'drums', 'drum', 'full_drums', 'percussion',
        'kick', 'snare', 'hat', 'hats', 'hihat',
        'clap', 'rim', 'crash', 'ride', 'tom'
    }

    # Melodic instruments that should use MIDI channel 0
    MELODIC_INSTRUMENTS = {
        'bass', 'sub', '808', 'melody', 'lead', 'synth'
    }

    # Supported styles
    SUPPORTED_STYLES = {
        'techno', 'trap', 'house', 'dnb', 'lofi', 
        'modern_trap', 'cinematic', 'deep_house', 'liquid_dnb'
    }

    def __init__(self, enable_humanization: bool = True):
        """
        Initialize the integrated MIDI generator.

        Args:
            enable_humanization: Whether to apply humanization by default
        """
        self.basic_generator = MidiGenerator()
        self.advanced_generator = AdvancedPatternGenerator()
        self.humanizer = HumanizationEngine()
        self.music_theory = MusicTheoryService()
        self.enable_humanization = enable_humanization

    def generate(self,
                 description: str,
                 use_dna: bool = None,
                 humanize: bool = None,
                 seed: int = None,
                 **kwargs) -> Tuple[mido.MidiFile, int]:
        """
        Smart routing between generators with comprehensive error handling.

        Args:
            description: Text description of the pattern to generate
            use_dna: Force use of DNA-based advanced generator (None = auto-detect)
            humanize: Apply humanization (None = use instance default)
            seed: Random seed for deterministic generation (None = random)
            **kwargs: Additional parameters
                - style: str - Music style (techno, trap, etc.)
                - instrument: str - Instrument type
                - complexity: float - Pattern complexity (0-1)
                - density: float - Note density (0-1)
                - groove: float - Swing/groove amount (0-1)
                - velocity_curve: str - Velocity pattern
                - evolution: float - Pattern evolution (0-1)
                - bars: int - Number of bars to generate
                - bpm: int - Tempo in beats per minute

        Returns:
            Tuple[mido.MidiFile, int]: Generated MIDI file object and the seed used

        Raises:
            ValueError: If invalid parameters are provided
        """
        try:
            # Handle seeding
            if seed is None:
                seed = random.randint(0, 2**32 - 1)
            
            random.seed(seed)
            # Note: We should ideally seed numpy as well if used in advanced_generator
            # but standard random covers the logic we implemented in _add_pitch and _add_notes
            
            # Validate and normalize parameters
            style = kwargs.get('style', self._detect_style(description))
            instrument = kwargs.get('instrument', self._detect_instrument(description))
            key = kwargs.get('key', 'C')
            scale_type = kwargs.get('scale_type', 'minor')

            # Validate style/instrument combination
            self._validate_generation_params(style, instrument)

            # Determine humanization setting
            should_humanize = humanize if humanize is not None else self.enable_humanization

            # Auto-detect DNA usage if not specified
            if use_dna is None:
                # Use DNA for supported styles, regardless of complexity
                use_dna = style in self.advanced_generator.pattern_templates
                logger.info(f"Auto-detected use_dna={use_dna} for style={style}")

            # Determine MIDI channel based on instrument type
            channel = self._get_channel_for_instrument(instrument)
            kwargs['channel'] = channel

            logger.info(f"Generating: style={style}, instrument={instrument}, "
                       f"use_dna={use_dna}, humanize={should_humanize}, channel={channel}")

            # Route to appropriate generator
            if use_dna and style in self.advanced_generator.pattern_templates:
                # Remove style and instrument from kwargs to avoid duplicate arguments
                dna_kwargs = {k: v for k, v in kwargs.items() if k not in ['style', 'instrument']}
                midi_file = self._generate_with_dna(
                    description=description,
                    style=style,
                    instrument=instrument,
                    humanize=should_humanize,
                    **dna_kwargs
                )
            else:
                logger.info(f"Using basic generator (use_dna={use_dna}, "
                           f"style_supported={style in self.advanced_generator.pattern_templates})")
                # Remove duplicate arguments
                basic_kwargs = {k: v for k, v in kwargs.items() if k not in ['instrument']}
                midi_file = self.basic_generator.generate_track(
                    description=description,
                    instrument=instrument,
                    **basic_kwargs
                )
            
            return midi_file, seed

        except Exception as e:
            logger.error(f"Error generating MIDI: {e}", exc_info=True)
            raise ValueError(f"Failed to generate MIDI: {str(e)}") from e


    def save_file(self, midi_file: mido.MidiFile, filename: str) -> None:
        """
        Helper method to save a MIDI object to disk.
        
        Args:
            midi_file: The mido.MidiFile object
            filename: Target file path
        """
        try:
            midi_file.save(filename)
            logger.info(f"Successfully saved MIDI file to {filename}")
        except Exception as e:
            logger.error(f"Failed to save MIDI file: {e}")
            raise

    def quantize_to_scale(self, note_value: int, scale_type: str, root_note: str) -> int:
        """
        Quantize a MIDI note number to the nearest note in the valid scale.
        
        Args:
            note_value: Input MIDI note number
            scale_type: Scale name (e.g. 'minor', 'major')
            root_note: Key root (e.g. 'C', 'F#')
            
        Returns:
            int: Quantized MIDI note number
        """
        # Get all valid notes for this scale across meaningful octaves (0-8)
        valid_notes = []
        for octave in range(9):
            notes = self.music_theory.get_scale_notes(root_note, scale_type, octave)
            valid_notes.extend(notes)
            
        # Find nearest valid note
        try:
            quantized_note = min(valid_notes, key=lambda x: abs(x - note_value))
            return quantized_note
        except ValueError:
            # Fallback if list is empty (shouldn't happen with correct usage)
            return note_value

    def _generate_with_dna(self,
                           description: str,
                           style: str,
                           instrument: str,
                           humanize: bool,
                           **kwargs) -> mido.MidiFile:
        """
        Generate pattern using DNA-based advanced generator.

        Args:
            description: Pattern description
            style: Music style
            instrument: Instrument type
            humanize: Whether to apply humanization
            **kwargs: Additional DNA parameters

        Returns:
            mido.MidiFile: Generated MIDI file
        """
        # Create DNA from parameters
        dna = PatternDNA(
            density=kwargs.get('density', 0.7),
            complexity=kwargs.get('complexity', 0.5),
            groove=kwargs.get('groove', 0.2),
            velocity_curve=kwargs.get('velocity_curve', 'natural'),
            evolution=kwargs.get('evolution', 0.3)
        )

        logger.debug(f"DNA parameters: {dna}")

        # Generate pattern with DNA
        events = self.advanced_generator.generate_pattern_with_dna(
            style=style,
            instrument=instrument,
            dna=dna,
            bars=kwargs.get('bars', 4)
        )

        # Add pitch and channel information to events
        events = self._add_pitch_to_events(
            events,
            instrument,
            kwargs.get('channel', 9),
            key=kwargs.get('key', 'C'),
            scale_type=kwargs.get('scale_type', 'minor')
        )

        # Apply humanization if enabled
        if humanize:
            logger.debug(f"Applying humanization to {len(events)} events")
            events = self.humanizer.humanize_midi(events)
            # Re-sort after humanization to maintain timing integrity
            events.sort(key=lambda x: x['time'])

        # Convert to MIDI file
        return self._events_to_midi(events, kwargs.get('bpm', 120))

    def _validate_generation_params(self, style: str, instrument: str):
        """
        Validate style and instrument combination.

        Args:
            style: Music style
            instrument: Instrument type

        Raises:
            ValueError: If invalid combination
        """
        # Validate style
        if style not in self.SUPPORTED_STYLES:
            logger.warning(f"Unsupported style '{style}', will use fallback")

        # Validate instrument
        if instrument not in (self.DRUM_INSTRUMENTS | self.MELODIC_INSTRUMENTS):
            logger.warning(f"Unknown instrument '{instrument}', will use best effort")

        # Check if style/instrument combination is supported by advanced generator
        if style in self.advanced_generator.pattern_templates:
            style_data = self.advanced_generator.pattern_templates[style]
            if instrument not in style_data and instrument not in self.MELODIC_INSTRUMENTS:
                logger.warning(
                    f"Instrument '{instrument}' not explicitly supported for style '{style}'. "
                    f"Supported: {list(style_data.keys())}"
                )

    def _get_channel_for_instrument(self, instrument: str) -> int:
        """
        Determine MIDI channel based on instrument type.

        Args:
            instrument: Instrument name

        Returns:
            int: MIDI channel (9 for drums, 0 for melodic)
        """
        if instrument in self.DRUM_INSTRUMENTS:
            return 9  # MIDI channel 10 (0-indexed as 9) is for drums
        else:
            return 0  # Default to channel 1 (0-indexed as 0) for melodic

    def _detect_style(self, description: str) -> str:
        """
        Detect music style from description.

        Args:
            description: Text description

        Returns:
            str: Detected style name
        """
        if 'modern' in description and 'trap' in description:
            return 'modern_trap'
        if 'cinematic' in description or 'ambient' in description:
            return 'cinematic'
        if 'deep' in description and 'house' in description:
            return 'deep_house'
        if 'liquid' in description:
            return 'liquid_dnb'
        
        # Reuse basic generator's detection logic
        return self.basic_generator._detect_style(description)

    def _detect_instrument(self, description: str) -> str:
        """
        Detect instrument from description.

        Args:
            description: Text description

        Returns:
            str: Detected instrument name
        """
        # Reuse basic generator's detection logic
        return self.basic_generator._detect_instrument(description)

    def _add_pitch_to_events(self,
                             events: List[Dict],
                             instrument: str,
                             channel: int,
                             key: str = 'C',
                             scale_type: str = 'minor') -> List[Dict]:
        """
        Add pitch and channel information with scale quantization for melodies.
        
        Args:
            events: List of event dictionaries
            instrument: Instrument type
            channel: MIDI channel
            key: Musical key (root note)
            scale_type: Type of scale
            
        Returns:
            List[Dict]: Events with pitch and channel added
        """
        # Get drum map from basic generator
        drum_map = self.basic_generator.drum_map

        # Probabilistic pitch walk state
        current_pitch = 60 # Start at Middle C
        
        for event in events:
            # Add channel
            event['channel'] = channel

            # Add pitch if not present
            if 'pitch' not in event:
                if channel == 9:  # Drums
                    # Map instrument name to MIDI note
                    if instrument in drum_map:
                        event['pitch'] = drum_map[instrument]
                    elif instrument in self.DRUM_INSTRUMENTS:
                        # Default to kick for unknown drum instruments
                        event['pitch'] = drum_map.get('kick', 36)
                    else:
                        event['pitch'] = 36  # Default kick
                else:  # Melodic
                    # Generate probabilistic pitch variation ("Random Walk")
                    # Move by small intervals (-2 to +2 semitones usually, occasionally more)
                    interval = random.choice([-5, -4, -3, -2, -1, 0, 0, 0, 1, 2, 3, 4, 7])
                    
                    # Apply variation to current pitch context
                    raw_pitch = current_pitch + interval
                    
                    # Keep within reasonable range (C2 to C6)
                    raw_pitch = max(36, min(84, raw_pitch))
                    
                    # Quantize to scale
                    quantized_pitch = self.quantize_to_scale(raw_pitch, scale_type, key)
                    
                    event['pitch'] = quantized_pitch
                    
                    # Update current pitch for next step (to create melody flow)
                    current_pitch = quantized_pitch

        return events

    def _events_to_midi(self, events: List[Dict], bpm: int) -> mido.MidiFile:
        """
        Orchestrator for creating a MIDI file from events.
        """
        mid, track = self._create_track(bpm)
        self._add_notes(track, events)
        
        logger.info(f"Generated MIDI file: {len(events)} events, {bpm} BPM")
        return mid

    def _create_track(self, bpm: int) -> tuple[mido.MidiFile, mido.MidiTrack]:
        """
        Initialize MIDI file and track with tempo.
        """
        mid = mido.MidiFile()
        track = mido.MidiTrack()
        mid.tracks.append(track)
        track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm)))
        return mid, track

    def _add_notes(self, track: mido.MidiTrack, events: List[Dict]) -> None:
        """
        Convert events to MIDI messages and add them to the track.
        Handles note_on/note_off pairing, sorting, and delta time calculation.
        Applies Gaussian humanization to velocity.
        """
        messages = []
        ticks_per_beat = 480  # MIDI standard
        
        # Standard deviation for velocity humanization
        velocity_sigma = 5.0

        for event in events:
            # Validate event structure
            if not all(key in event for key in ['time', 'pitch', 'velocity', 'duration']):
                logger.warning(f"Skipping incomplete event: {event}")
                continue

            start_tick = int(event['time'] * ticks_per_beat)
            end_tick = int((event['time'] + event['duration']) * ticks_per_beat)
            channel = event.get('channel', 0)
            
            # Apply Gaussian humanization to velocity
            # Use original velocity as mean, ensure it stays within 0-127
            original_velocity = int(event['velocity'])
            
            # We calculate a 'humanized' velocity using a Gaussian distribution
            # centered on the original velocity.
            humanized_velocity = int(random.gauss(original_velocity, velocity_sigma))
            
            # Clamp value to be safe MIDI velocity (1-127, avoiding 0 which is note-off)
            final_velocity = max(1, min(127, humanized_velocity))

            # Note on message
            messages.append({
                'tick': start_tick,
                'type': 'note_on',
                'note': int(event['pitch']),
                'velocity': final_velocity,
                'channel': channel
            })

            # Note off message
            messages.append({
                'tick': end_tick,
                'type': 'note_off',
                'note': int(event['pitch']),
                'velocity': 0,
                'channel': channel
            })

        # Sort all messages by tick time
        # Note: note_off sorts after note_on at same tick to avoid conflicts
        messages.sort(key=lambda x: (x['tick'], x['type'] == 'note_off'))

        # Convert absolute ticks to delta times
        last_tick = 0
        for msg in messages:
            delta = msg['tick'] - last_tick
            if delta < 0:
                logger.warning(f"Negative delta time detected: {delta}, setting to 0")
                delta = 0

            track.append(mido.Message(
                msg['type'],
                note=msg['note'],
                velocity=msg['velocity'],
                time=delta,
                channel=msg['channel']
            ))

            last_tick = msg['tick']
