'use client';

import { useState, useEffect, useRef } from 'react';
import * as Tone from 'tone';
import { Midi } from '@tonejs/midi';

interface MidiPlayerWithAudioProps {
  midiUrl: string;
  bpm?: number;
}

export default function MidiPlayerWithAudio({ midiUrl, bpm = 120 }: MidiPlayerWithAudioProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(-6); // dB
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isReady, setIsReady] = useState(false);

  const synthsRef = useRef<Tone.PolySynth[]>([]);
  const partsRef = useRef<Tone.Part[]>([]);
  const midiDataRef = useRef<Midi | null>(null);
  const animationFrameRef = useRef<number>();

  useEffect(() => {
    if (midiUrl) {
      loadAndParseMidi();
    }

    return () => {
      cleanup();
    };
  }, [midiUrl]);

  useEffect(() => {
    // Update synth volumes
    synthsRef.current.forEach(synth => {
      synth.volume.value = volume;
    });
  }, [volume]);

  const cleanup = () => {
    stop();
    partsRef.current.forEach(part => part.dispose());
    synthsRef.current.forEach(synth => synth.dispose());
    partsRef.current = [];
    synthsRef.current = [];
    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
  };

  const loadAndParseMidi = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Fetch MIDI file
      const response = await fetch(midiUrl);
      if (!response.ok) throw new Error('Failed to fetch MIDI file');

      const arrayBuffer = await response.arrayBuffer();
      const midi = new Midi(arrayBuffer);

      midiDataRef.current = midi;
      setDuration(midi.duration);

      // Create synths and parts for each track
      cleanup();

      midi.tracks.forEach((track, trackIndex) => {
        // Create a polyphonic synth for this track
        const synth = new Tone.PolySynth(Tone.Synth, {
          volume: volume,
          oscillator: {
            type: trackIndex === 0 ? 'triangle' : 'sine' // Different timbres
          },
          envelope: {
            attack: 0.005,
            decay: 0.1,
            sustain: 0.3,
            release: 0.1
          }
        }).toDestination();

        synthsRef.current.push(synth);

        // Create a Tone.Part for this track
        const notes = track.notes.map(note => ({
          time: note.time,
          note: note.name,
          duration: note.duration,
          velocity: note.velocity
        }));

        const part = new Tone.Part((time, note) => {
          synth.triggerAttackRelease(
            note.note,
            note.duration,
            time,
            note.velocity
          );
        }, notes);

        partsRef.current.push(part);
      });

      setIsLoading(false);
      setIsReady(true);
    } catch (err) {
      console.error('Failed to load MIDI:', err);
      setError('Failed to load MIDI file');
      setIsLoading(false);
    }
  };

  const play = async () => {
    if (!isReady) return;

    try {
      // Start Tone.js audio context
      await Tone.start();

      // Set transport position
      Tone.Transport.seconds = currentTime;

      // Start all parts
      partsRef.current.forEach(part => {
        part.start(0);
      });

      // Start transport
      Tone.Transport.start();
      setIsPlaying(true);

      // Start animation loop
      updateTime();
    } catch (err) {
      console.error('Playback error:', err);
      setError('Failed to start playback');
    }
  };

  const pause = () => {
    Tone.Transport.pause();
    setIsPlaying(false);

    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
  };

  const stop = () => {
    Tone.Transport.stop();
    Tone.Transport.seconds = 0;
    setIsPlaying(false);
    setCurrentTime(0);

    // Stop all parts
    partsRef.current.forEach(part => {
      part.stop();
    });

    if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
  };

  const updateTime = () => {
    if (!isPlaying) return;

    const time = Tone.Transport.seconds;
    setCurrentTime(time);

    // Auto-stop at end
    if (time >= duration) {
      stop();
      return;
    }

    animationFrameRef.current = requestAnimationFrame(updateTime);
  };

  const seek = (time: number) => {
    const wasPlaying = isPlaying;

    if (wasPlaying) {
      pause();
    }

    Tone.Transport.seconds = time;
    setCurrentTime(time);

    if (wasPlaying) {
      play();
    }
  };

  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const downloadMidi = () => {
    const link = document.createElement('a');
    link.href = midiUrl;
    link.download = `pattern_${Date.now()}.mid`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (error) {
    return (
      <div className="bg-gray-900 p-6 rounded-lg border border-red-500">
        <div className="text-red-500 mb-4">
          <h3 className="text-xl font-bold mb-2">❌ Error</h3>
          <p>{error}</p>
        </div>
        <button
          onClick={downloadMidi}
          className="px-6 py-2 bg-green-600 hover:bg-green-700 rounded-lg"
        >
          Download MIDI File Instead
        </button>
      </div>
    );
  }

  return (
    <div className="bg-gray-900 p-6 rounded-lg border border-gray-800">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-xl font-bold">🎵 MIDI Player with Audio</h3>
        <div className="flex items-center gap-4">
          {midiDataRef.current && (
            <div className="text-sm text-gray-400">
              {midiDataRef.current.tracks.length} track(s)
            </div>
          )}
          {bpm && (
            <div className="text-sm text-gray-400 font-mono">
              {bpm} BPM
            </div>
          )}
        </div>
      </div>

      {isLoading ? (
        <div className="text-center py-8">
          <div className="animate-pulse">
            <div className="text-4xl mb-2">🎹</div>
            <p className="text-gray-400">Loading MIDI...</p>
          </div>
        </div>
      ) : (
        <>
          {/* Waveform Visualization */}
          <div className="mb-6 bg-gray-800 rounded-lg p-4">
            <div className="relative h-24 flex items-center">
              {/* Simulated waveform bars */}
              <div className="flex items-end justify-around w-full h-full gap-1">
                {Array.from({ length: 50 }).map((_, i) => {
                  const height = 20 + Math.random() * 80;
                  const isActive = (currentTime / duration) * 50 > i;
                  return (
                    <div
                      key={i}
                      className={`flex-1 rounded-t transition-all ${
                        isActive && isPlaying
                          ? 'bg-gradient-to-t from-green-500 to-blue-500 animate-pulse'
                          : isActive
                          ? 'bg-gradient-to-t from-blue-500 to-purple-500'
                          : 'bg-gray-700'
                      }`}
                      style={{ height: `${height}%` }}
                    />
                  );
                })}
              </div>

              {/* Playhead */}
              <div
                className={`absolute top-0 bottom-0 w-0.5 transition-all ${
                  isPlaying ? 'bg-green-400 shadow-lg shadow-green-400/50' : 'bg-white shadow-lg shadow-white/50'
                }`}
                style={{ left: `${(currentTime / duration) * 100}%` }}
              />
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mb-4">
            <input
              type="range"
              min="0"
              max={duration}
              step="0.1"
              value={currentTime}
              onChange={(e) => seek(parseFloat(e.target.value))}
              className="w-full accent-blue-600 cursor-pointer"
              disabled={isLoading}
            />
            <div className="flex justify-between text-xs text-gray-400 mt-1">
              <span>{formatTime(currentTime)}</span>
              <span>{formatTime(duration)}</span>
            </div>
          </div>

          {/* Controls */}
          <div className="flex items-center justify-between gap-4 flex-wrap">
            {/* Playback Controls */}
            <div className="flex items-center gap-3">
              {/* Stop */}
              <button
                onClick={stop}
                disabled={!isPlaying && currentTime === 0}
                className="p-3 bg-gray-800 hover:bg-gray-700 disabled:bg-gray-800 disabled:opacity-50 rounded-lg transition-all"
                title="Stop"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <rect x="6" y="6" width="12" height="12" />
                </svg>
              </button>

              {/* Play/Pause */}
              <button
                onClick={isPlaying ? pause : play}
                disabled={!isReady}
                className="p-4 bg-gradient-to-r from-green-600 to-blue-600 hover:shadow-lg hover:shadow-green-500/50 rounded-lg transition-all disabled:opacity-50"
                title={isPlaying ? 'Pause' : 'Play'}
              >
                {isPlaying ? (
                  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                    <rect x="6" y="4" width="4" height="16" />
                    <rect x="14" y="4" width="4" height="16" />
                  </svg>
                ) : (
                  <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M8 5v14l11-7z" />
                  </svg>
                )}
              </button>
            </div>

            {/* Volume Control */}
            <div className="flex items-center gap-2 flex-1 max-w-xs">
              <svg className="w-5 h-5 text-gray-400" fill="currentColor" viewBox="0 0 24 24">
                <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z" />
              </svg>
              <input
                type="range"
                min="-40"
                max="0"
                step="1"
                value={volume}
                onChange={(e) => setVolume(parseFloat(e.target.value))}
                className="flex-1 accent-blue-600"
                title="Volume"
              />
              <span className="text-xs text-gray-400 w-12 text-right">
                {Math.round(((volume + 40) / 40) * 100)}%
              </span>
            </div>

            {/* Download Button */}
            <button
              onClick={downloadMidi}
              className="px-6 py-3 bg-green-600 hover:bg-green-700 rounded-lg font-semibold transition-all shadow-lg hover:shadow-green-500/50 flex items-center gap-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Download
            </button>
          </div>

          {/* Info Note */}
          <div className="mt-4 p-3 bg-green-900/20 border border-green-500/30 rounded-lg">
            <p className="text-xs text-green-300">
              🎵 <strong>Real Audio Playback:</strong> This player uses Tone.js to synthesize MIDI notes into actual audio. Click Play to hear your pattern!
            </p>
          </div>

          {/* Track Info */}
          {midiDataRef.current && midiDataRef.current.tracks.length > 0 && (
            <div className="mt-4 p-3 bg-blue-900/20 border border-blue-500/30 rounded-lg">
              <div className="text-xs text-blue-300">
                <div className="font-semibold mb-1">Track Details:</div>
                {midiDataRef.current.tracks.map((track, i) => (
                  <div key={i} className="flex justify-between py-1">
                    <span>Track {i + 1}: {track.name || 'Unnamed'}</span>
                    <span>{track.notes.length} notes</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
