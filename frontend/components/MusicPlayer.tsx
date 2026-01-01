// frontend/components/MusicPlayer.tsx
import React, { useEffect, useRef, useState, useCallback } from 'react';
import * as Tone from 'tone';
import { Midi } from '@tonejs/midi';

interface MusicPlayerProps {
  midiUrl: string | null;
  bpm?: number;
  instrument?: string;
}

const MusicPlayer: React.FC<MusicPlayerProps> = ({ midiUrl, bpm = 120, instrument = 'full' }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);
  const [loadingProgress, setLoadingProgress] = useState(0);

  // Use refs for synths
  drums: Tone.MembraneSynth | null;
  bass: Tone.MonoSynth | null;
  lead: Tone.PolySynth | null;
}> ({
  drums: null,
  bass: null,
  lead: null
});

// Transport position ref
const transportRef = useRef<number>(0);

useEffect(() => {
  // Initialize synths with better sounds

  // Use MembraneSynth for drums (realistic drum sound without samples)
  synthsRef.current.drums = new Tone.MembraneSynth({
    pitchDecay: 0.05,
    octaves: 4,
    oscillator: { type: "sine" },
    envelope: {
      attack: 0.001,
      decay: 0.4,
      sustain: 0.01,
      release: 1.4,
    },
    volume: -6
  }).toDestination();

  // Bass synth
  synthsRef.current.bass = new Tone.MonoSynth({
    oscillator: { type: "sawtooth" },
    envelope: {
      attack: 0.01,
      decay: 0.1,
      sustain: 0.5,
      release: 0.5
    },
    filterEnvelope: {
      attack: 0.01,
      decay: 0.1,
      sustain: 0.5,
      release: 2,
      baseFrequency: 100,
      octaves: 2
    },
    volume: -10
  }).toDestination();

  // Lead/melody synth
  synthsRef.current.lead = new Tone.PolySynth(Tone.Synth, {
    oscillator: { type: "square" },
    envelope: {
      attack: 0.02,
      decay: 0.1,
      sustain: 0.3,
      release: 0.8
    },
    volume: -12
  }).toDestination();

  // Add reverb for atmosphere
  const reverb = new Tone.Reverb(1.5).toDestination();
  synthsRef.current.lead?.connect(reverb);

  return () => {
    // Cleanup
    Object.values(synthsRef.current).forEach(synth => synth?.dispose());
    Tone.Transport.stop();
    Tone.Transport.cancel();
  };
}, []);

const loadMidi = useCallback(async (url: string) => {
  setIsLoaded(false);
  setLoadingProgress(0);

  try {
    // Fetch and parse MIDI
    setLoadingProgress(25);
    const midi = await Midi.fromUrl(url);

    setLoadingProgress(50);

    // Clear previous transport
    Tone.Transport.stop();
    Tone.Transport.cancel();
    Tone.Transport.position = 0;

    // Set tempo
    const tempo = midi.header.tempos[0]?.bpm || bpm;
    Tone.Transport.bpm.value = tempo;

    setLoadingProgress(75);

    // Schedule all notes
    midi.tracks.forEach((track, trackIndex) => {
      track.notes.forEach((note) => {
        Tone.Transport.schedule((time) => {
          const velocity = note.velocity || 0.8;

          // Route to appropriate synth based on note range and track
          if (note.midi < 48 || track.channel === 9) {
            // Drums/percussion (MIDI channel 10 or low notes)
            if (synthsRef.current.drums) {
              const drumNote = note.midi === 36 ? "C1" :
                note.midi === 38 ? "D1" :
                  note.midi === 42 ? "F#1" : "C2";

              (synthsRef.current.drums as any).triggerAttackRelease(
                drumNote,
                "8n",
                time,
                velocity
              );
            }
          } else if (note.midi < 60) {
            // Bass range
            synthsRef.current.bass?.triggerAttackRelease(
              note.name,
              note.duration || "8n",
              time,
              velocity
            );
          } else {
            // Lead/melody
            synthsRef.current.lead?.triggerAttackRelease(
              note.name,
              note.duration || "4n",
              time,
              velocity * 0.7
            );
          }
        }, note.time);
      });
    });

    // Set loop points
    const duration = midi.duration || 4;
    Tone.Transport.loopEnd = `${Math.ceil(duration)}m`;
    Tone.Transport.loop = true;

    setLoadingProgress(100);
    setTimeout(() => setIsLoaded(true), 200);

  } catch (error) {
    console.error("Error loading MIDI:", error);
    setIsLoaded(false);
    setLoadingProgress(0);
  }
}, [bpm]);

useEffect(() => {
  if (midiUrl) {
    loadMidi(midiUrl);
  }
}, [midiUrl, loadMidi]);

const togglePlay = async () => {
  // Initialize audio context on user interaction
  if (Tone.context.state !== "running") {
    await Tone.start();
  }

  if (isPlaying) {
    Tone.Transport.pause();
    setIsPlaying(false);
  } else {
    Tone.Transport.start();
    setIsPlaying(true);
  }
};

const stopPlayback = () => {
  Tone.Transport.stop();
  Tone.Transport.position = 0;
  setIsPlaying(false);
};

return (
  <div className="p-6 mt-4 border border-neutral-800 rounded-xl bg-gradient-to-b from-neutral-900 to-black text-white">
    <div className="flex items-center justify-between mb-4">
      <h3 className="text-sm font-bold uppercase tracking-wider text-neutral-400">
        Audio Preview
      </h3>
      {isLoaded && (
        <span className="text-xs text-green-400 animate-pulse">
          ● Ready
        </span>
      )}
    </div>

    {!midiUrl ? (
      <p className="text-xs text-neutral-600 text-center py-4">
        Generate a track to preview...
      </p>
    ) : (
      <div className="space-y-4">
        {/* Loading bar */}
        {!isLoaded && loadingProgress > 0 && (
          <div className="w-full bg-neutral-800 rounded-full h-1">
            <div
              className="bg-gradient-to-r from-blue-500 to-purple-500 h-1 rounded-full transition-all duration-300"
              style={{ width: `${loadingProgress}%` }}
            />
          </div>
        )}

        {/* Control buttons */}
        <div className="flex gap-2 justify-center">
          <button
            onClick={togglePlay}
            disabled={!isLoaded}
            className={`px-8 py-3 rounded-full font-bold transition-all text-sm ${isLoaded
                ? isPlaying
                  ? 'bg-red-500 hover:bg-red-600 text-white shadow-[0_0_20px_rgba(239,68,68,0.5)]'
                  : 'bg-green-500 hover:bg-green-600 text-white shadow-[0_0_20px_rgba(34,197,94,0.5)]'
                : 'bg-neutral-800 text-neutral-500 cursor-not-allowed'
              }`}
          >
            {!isLoaded ? 'Loading...' : isPlaying ? '⏸ PAUSE' : '▶ PLAY'}
          </button>

          {isPlaying && (
            <button
              onClick={stopPlayback}
              className="px-6 py-3 rounded-full font-bold text-sm bg-neutral-800 hover:bg-neutral-700 transition-all"
            >
              ⏹ STOP
            </button>
          )}
        </div>

        {/* Instrument indicator */}
        <div className="text-center text-xs text-neutral-500">
          Playing: {instrument || 'Full arrangement'}
        </div>
      </div>
    )}
  </div>
);
};

export default MusicPlayer;