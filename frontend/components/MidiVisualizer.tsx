// frontend/components/MidiVisualizer.tsx
'use client';
import { useEffect, useRef, useState, useCallback } from 'react';
import { Midi } from '@tonejs/midi';

interface VisualizerProps {
  midiUrl: string | null;
  instrument: string;
  height?: number;
}

export default function MidiVisualizer({ midiUrl, instrument, height = 120 }: VisualizerProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number | null>(null);
  const [midiData, setMidiData] = useState<Midi | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Color scheme based on instrument
  const getColorScheme = useCallback(() => {
    const schemes = {
      kick: { primary: '#f97316', glow: '#fb923c', bg: '#7c2d12' },
      bass: { primary: '#a855f7', glow: '#c084fc', bg: '#581c87' },
      melody: { primary: '#ec4899', glow: '#f9a8d4', bg: '#831843' },
      drums: { primary: '#60a5fa', glow: '#93c5fd', bg: '#1e3a8a' },
      hat: { primary: '#10b981', glow: '#34d399', bg: '#064e3b' },
      default: { primary: '#60a5fa', glow: '#93c5fd', bg: '#1e3a8a' }
    };

    return schemes[instrument as keyof typeof schemes] || schemes.default;
  }, [instrument]);

  // Load MIDI data
  useEffect(() => {
    if (!midiUrl) return;

    const loadMidi = async () => {
      setIsLoading(true);
      try {
        const midi = await Midi.fromUrl(midiUrl);
        setMidiData(midi);
      } catch (error) {
        console.error('Failed to load MIDI:', error);
      } finally {
        setIsLoading(false);
      }
    };

    loadMidi();
  }, [midiUrl]);

  // Draw visualization
  const draw = useCallback(() => {
    if (!midiData || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const width = canvas.width;
    const height = canvas.height;
    const colors = getColorScheme();

    // Clear canvas
    ctx.fillStyle = '#0a0a0a';
    ctx.fillRect(0, 0, width, height);

    // Draw grid
    ctx.strokeStyle = '#262626';
    ctx.lineWidth = 0.5;

    // Vertical lines (bars)
    for (let i = 0; i <= 4; i++) {
      const x = (width / 4) * i;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }

    // Horizontal lines (octaves)
    for (let i = 0; i <= 4; i++) {
      const y = (height / 4) * i;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
    }

    // Get all notes
    const allNotes = midiData.tracks.flatMap(t => t.notes);
    if (allNotes.length === 0) return;

    // Find note range
    let minNote = Math.min(...allNotes.map(n => n.midi));
    let maxNote = Math.max(...allNotes.map(n => n.midi));

    // Add padding
    minNote = Math.max(0, minNote - 2);
    maxNote = Math.min(127, maxNote + 2);
    const noteRange = maxNote - minNote || 1;

    const duration = midiData.duration || 4;

    // Draw notes with glow effect
    allNotes.forEach(note => {
      const x = (note.time / duration) * width;
      const w = Math.max(2, (note.duration / duration) * width);
      const normalizedPitch = (note.midi - minNote) / noteRange;
      const y = height - (normalizedPitch * height) - 5;
      const h = 4;

      // Draw glow
      ctx.shadowBlur = 8;
      ctx.shadowColor = colors.glow;

      // Draw note rectangle with gradient
      const gradient = ctx.createLinearGradient(x, y, x + w, y);
      gradient.addColorStop(0, colors.primary);
      gradient.addColorStop(0.5, colors.glow);
      gradient.addColorStop(1, colors.primary);

      ctx.fillStyle = gradient;
      ctx.fillRect(x, y, w, h);

      // Draw velocity indicator
      const velocityAlpha = note.velocity || 0.8;
      ctx.fillStyle = `${colors.glow}${Math.floor(velocityAlpha * 255).toString(16).padStart(2, '0')}`;
      ctx.fillRect(x, y - 1, w, 1);

      ctx.shadowBlur = 0;
    });

    // Draw playhead animation
    const currentTime = (Date.now() % 4000) / 4000; // Loop every 4 seconds
    const playheadX = currentTime * width;

    ctx.strokeStyle = '#ffffff30';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(playheadX, 0);
    ctx.lineTo(playheadX, height);
    ctx.stroke();

  }, [midiData, getColorScheme]);

  // Animation loop
  useEffect(() => {
    if (!midiData) return;

    const animate = () => {
      draw();
      animationRef.current = requestAnimationFrame(animate);
    };

    animate();

    return () => {
      if (animationRef.current !== null) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [midiData, draw]);

  if (!midiUrl) return null;

  return (
    <div className="w-full mt-4 animate-in fade-in zoom-in duration-300">
      <div className="flex justify-between items-center mb-2">
        <span className="text-xs text-neutral-500 font-bold uppercase tracking-wider">
          Piano Roll
        </span>
        {isLoading && (
          <span className="text-xs text-blue-400 animate-pulse">Loading...</span>
        )}
        {!isLoading && midiData && (
          <span className="text-xs text-neutral-500">
            {midiData.tracks.flatMap(t => t.notes).length} notes
          </span>
        )}
      </div>

      <div className="relative rounded-lg overflow-hidden border border-neutral-800 bg-black shadow-inner">
        <canvas
          ref={canvasRef}
          width={800}
          height={height}
          className="w-full"
          style={{ height: `${height}px` }}
        />

        {/* Overlay gradient for depth */}
        <div className="absolute inset-0 pointer-events-none bg-gradient-to-t from-black/50 to-transparent" />
      </div>
    </div>
  );
}