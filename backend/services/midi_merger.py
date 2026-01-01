# backend/services/midi_merger.py
"""
MIDI Merger Service
Combines multiple single-track MIDI files into one multi-track MIDI file (Type 1)
"""

from mido import MidiFile, MidiTrack, MetaMessage, Message
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class MidiMerger:
    """
    Merge multiple MIDI files into a single multi-track MIDI file
    Handles tempo, time signature, and track synchronization
    """

    def __init__(self, bpm: int = 120, time_signature: tuple = (4, 4)):
        """
        Initialize merger with global project settings

        Args:
            bpm: Beats per minute for the project
            time_signature: Time signature as (numerator, denominator)
        """
        self.bpm = bpm
        self.time_signature = time_signature
        self.ticks_per_beat = 480  # Standard MIDI resolution

    def merge_tracks(self, track_files: List[Dict[str, Any]], output_path: str) -> Path:
        """
        Merge multiple MIDI files into one Type 1 MIDI file

        Args:
            track_files: List of dicts with keys:
                - 'path': Path to MIDI file
                - 'name': Track name
                - 'volume': Track volume (0.0-1.0)
                - 'pan': Track pan (0.0-1.0, 0.5 = center)
                - 'muted': Boolean, if True track is muted
            output_path: Where to save the merged MIDI file

        Returns:
            Path to the created MIDI file
        """
        logger.info(f"Merging {len(track_files)} tracks into {output_path}")

        # Create new Type 1 MIDI file (multi-track)
        merged_midi = MidiFile(type=1, ticks_per_beat=self.ticks_per_beat)

        # Track 0: Tempo and time signature (conductor track)
        tempo_track = MidiTrack()
        merged_midi.tracks.append(tempo_track)

        # Add tempo (microseconds per beat)
        tempo_track.append(MetaMessage('set_tempo', tempo=self._bpm_to_tempo(self.bpm), time=0))

        # Add time signature
        tempo_track.append(MetaMessage(
            'time_signature',
            numerator=self.time_signature[0],
            denominator=self.time_signature[1],
            time=0
        ))

        # Add track name
        tempo_track.append(MetaMessage('track_name', name='Conductor', time=0))

        # Add end of track
        tempo_track.append(MetaMessage('end_of_track', time=0))

        # Process each input track
        for idx, track_info in enumerate(track_files):
            try:
                self._add_track(merged_midi, track_info, idx + 1)
            except Exception as e:
                logger.error(f"Error adding track {track_info.get('name', 'Unknown')}: {e}")
                # Continue with other tracks even if one fails

        # Save merged file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        merged_midi.save(str(output_file))

        logger.info(f"Merged MIDI file created: {output_file} ({len(merged_midi.tracks)} tracks)")
        return output_file

    def _add_track(self, merged_midi: MidiFile, track_info: Dict[str, Any], track_number: int):
        """Add a single track to the merged MIDI file"""
        track_path = track_info['path']
        track_name = track_info.get('name', f'Track {track_number}')
        volume = track_info.get('volume', 0.8)
        pan = track_info.get('pan', 0.5)
        muted = track_info.get('muted', False)

        logger.debug(f"Adding track: {track_name} from {track_path}")

        # Load source MIDI file
        source_midi = MidiFile(track_path)

        # Create new track
        new_track = MidiTrack()
        merged_midi.tracks.append(new_track)

        # Add track name
        new_track.append(MetaMessage('track_name', name=track_name, time=0))

        # Set MIDI channel (max 16 channels, wrap around if needed)
        channel = (track_number - 1) % 16

        # Add initial volume and pan control changes
        if not muted:
            # Volume (CC 7)
            volume_value = int(volume * 127)
            new_track.append(Message('control_change', control=7, value=volume_value, channel=channel, time=0))

            # Pan (CC 10)
            pan_value = int(pan * 127)
            new_track.append(Message('control_change', control=10, value=pan_value, channel=channel, time=0))

        # Copy all note events from source tracks
        absolute_time = 0
        for source_track in source_midi.tracks:
            for msg in source_track:
                absolute_time += msg.time

                # Skip meta messages (except some we want to keep)
                if msg.is_meta:
                    # Keep certain meta messages
                    if msg.type in ['lyric', 'marker', 'cue_marker']:
                        new_track.append(msg.copy(time=msg.time))
                    continue

                # Copy note messages
                if msg.type in ['note_on', 'note_off']:
                    if muted:
                        # If muted, skip note events
                        continue

                    # Copy message with correct channel
                    new_msg = msg.copy(channel=channel, time=msg.time)
                    new_track.append(new_msg)

                # Copy control change messages
                elif msg.type == 'control_change':
                    new_msg = msg.copy(channel=channel, time=msg.time)
                    new_track.append(new_msg)

                # Copy program change messages
                elif msg.type == 'program_change':
                    new_msg = msg.copy(channel=channel, time=msg.time)
                    new_track.append(new_msg)

        # Add end of track
        new_track.append(MetaMessage('end_of_track', time=0))

    def _bpm_to_tempo(self, bpm: int) -> int:
        """
        Convert BPM to MIDI tempo (microseconds per beat)

        Args:
            bpm: Beats per minute

        Returns:
            Tempo in microseconds per beat
        """
        return int(60_000_000 / bpm)

    def create_empty_project(self, output_path: str, bars: int = 4) -> Path:
        """
        Create an empty MIDI project file with just tempo/time signature

        Args:
            output_path: Where to save the file
            bars: Number of bars for the project length

        Returns:
            Path to the created file
        """
        midi = MidiFile(type=1, ticks_per_beat=self.ticks_per_beat)

        # Conductor track
        track = MidiTrack()
        midi.tracks.append(track)

        track.append(MetaMessage('track_name', name='Empty Project', time=0))
        track.append(MetaMessage('set_tempo', tempo=self._bpm_to_tempo(self.bpm), time=0))
        track.append(MetaMessage(
            'time_signature',
            numerator=self.time_signature[0],
            denominator=self.time_signature[1],
            time=0
        ))

        # Calculate total ticks for project length
        ticks_per_bar = self.ticks_per_beat * self.time_signature[0]
        total_ticks = ticks_per_bar * bars

        track.append(MetaMessage('end_of_track', time=total_ticks))

        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        midi.save(str(output_file))

        return output_file


# Convenience function
def merge_midi_files(
    track_files: List[Dict[str, Any]],
    output_path: str,
    bpm: int = 120,
    time_signature: tuple = (4, 4)
) -> Path:
    """
    Merge multiple MIDI files into one multi-track file

    Args:
        track_files: List of track info dicts
        output_path: Output file path
        bpm: Project tempo
        time_signature: Project time signature

    Returns:
        Path to merged MIDI file
    """
    merger = MidiMerger(bpm=bpm, time_signature=time_signature)
    return merger.merge_tracks(track_files, output_path)
