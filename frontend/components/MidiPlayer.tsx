'use client';

import { useState, useEffect, useRef } from 'react';

interface MidiPlayerProps {
  midiUrl: string;
  bpm?: number;
}

// Generate stable waveform heights outside component
const WAVEFORM_HEIGHTS = Array.from({ length: 50 }, () => 20 + Math.random() * 80);

export default function MidiPlayer({ midiUrl, bpm = 120 }: MidiPlayerProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.7);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Using Web Audio API for MIDI playback
  const audioContextRef = useRef<AudioContext | null>(null);
  const sourceNodeRef = useRef<AudioBufferSourceNode | null>(null);
  const gainNodeRef = useRef<GainNode | null>(null);
  const startTimeRef = useRef<number>(0);
  const pausedAtRef = useRef<number>(0);

  const stop = () => {
    setIsPlaying(false);
    setCurrentTime(0);
    pausedAtRef.current = 0;
    startTimeRef.current = 0;

    if (sourceNodeRef.current) {
      try {
        sourceNodeRef.current.stop();
      } catch (e) {
        // Already stopped
      }
      sourceNodeRef.current = null;
    }
  };

  const loadMidi = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Estimate duration from BPM and file size (rough estimate)
      const estimatedDuration = 60; // Default 60 seconds
      setDuration(estimatedDuration);
      setIsLoading(false);
    } catch (err) {
      console.error('Failed to load MIDI:', err);
      setError('Failed to load MIDI file');
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // Initialize Audio Context
    if (typeof window !== 'undefined' && !audioContextRef.current) {
      const AudioContextClass = window.AudioContext || (window as typeof window & { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      audioContextRef.current = new AudioContextClass();
      gainNodeRef.current = audioContextRef.current.createGain();
      gainNodeRef.current.connect(audioContextRef.current.destination);
    }

    return () => {
      stop();
    };
  }, []);

  useEffect(() => {
    if (midiUrl) {
      loadMidi();
    }
  }, [midiUrl]);

  useEffect(() => {
    if (gainNodeRef.current) {
      gainNodeRef.current.gain.value = volume;
    }
  }, [volume]);

  const play = () => {
    if (!audioContextRef.current) return;

    if (audioContextRef.current.state === 'suspended') {
      audioContextRef.current.resume();
    }

    setIsPlaying(true);
    startTimeRef.current = audioContextRef.current.currentTime - pausedAtRef.current;

    // Start time update loop
    updateTime();
  };

  const pause = () => {
    setIsPlaying(false);
    if (audioContextRef.current) {
      pausedAtRef.current = audioContextRef.current.currentTime - startTimeRef.current;
    }
  };

  const updateTime = () => {
    if (!isPlaying || !audioContextRef.current) return;

    const elapsed = audioContextRef.current.currentTime - startTimeRef.current;
    setCurrentTime(Math.min(elapsed, duration));

    if (elapsed >= duration) {
      stop();
      return;
    }

    requestAnimationFrame(updateTime);
  };

  const seek = (time: number) => {
    pausedAtRef.current = time;
    setCurrentTime(time);

    if (isPlaying) {
      stop();
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
        <h3 className="text-xl font-bold">🎵 MIDI Preview</h3>
        {bpm && (
          <div className="text-sm text-gray-400">
            {bpm} BPM
          </div>
        )}
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
                {WAVEFORM_HEIGHTS.map((height: number, i: number) => {
                  const isActive = (currentTime / duration) * 50 > i;
                  return (
                    <div
                      key={i}
                      className={`flex-1 rounded-t transition-all ${
                        isActive
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
                className="absolute top-0 bottom-0 w-0.5 bg-white shadow-lg shadow-white/50"
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
          <div className="flex items-center justify-between gap-4">
            {/* Playback Controls */}
            <div className="flex items-center gap-3">
              {/* Stop */}
              <button
                onClick={stop}
                disabled={!isPlaying && currentTime === 0}
                className="p-3 bg-gray-800 hover:bg-gray-700 disabled:bg-gray-800 disabled:opacity-50 rounded-lg transition-all"
              >
                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                  <rect x="6" y="6" width="12" height="12" />
                </svg>
              </button>

              {/* Play/Pause */}
              <button
                onClick={isPlaying ? pause : play}
                className="p-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:shadow-lg hover:shadow-blue-500/50 rounded-lg transition-all"
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
                min="0"
                max="1"
                step="0.01"
                value={volume}
                onChange={(e) => setVolume(parseFloat(e.target.value))}
                className="flex-1 accent-blue-600"
              />
              <span className="text-xs text-gray-400 w-12 text-right">
                {Math.round(volume * 100)}%
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
          <div className="mt-4 p-3 bg-blue-900/20 border border-blue-500/30 rounded-lg">
            <p className="text-xs text-blue-300">
              💡 <strong>Note:</strong> This is a visual MIDI player. For audio playback, download the file and open it in your DAW or a MIDI player application.
            </p>
          </div>
        </>
      )}
    </div>
  );
}
