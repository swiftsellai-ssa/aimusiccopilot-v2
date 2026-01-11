import mido
import math
from typing import List, Dict, Optional
from services.music_theory_engine import MusicTheoryEngine

class MidiAnalyzer:
    def __init__(self):
        self.theory = MusicTheoryEngine()
        # Invert the interval map for detection: tuple(intervals) -> chord_type
        # e.g. (0, 4, 7) -> 'maj'
        self.interval_map = {}
        for c_type, intervals in self.theory.CHORD_INTERVALS.items():
            self.interval_map[tuple(intervals)] = c_type

    def analyze_structure(self, midi_file_bytes: bytes) -> Dict:
        """
        Analyzes MIDI bytes to extract BPM and Harmonic Structure.
        """
        # Save bytes to temp file because mido.MidiFile wants a path or file-like object
        # Mido can read from BytesIO file-like object? Yes.
        import io
        
        mid = mido.MidiFile(file=io.BytesIO(midi_file_bytes))
        
        # 1. Detect BPM (from Tempo meta messages)
        bpm = 120 # Default
        for track in mid.tracks:
            for msg in track:
                if msg.type == 'set_tempo':
                    bpm = int(mido.tempo2bpm(msg.tempo))
                    break # Take first tempo found
            if bpm != 120: break
            
        # 2. Flatten all notes to absolute time
        notes = []
        ticks_per_beat = mid.ticks_per_beat
        
        for track in mid.tracks:
            curr_ticks = 0
            for msg in track:
                curr_ticks += msg.time
                if msg.type == 'note_on' and msg.velocity > 0:
                    notes.append({
                        'note': msg.note,
                        'start_tick': curr_ticks,
                        'velocity': msg.velocity
                    })
        
        # Sort by time
        notes.sort(key=lambda x: x['start_tick'])
        
        if not notes:
            return {"bpm": bpm, "bars": []}

        # 3. Bar Analysis
        # Assuming 4/4 for now
        ticks_per_bar = ticks_per_beat * 4
        total_ticks = notes[-1]['start_tick']
        total_bars = math.ceil(total_ticks / ticks_per_bar)
        
        analyzed_bars = []
        
        for bar_idx in range(total_bars):
            start_t = bar_idx * ticks_per_bar
            end_t = (bar_idx + 1) * ticks_per_bar
            
            # Get notes in this bar
            bar_notes = [n['note'] for n in notes if start_t <= n['start_tick'] < end_t]
            
            if not bar_notes:
                continue
                
            # Detect Chord
            # 1. Get unique pitch classes (0-11)
            pitch_classes = sorted(list(set([n % 12 for n in bar_notes])))
            
            detected_chord = "Unknown"
            
            # Brute force root: Try every note in the set as root
            best_match = None
            
            for root in pitch_classes:
                # Calculate intervals relative to this root
                current_intervals = tuple(sorted([(pc - root) % 12 for pc in pitch_classes]))
                
                # Check exact match
                if current_intervals in self.interval_map:
                    chord_type = self.interval_map[current_intervals]
                    # Convert root pitch class to Note Name
                    root_name = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'][root]
                    best_match = f"{root_name} {chord_type}"
                    break
                
                # Check subset match (e.g. if we have 7th but ignore it, or missed a note)
                # Simple heuristic: Look for major/minor triad
                base_triad = (0, 4, 7) # Major
                min_triad = (0, 3, 7) # Minor
                
                # Check if 0, 4, 7 is a subset of current_intervals
                if set(base_triad).issubset(set(current_intervals)):
                    root_name = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'][root]
                    best_match = f"{root_name} maj"
                    break
                if set(min_triad).issubset(set(current_intervals)):
                    root_name = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'][root]
                    best_match = f"{root_name} min"
                    break
            
            if best_match:
                detected_chord = best_match
            else:
                # Heuristic: Bass note is likely root?
                # Simple fallback: Just say "Poly"
                pass
                
            analyzed_bars.append({
                "bar": bar_idx + 1,
                "chord": detected_chord,
                "notes": pitch_classes # returning classes for debug
            })
            
        return {
            "bpm": bpm,
            "bars": analyzed_bars
        }
