
'use client';
import { useEffect, useRef, useState, useMemo, useCallback } from 'react';
import { Midi } from '@tonejs/midi';

interface VisualizerProps {
  midiUrl: string | null;
  instrument: string;
  height?: number;
  musicalKey?: string;
  musicalScale?: string;
}

// Helper: Note Name -> MIDI
const NOTE_TO_OFFSET: Record<string, number> = {
  'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
  'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
  'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
};

interface IntervalInfo {
  label: string;
  type: 'root' | 'stable' | 'color' | 'chromatic';
  color: string;
}

// Pitch Class Colors (Piano Keys)
const IS_BLACK_KEY = [false, true, false, true, false, false, true, false, true, false, true, false];

export default function MidiVisualizer({
  midiUrl,
  instrument,
  height = 300, // Container height
  musicalKey = 'C',
  musicalScale = 'minor'
}: VisualizerProps) {
  const [midiData, setMidiData] = useState<Midi | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);

  // Theory State
  const [showTheory, setShowTheory] = useState(false);
  const [hoveredNote, setHoveredNote] = useState<{ note: string; interval: string; color: string; x: number; y: number } | null>(null);

  // Animation Loop
  useEffect(() => {
    let animFrame: number;
    const animate = () => {
      // @ts-ignore
      const now = window.Tone?.Transport?.seconds || 0;
      setCurrentTime(now);
      animFrame = requestAnimationFrame(animate);
    };
    animate();
    return () => cancelAnimationFrame(animFrame);
  }, []);

  // 1. Logic: Interval Color
  const calculateInterval = useCallback((noteMidi: number): IntervalInfo => {
    const rootOffset = NOTE_TO_OFFSET[musicalKey] || 0;
    const pitchClass = noteMidi % 12;
    const rootClass = rootOffset % 12;
    const interval = (pitchClass - rootClass + 12) % 12;

    if (interval === 0) return { label: 'Root', type: 'root', color: '#06b6d4' }; // Cyan
    if (interval === 7) return { label: 'Perfect 5th', type: 'stable', color: '#3b82f6' }; // Blue
    if (interval === 4) return { label: 'Major 3rd', type: 'stable', color: '#a855f7' }; // Purple
    if (interval === 3) return { label: 'Minor 3rd', type: 'stable', color: '#a855f7' };
    if (interval === 10 || interval === 11) return { label: interval === 11 ? 'Major 7th' : 'Minor 7th', type: 'color', color: '#ec4899' }; // Pink
    if (interval === 2) return { label: 'Major 2nd (9th)', type: 'color', color: '#ec4899' };
    if (interval === 9) return { label: 'Major 6th (13th)', type: 'color', color: '#ec4899' };

    const map: Record<number, string> = { 1: 'm2', 5: 'P4', 6: 'Tritone', 8: 'm6' };
    return { label: map[interval] || '?', type: 'chromatic', color: '#4b5563' }; // Gray
  }, [musicalKey]);

  // Load MIDI
  useEffect(() => {
    if (!midiUrl) return;
    setIsLoading(true);
    Midi.fromUrl(midiUrl).then(m => {
      setMidiData(m);
      setIsLoading(false);
    });
  }, [midiUrl]);

  // 2. Compute Layout Data
  const layout = useMemo(() => {
    if (!midiData) return null;
    const track = midiData.tracks[0];
    if (!track) return null;

    // Pitch Range (Auto-Fit)
    let minPitch = 127, maxPitch = 0;
    track.notes.forEach(n => {
      minPitch = Math.min(minPitch, n.midi);
      maxPitch = Math.max(maxPitch, n.midi);
    });

    const PADDING_ROWS = 2; // Vertical breathing room
    const viewMin = Math.max(0, minPitch - PADDING_ROWS);
    const viewMax = Math.min(127, maxPitch + PADDING_ROWS);

    // Total rows to render
    const pitchRange = viewMax - viewMin + 1;

    const rowHeight = 20; // Fixed 20px per key
    const totalHeight = pitchRange * rowHeight;

    // Horizontal (Scroll)
    const bpm = midiData.header.tempos[0]?.bpm || 120;
    const secondsPerBar = (60 / bpm) * 4;
    const pixelsPerBar = 160;
    const pixelsPerSecond = pixelsPerBar / secondsPerBar;

    const duration = Math.max(midiData.duration, secondsPerBar * 4); // Min 4 bars
    const totalWidth = duration * pixelsPerSecond;

    return {
      track, duration,
      minMidi: viewMin, // standardized names for the rest of the component
      maxMidi: viewMax,
      pitchRange,
      pixelsPerSecond, totalWidth, totalHeight, rowHeight,
      bpm // <--- Export BPM
    };
  }, [midiData]); // Height prop handled in CSS container

  if (!midiUrl) return null;

  return (
    <div className="w-full mt-4 flex flex-col animate-in fade-in zoom-in duration-300 transform-gpu">

      {/* Header */}
      <div className="flex justify-between items-center mb-2 px-1">
        <div className="flex items-center gap-3">
          <span className="text-xs text-neutral-500 font-bold uppercase tracking-wider">
            Piano Roll
          </span>
          <button
            onClick={() => setShowTheory(!showTheory)}
            className={`text-[10px] px-2 py-0.5 rounded-full border transition-all ${showTheory
              ? 'bg-cyan-900/50 border-cyan-500 text-cyan-300 shadow-[0_0_10px_rgba(6,182,212,0.3)]'
              : 'bg-transparent border-neutral-700 text-neutral-500 hover:text-neutral-300'
              }`}
          >
            {showTheory ? 'Theory ON' : 'Show Theory'}
          </button>
        </div>
        {isLoading && <span className="text-xs text-blue-400 animate-pulse">Loading...</span>}
      </div>

      {/* Logic Container - fixed height with scroll */}
      <div
        className="flex bg-black border border-neutral-800 rounded-lg overflow-hidden shadow-inner"
        style={{ height: height }} // Container height (view port)
      >

        {/* LEFT: Piano Gutter  */}
        {/* We wrap everything in one scrollable container (except the header). 
              The Gutter needs to be sticky. 
          */}
        <div className="flex-1 overflow-auto custom-scrollbar relative flex">

          {layout && (
            <div className="flex relative" style={{ width: layout.totalWidth + 40, height: layout.totalHeight }}>

              {/* Sticky Piano Gutter */}
              <div className="sticky left-0 z-20 w-[40px] flex-shrink-0 bg-neutral-900 border-r border-neutral-800 h-full">
                <svg width="40" height={layout.totalHeight} preserveAspectRatio="none">
                  {Array.from({ length: layout.pitchRange }).map((_, i) => {
                    // i=0 is top (maxMidi) -> y=0
                    const currentMidi = layout.maxMidi - i;
                    const isBlack = IS_BLACK_KEY[currentMidi % 12];
                    const octave = Math.floor(currentMidi / 12) - 1;
                    const y = i * layout.rowHeight;

                    return (
                      <g key={currentMidi}>
                        <rect
                          x="0" y={y} width="40" height={layout.rowHeight}
                          fill={isBlack ? '#171717' : '#e5e5e5'}
                          stroke="#262626" strokeWidth="0.5"
                        />
                        {!isBlack && currentMidi % 12 === 0 && (
                          <text
                            x="34" y={y + layout.rowHeight - 5}
                            textAnchor="end" fill="#525252" fontSize="10" fontFamily="monospace" fontWeight="bold"
                          >
                            C{octave}
                          </text>
                        )}
                      </g>
                    );
                  })}
                </svg>
              </div>

              {/* Grid & Notes */}
              <div className="relative">
                <svg width={layout.totalWidth} height={layout.totalHeight} preserveAspectRatio="none">

                  {/* 1. Rows */}
                  {Array.from({ length: layout.pitchRange }).map((_, i) => {
                    const y = i * layout.rowHeight;
                    const currentMidi = layout.maxMidi - i;
                    const isBlack = IS_BLACK_KEY[currentMidi % 12];
                    return (
                      <line
                        key={`row-${i}`}
                        x1="0" y1={y} x2={layout.totalWidth} y2={y}
                        stroke={isBlack ? '#1f2937' : '#374151'} opacity={isBlack ? 0.3 : 0.1} strokeWidth="1"
                      />
                    );
                  })}

                  {/* 2. Beats */}
                  {(() => {
                    const bpm = layout.bpm; // <--- Use layout.bpm instead of midiData
                    const beatTime = 60 / bpm;
                    // Use layout.duration to cover full width
                    const totalBeats = Math.floor(layout.duration / beatTime);

                    return Array.from({ length: totalBeats + 1 }).map((_, i) => {
                      const x = i * beatTime * layout.pixelsPerSecond;
                      const isBar = i % 4 === 0;
                      return (
                        <line
                          key={`beat-${i}`}
                          x1={x} y1="0" x2={x} y2={layout.totalHeight}
                          stroke={isBar ? '#4b5563' : '#1f2937'}
                          strokeWidth={isBar ? 1 : 0.5}
                        />
                      );
                    });
                  })()}

                  {/* 3. Notes */}
                  {layout.track.notes.map((note, i) => {
                    const x = note.time * layout.pixelsPerSecond;
                    const w = note.duration * layout.pixelsPerSecond;

                    // Calc Y: Top (0) is maxMidi.
                    const rowIndex = layout.maxMidi - note.midi;
                    const y = rowIndex * layout.rowHeight;

                    // Color
                    const theory = calculateInterval(note.midi);
                    const isPlaying = currentTime >= note.time && currentTime < (note.time + note.duration);
                    const fill = isPlaying ? '#ffffff' : (showTheory ? theory.color : '#60a5fa');

                    return (
                      <rect
                        key={`note-${i}`}
                        x={x} y={y + 1} width={Math.max(w, 2)} height={layout.rowHeight - 2}
                        fill={fill} rx="2"
                        className="cursor-help transition-colors"
                        onMouseEnter={(e) => {
                          // Simple Tooltip Position: Just use the x/y in the SVG relative to the group
                          setHoveredNote({
                            note: note.name,
                            interval: theory.label,
                            color: theory.color,
                            x: x + w / 2,
                            y: y
                          });
                        }}
                      />
                    );
                  })}

                  {/* 4. Playhead */}
                  <line
                    x1={currentTime * layout.pixelsPerSecond} y1="0"
                    x2={currentTime * layout.pixelsPerSecond} y2={layout.totalHeight}
                    stroke="#facc15" strokeWidth="2"
                  />

                </svg>

                {/* Tooltip (Inside Relative Grid for scrolling) */}
                {showTheory && hoveredNote && (
                  <div
                    className="absolute pointer-events-none z-50 flex flex-col items-center"
                    style={{
                      left: hoveredNote.x,
                      top: hoveredNote.y - 12,
                      transform: 'translate(-50%, -100%)'
                    }}
                  >
                    <div className="bg-gray-900/95 backdrop-blur border border-gray-700 rounded-lg p-2 shadow-xl mb-1 text-center min-w-[100px]">
                      <div className="text-white font-bold text-sm">{hoveredNote.note}</div>
                      <div className="text-[10px] uppercase font-mono font-bold" style={{ color: hoveredNote.color }}>
                        {hoveredNote.interval}
                      </div>
                    </div>
                    <div className="w-0 h-0 border-l-[6px] border-l-transparent border-r-[6px] border-r-transparent border-t-[6px] border-t-gray-700"></div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}