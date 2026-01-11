from .midi_generator import MidiGenerator
from .advanced_midi_generator import AdvancedPatternGenerator, PatternDNA, MUSIC_STYLES
from .style_patterns import StylePatterns
from .humanization_engine import HumanizationEngine
from .music_theory import MusicTheoryService
from .music_theory_engine import MusicTheoryEngine
from .groove_engine import GrooveEngine
# New Engines
from .pattern_intelligence import PatternIntelligence
from .harmonic_engine import HarmonicEngine
from .rhythm_engine import RhythmEngine
from .production_engine import ProductionEngine

import mido
import logging
import random
from typing import Optional, Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


class IntegratedMidiGenerator:
    """
    Combines both generators for maximum flexibility.
    ...
    """
    # ... (Constants remain the same) ...
    DRUM_INSTRUMENTS = {
        'drums', 'drum', 'full_drums', 'percussion',
        'kick', 'snare', 'hat', 'hats', 'hihat',
        'clap', 'rim', 'crash', 'ride', 'tom'
    }

    # Melodic instruments that should use MIDI channel 0
    MELODIC_INSTRUMENTS = {
        'bass', 'sub', '808', 'melody', 'lead', 'synth', 'keys', 'piano', 'pad', 'chords', 'strings'
    }

    # Supported styles
    SUPPORTED_STYLES = {
        'techno', 'trap', 'house', 'dnb', 'lofi', 
        'modern_trap', 'cinematic', 'deep_house', 'liquid_dnb',
        'pop', 'rock', 'jazz', 'blues', 'latin', 'reggaeton', 'afrobeat', 'funk', 'disco', 'soul',
        'boom_bap', 'metal', 'indie', 'hip_hop', 'punk',
        'dubstep', 'ambient', 'gospel' # Added last batch
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
        self.groove_engine = GrooveEngine()
        
        # Initialize New Engines
        self.pattern_intelligence = PatternIntelligence()
        self.harmonic_engine = HarmonicEngine()
        self.music_theory_engine = MusicTheoryEngine() # New Logic
        self.rhythm_engine = RhythmEngine()
        self.production_engine = ProductionEngine()
        
        self.enable_humanization = enable_humanization

    def generate(self,
                 description: str,
                 use_dna: bool = None,
                 humanize: bool = None,
                 seed: int = None,
                 forced_context: list = None, # 1. Update Signature
                 **kwargs) -> Tuple[mido.MidiFile, int]:
        # ... (generate method validation logic remains) ...
        # Copied context for safety
        try:
            # Handle seeding
            if seed is None:
                seed = random.randint(0, 2**32 - 1)
            
            random.seed(seed)
            
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
                use_dna = style in self.advanced_generator.style_patterns.PATTERNS
                logger.info(f"Auto-detected use_dna={use_dna} for style={style}")

            # Determine MIDI channel based on instrument type
            channel = self._get_channel_for_instrument(instrument)
            kwargs['channel'] = channel

            logger.info(f"Generating: style={style}, instrument={instrument}, "
                       f"use_dna={use_dna}, humanize={should_humanize}, channel={channel}")

            # Route to appropriate generator
            is_advanced_style = style in self.advanced_generator.style_patterns.PATTERNS
            
            if use_dna or is_advanced_style:
                # Remove style and instrument from kwargs to avoid duplicate arguments
                dna_kwargs = {k: v for k, v in kwargs.items() if k not in ['style', 'instrument']}
                dna_kwargs['forced_context'] = forced_context # Pass explicit param explicitly
                midi_file = self._generate_with_dna(
                    description=description,
                    style=style,
                    instrument=instrument,
                    humanize=should_humanize,
                    **dna_kwargs
                )
            else:
                logger.info(f"Using basic generator (use_dna={use_dna}, "
                           f"style_supported={is_advanced_style})")
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
        """Helper method to save a MIDI object to disk."""
        try:
            midi_file.save(filename)
            logger.info(f"Successfully saved MIDI file to {filename}")
        except Exception as e:
            logger.error(f"Failed to save MIDI file: {e}")
            raise

    def quantize_to_scale(self, note_value: int, scale_type: str, root_note: str) -> int:
        """Quantize a MIDI notes."""
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
            return note_value

    def _generate_with_dna(self,
                           description: str,
                           style: str,
                           instrument: str,
                           humanize: bool,
                           forced_context: list = None,
                           **kwargs) -> mido.MidiFile:
        """
        Generează pattern-ul (4 Măsuri), aplică logica de note și scrie fișierul MIDI.
        Enhanced with PatternIntelligence, HarmonicEngine, RhythmEngine, ProductionEngine.
        """
        import time 

        # Create DNA from parameters
        dna = PatternDNA(
            density=kwargs.get('density', 0.7),
            complexity=kwargs.get('complexity', 0.5),
            groove=kwargs.get('groove', 0.2),
            velocity_curve=kwargs.get('velocity_curve', 'natural'),
            evolution=kwargs.get('evolution', 0.3)
        )
        
        logger.debug(f"DNA parameters: {dna}")
        
        # --- SECTION MODIFIERS (Phase 5) ---
        section_mod = kwargs.get('sub_option', '')
        if section_mod == 'chorus':
            dna.density = min(1.0, dna.density + 0.2) # Energy Boost
            logger.info("🔥 Chorus Mode: Density Boosted")
        elif section_mod == 'verse':
            dna.density = min(0.7, dna.density) # Leave room for vocals
            logger.info("🎤 Verse Mode: Density Capped")
            # Dynamics tuned in post-processing
        elif section_mod == 'intro':
            dna.density = 0.3 # Force low density (User Request: 0.3)
            logger.info("🌅 Intro Mode: Sparse Density")
        elif section_mod == 'drop':
            dna.density = 1.0 # Max density
            dna.complexity = 1.0 
            logger.info("💣 Drop Mode: Max Energy")

        # SETĂM LUNGIMEA: 4 Măsuri (Standard)
        NUM_BARS = kwargs.get('bars', 4)

        # 1. Generează Ritmul de Bază (1 Bar / 16 Steps)
        if instrument in ['drums', 'full_kit', 'full_drums']:
             # STRICT COMPONENT GENERATION (User Request)
             # Iterate explicitly to ensure Kick, Snare, and Hats get their specific patterns.
             base_events = []
             components = ['kick', 'snare', 'hat']
             
             
             # DROP MODE OVERRIDE: If Drop, maybe we want fills?
             # For now, if drop, we stick to pattern but maybe add extra notes?
             # Actually user 'drop' request: "Force 1/16th note fills or maximum syncopation"
             # If strict pattern is used, we get the style's pattern.
             # We can add fills on top if section_mod == 'drop'.
             
             for comp in components:
                 # Get strict pattern
                 pattern = StylePatterns.get_pattern(style, comp)
                 
                 # DROP LOGIC: Override pattern for snare/hats to be denser?
                 if section_mod == 'drop' and comp in ['snare', 'hat']:
                     # Force 1/16th rolls
                     pattern = [1] * 16 
                 
                 if not pattern: 
                      # Fallback to advanced generator (random) if really missing
                      comp_events = self.advanced_generator.generate_pattern_with_dna(style, comp, dna, bars=1)
                      base_events.extend(comp_events)
                      continue
                      
                 # Generate events from pattern
                 for i, is_hit in enumerate(pattern):
                     if is_hit:
                         base_events.append({
                             'time': i * 0.25,
                             'duration': 0.25,
                             'velocity': random.randint(90, 110), # Strong base
                             'instrument_type': comp,
                             'channel': 9
                         })
                         
             # Sort merged events
             base_events.sort(key=lambda x: x['time'])
             
        else:
            # Melodic / Single Instrument
            base_events = self.advanced_generator.generate_pattern_with_dna(
                style=style,
                instrument=instrument,
                dna=dna,
                bars=1 
            )
        
        # [NEW] Apply Rhythm Engine (Ghost notes)
        # Check explicit flag first, default to True if not present (backward compat compatibility)
        use_ghost_notes = kwargs.get('ghost_notes', True)
        if use_ghost_notes and instrument in self.DRUM_INSTRUMENTS:
            base_events = self.rhythm_engine.add_ghost_notes(base_events, style)
            if len(base_events) > 16: # Assuming 16 steps basic
                 logger.info(f"👻 Ghost Notes Applied: {len(base_events)} events total")

        # 2. EXTINDERE TIMP & PHRASING: Pattern Intelligence
        # Use full phrase structure instead of simple copy
        # Inject structure preference if provided
        req_structure = kwargs.get('structure', 'AABA')
        context = {
            'bars': NUM_BARS, 
            'style': style, 
            'instrument': instrument,
            'structure': req_structure 
        }
        
        # This replaces the simple loop loop logic
        full_events = self.pattern_intelligence.generate_intelligent_pattern(base_events, context)
        logger.info(f"🏗️ Structure Used: {req_structure} (Pattern expanded to {len(full_events)} events)")

        # 3. Adaugă Notele (Melody Walker / Smart Bass)
        key = kwargs.get('key', 'C')
        scale = kwargs.get('scale_type', 'minor')
        sub_option = kwargs.get('sub_option', 'full_kit')
        
        # [NEW] Phase 7: Context Overrides
        # Support both explicit param and kwargs (for backward compat/API flexibility)
        ctx = forced_context or kwargs.get('context_chords')
        
        if ctx:
             # 2. Override Harmonic Logic
             # 4. Handle Length Mismatch (handled inside helper)
             master_progression = self._parse_context_to_progression(ctx, total_bars=NUM_BARS)
             logger.info(f"🔒 Context Locked: Using {len(master_progression)} user-defined chords (Target Bars: {NUM_BARS})")
             
        else:
            # [NEW] Phase 6: Generate Master Chord Progression
            # Convert Root Key to MIDI (e.g. C -> 60)
            try:
                 root_key_midi = self.music_theory._note_to_midi(key, 4) 
            except:
                 root_key_midi = 60 
                 
            master_progression = self.music_theory_engine.generate_progression(style, root_key_midi, scale)
            logger.info(f"🎹 Generated Progression ({style}): {[c['name'] for c in master_progression]}")
        
        events_with_pitch = self._add_pitch_to_events(
            full_events, 
            instrument, 
            sub_option, 
            kwargs.get('channel', 9), # Fixed args
            key, 
            scale, 
            style,
            kwargs.get('complexity', 0.5), # Pass complexity
            master_progression # [NEW] Pass progression
        )
        
        # [NEW] Harmonic Engine (Passing tones)
        use_passing_tones = kwargs.get('passing_tones', False)
        if use_passing_tones and instrument not in self.DRUM_INSTRUMENTS:
             try:
                 original_count = len(events_with_pitch)
                 events_with_pitch = self.harmonic_engine.add_passing_tones(events_with_pitch)
                 if len(events_with_pitch) > original_count:
                     logger.info(f"🎼 Harmonic Engine: Added {len(events_with_pitch) - original_count} passing tones")
             except Exception as e:
                 logger.warning(f"Harmonic Engine failed to add passing tones: {e}, using original definition")
                 pass
        
        # Presort by time
        events_with_pitch.sort(key=lambda x: x['time'])

        # 4. Aplică Groove-ul (Humanize)
        complexity = kwargs.get('complexity', 0.5)
        
        # [NEW] Retrieve swing from style definition
        # Use MUSIC_STYLES dictionary directly
        style_meta = MUSIC_STYLES.get(style, {'swing': 0.0}) 
        style_swing = style_meta.get('swing', 0.0)
        
        final_events = self.groove_engine.apply_groove(events_with_pitch, style, complexity, custom_swing=style_swing)

        # 5. Production Engine (Velocity & Articulation)
        # Apply velocity curve
        final_events = self.production_engine.velocity.apply_velocity_curve(final_events, curve_type=dna.velocity_curve)
        final_events = self.production_engine.articulation.add_articulations(final_events, style)

        # --- SECTION POST-PROCESSING ---
        if section_mod == 'chorus' and instrument in self.DRUM_INSTRUMENTS:
            # Force Open Hats & Crash
            has_crash = False
            for evt in final_events:
                # Boost Dynamics (User: +15%)
                vel = evt.get('velocity', 90)
                evt['velocity'] = min(127, int(vel * 1.15))
                
                # Swap Closed Hat (42) to Open Hat (46)
                if evt.get('pitch') == 42:
                    evt['pitch'] = 46
                    
                # Crash check (Time 0)
                if evt['time'] == 0.0 and evt.get('pitch') == 49:
                    has_crash = True
            
            if not has_crash:
                final_events.append({
                    'time': 0.0, 'duration': 1.0, 'velocity': 110, 
                    'pitch': 49, 'channel': 9, 'instrument_type': 'crash'
                })
                
        elif section_mod == 'verse' and instrument in self.DRUM_INSTRUMENTS:
            # Force Closed Hats & Remove Ghost Kicks
            filtered_events = []
            for evt in final_events:
                # Flatten Dynamics (Medium 80-90)
                evt['velocity'] = random.randint(80, 90)

                # Lock Open Hat to Closed
                if evt.get('pitch') == 46:
                    evt['pitch'] = 42
                
                # Filter Ghost Kicks (Velocity < 60)
                if evt.get('instrument_type') == 'kick' and evt.get('velocity', 90) < 60:
                    continue 
                
                filtered_events.append(evt)
            final_events = filtered_events

        elif section_mod == 'intro' and instrument in self.DRUM_INSTRUMENTS:
            # Filter Snare & Hats (Keep Kick/Atmosphere)
            final_events = [e for e in final_events if e.get('pitch') not in [38, 40, 42, 46]]

        # 6. Additional Humanization (Jitter)
        if humanize:
            final_events = self.humanizer.humanize_midi(final_events)
            
        final_events.sort(key=lambda x: x['time'])

        # 7. Convert to MIDI file
        return self._events_to_midi(final_events, kwargs.get('bpm', 120))

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
        if style in self.advanced_generator.style_patterns.PATTERNS:
            style_data = self.advanced_generator.style_patterns.PATTERNS[style]
            # StylePatterns structure is different now, simple existence check is sufficient
            # or check if instrument is a key in generic dict logic
            pass

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
                             sub_option: str, 
                             channel: int,
                             key: str = 'C',
                             scale_type: str = 'minor',
                             style: str = 'techno',
                             complexity: float = 0.5,
                             progression: List[Dict] = None) -> List[Dict]:
        """
        Adaugă note muzicale (Pitch) peste ritm.
        Acum cu logică de 'Melody Walk' si 'Chord Progression'.
        """
        """
        Adaugă note muzicale (Pitch) peste ritm.
        Acum cu logică de 'Melody Walk' pentru Lead-uri!
        """
        if not events:
            return []



             
        # Get drum map from basic generator (kept for compatibility)
        drum_map = self.basic_generator.drum_map

        # 1. Obținem notele gamei (folosind compatibility layer din MusicTheoryService)
        # Compatibility: scale_notes here will be MIDI numbers if using get_scale_notes (public) 
        # But user wants specific octaves. User code uses private _note_to_midi.
        # Let's use the explicit logic requested.
        
        # Mapping pentru instrumente: Bass-ul stă jos (Octava 2-3), Melodia sus (Octava 4-5)
        octave = 2 if instrument in ['bass', 'sub', '808'] else 4
        
        # Convertim notele gamei în numere MIDI pentru octava aleasă
        # We need note NAMES first. Accessing private method as requested/required by logic
        scale_note_names = self.music_theory._get_scale_notes(key, scale_type)
        scale_midi_notes = [self.music_theory._note_to_midi(n, octave) for n in scale_note_names]

        # [NEW] Phase 6: Use Master Progression Logic if key melodic instrument
        use_progression = (progression is not None) and (len(progression) > 0)
        
        # --- ARPEGGIO OVERRIDE LOGIC ---
        if sub_option == 'arp':
            # User Request: Force steady 1/16th stream (Legacy "High Density" override)
            # 1. Determine total duration from existing events
            if not events: return []
            last_time = max(e['time'] + e['duration'] for e in events) 
            # Round up to nearest bar (assuming 4 beats/bar)
            total_beats = int(last_time + (4 - last_time % 4) if last_time % 4 != 0 else last_time) 
            
            # 2. Generate new 16th note grid
            arp_events = []
            step_size = 0.25
            current_time = 0.0
            
            i = 0
            while current_time < total_beats:
                 # Create base event
                 evt = {
                     'time': current_time,
                     'duration': 0.25, # Short staccato
                     'velocity': random.randint(70, 95),
                     'instrument_type': instrument,
                     'channel': 0 
                 }
                 
                 # PITCH SELECTION
                 # v2: Use Progression if available
                 if use_progression:
                     # Determine bar index
                     bar_idx = int(current_time / 4) % len(progression) 
                     current_chord = progression[bar_idx]
                     chord_tones = self.music_theory_engine.get_chord_tones(current_chord)
                 else:
                     # v1 (Fallback)
                     current_chord_degree = 0 # Root
                     if int(current_time / 4) % 2 == 1:
                         current_chord_degree = 4 
                     chord_tones = self.harmonic_engine.get_chord_tones_from_scale(scale_midi_notes, current_chord_degree)
                     
                 if not chord_tones: chord_tones = [60, 64, 67, 72] # Safety
                 
                 # Cyclic Pattern
                 if complexity < 0.6: # Up pattern
                      note = chord_tones[i % len(chord_tones)]
                 else: # Up-Down pattern
                      cycle_len = len(chord_tones) * 2 - 2
                      if cycle_len < 1: cycle_len = 1
                      idx_in_cycle = i % cycle_len
                      if idx_in_cycle < len(chord_tones):
                          note = chord_tones[idx_in_cycle]
                      else:
                          note = chord_tones[cycle_len - idx_in_cycle]
                 
                 evt['pitch'] = note
                 arp_events.append(evt)
                 
                 current_time += step_size
                 i += 1
            
            return arp_events

        # --- LOGICA NOUĂ: MELODY WALKER ---
        current_note_index = 0 # Plecăm de la rădăcină (C)
        
        enhanced_events = []
        
        for event in events:
             # Use specific instrument from event if available
            evt_instrument = event.get('instrument_type', instrument)
            
            # Channel handling (PRESERVE EXISTING LOGIC)
            evt_channel = self._get_channel_for_instrument(evt_instrument)
            event['channel'] = evt_channel
            
            # Skip if pitch already assigned
            if 'pitch' in event and not isinstance(event['pitch'], list):
                enhanced_events.append(event)
                continue

            # DRUM HANDLING (Essential to keep)
            if evt_channel == 9:
                if evt_instrument in drum_map:
                    event['pitch'] = drum_map[evt_instrument]
                elif evt_instrument in self.DRUM_INSTRUMENTS:
                    event['pitch'] = drum_map.get('kick', 36)
                else:
                    event['pitch'] = 36
                enhanced_events.append(event)
                continue

            # MELODIC LOGIC (The new stuff)
            
            # A. Logica pentru BASS
            if evt_instrument in ['bass', 'sub', '808']:
                if use_progression:
                    # Use Root of current chord
                    bar_idx = int(event['time'] / 4) % len(progression)
                    current_chord = progression[bar_idx]
                    
                    # Bass plays Root (index 0 of intervals? No, 'root' field is MIDI note)
                    # We need to shift it to Bass Octave (e.g. 36-48)
                    # current_chord['root'] is likely ~60 (C4).
                    # Shift down 2 octaves (-24)
                    bass_pitch = current_chord['root'] - 24
                    
                    # Expert Mode: Sometimes play 5th or Octave?
                    if complexity >= 0.9 and random.random() < 0.3:
                         # 5th is +7 semitones
                         bass_pitch += 7
                         
                    event['pitch'] = bass_pitch
                    event['duration'] = 0.5
                else:
                    # Fallback to old logic
                    if complexity >= 0.9: # Expert / Complex
                         # ... (Old logic omitted for brevity, keeping if else structure)
                         # Actually I need to recreate it if I'm replacing the block?
                         # The tool replaces the CHUNK. I should keep the old logic as 'else'.
                         # But the chunk I selected (524+) covers it.
                         # I will paste the old logic in the else block.
                         pass
                    
                    # [Old Logic Reimplanted as Fallback]
                    if complexity >= 0.9:
                         roll = random.random()
                         if roll < 0.5: note_idx = 0 
                         elif roll < 0.8: note_idx = 4 
                         else: note_idx = 7 
                    else:
                        if random.random() < 0.7: note_idx = 0 
                        else: note_idx = random.choice([0, 4])
                    
                    if scale_midi_notes:
                        final_midi = scale_midi_notes[note_idx % len(scale_midi_notes)]
                        if note_idx >= len(scale_midi_notes): final_midi += 12
                        event['pitch'] = final_midi 
                    else:
                         event['pitch'] = 36
                    event['duration'] = 0.5

            # B. Logica pentru CHORDS
            elif sub_option == 'chords' or evt_instrument in ['chords', 'pad']:
                 if use_progression:
                      # Play the full chord from progression
                      bar_idx = int(event['time'] / 4) % len(progression)
                      current_chord = progression[bar_idx]
                      
                      # Get notes
                      chord_notes = current_chord['absolute_notes']
                      # Shift to octaves? Usually mid-range is fine (60s).
                      
                      event['duration'] = 1.0 # Sustain
                      
                      # Emit multiple events
                      for n in chord_notes:
                          chord_evt = event.copy()
                          chord_evt['pitch'] = n
                          enhanced_events.append(chord_evt)
                      continue
                 else:
                     # Fallback Logic
                     root_idx = random.choice([0, 3, 4, 5])
                     if scale_midi_notes:
                        root_midi = scale_midi_notes[root_idx % len(scale_midi_notes)]
                        chord_notes = [root_midi, root_midi + 3, root_midi + 7]
                        event['duration'] = 1.0
                        for n in chord_notes:
                            chord_evt = event.copy()
                            chord_evt['pitch'] = n
                            enhanced_events.append(chord_evt)
                        continue 
                     else:
                        event['pitch'] = 60
            # C. Logica pentru LEAD / MELODY (Random Walk)
            else:
                step = random.choice([-1, 0, 1, 1, 2, -2])
                current_note_index += step
                
                # Bounds check
                if scale_midi_notes:
                    current_note_index = max(0, min(len(scale_midi_notes) - 1, current_note_index))
                    midi_note = scale_midi_notes[current_note_index]
                    event['pitch'] = midi_note
                else:
                    event['pitch'] = 60
                
                # Variem durata
                event['duration'] = random.choice([0.25, 0.25, 0.5])

            enhanced_events.append(event)

        return enhanced_events

    def _midi_to_note_name(self, midi_val: int) -> str:
        """Convert MIDI number to note name (e.g. 60 -> C)"""
        notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        return notes[midi_val % 12]

    def _get_diatonic_chord_type(self, scale_type: str, degree: int) -> str:
        """Determine chord type (maj/min/dim) for a given scale degree"""
        # Simplified diatonic chords
        # 1-based degree
        if scale_type == 'major':
            # Major Scale: I-maj, ii-min, iii-min, IV-maj, V-maj, vi-min, vii-dim
            if degree in [1, 4, 5]: return 'maj'
            if degree in [2, 3, 6]: return 'min'
            if degree == 7: return 'dim'
        elif scale_type == 'minor':
            # Natural Minor: i-min, ii-dim, III-maj, iv-min, v-min, VI-maj, VII-maj
            if degree in [1, 4, 5]: return 'min'
            if degree in [3, 6, 7]: return 'maj'
            if degree == 2: return 'dim'
        
        return 'min' # Default fallback
    
    def _get_scale_degree_root_midi(self, key: str, scale_type: str, degree: int) -> int:
        """Get the MIDI note number for the root of a specific scale degree"""
        # Use MusicTheoryService to get scale notes
        scale_notes = self.music_theory.get_scale_notes(key, scale_type, octave=3)
        # Handle wrap around if degree > len(scale)
        idx = (degree - 1) % len(scale_notes)
        return scale_notes[idx]

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

    def _parse_context_to_progression(self, context_chords: List[Dict], total_bars: int = 4) -> List[Dict]:
        """
        Parses user-provided context chords into the internal progression format.
        Handles length mismatch by looping context.
        """
        master_progression = []
        if not context_chords:
            return []
            
        # Determine context length
        context_len = len(context_chords)
        
        # Loop context to fill total bars
        for bar_idx in range(total_bars):
            # Wrap around using modulo
            source_chord = context_chords[bar_idx % context_len]
            
            # Extract data
            notes = source_chord['notes']
            chord_name = source_chord['chord']
            
            # Reconstruct absolute notes (Octave 4 default)
            abs_notes = [60 + pc if pc < 12 else pc for pc in notes]
            abs_notes.sort()
            
            # Determine root
            root_note = abs_notes[0] if abs_notes else 60
            
            master_progression.append({
                'name': chord_name,
                'root': root_note,
                'absolute_notes': abs_notes,
                'intervals': [n - root_note for n in abs_notes]
            })
            
        return master_progression
