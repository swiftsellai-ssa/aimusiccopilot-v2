// frontend/components/MidiVisualDisplay.tsx

import { useEffect, useRef, useState } from 'react';
import { Midi } from '@tonejs/midi';

interface MidiVisualDisplayProps {
  midiUrl: string;
}

export default function MidiVisualDisplay({ midiUrl }: MidiVisualDisplayProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [noteCount, setNoteCount] = useState(0);

  useEffect(() => {
    if (!midiUrl) return;
    
    const loadAndDisplay = async () => {
      try {
        const midi = await Midi.fromUrl(midiUrl);
        const canvas = canvasRef.current;
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        if (!ctx) return;
        
        // Clear canvas
        ctx.fillStyle = '#0a0a0a';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Count total notes
        let totalNotes = 0;
        
        // Draw grid
        ctx.strokeStyle = '#1a1a1a';
        ctx.lineWidth = 1;
        for (let i = 0; i <= 16; i++) {
          const x = (canvas.width / 16) * i;
          ctx.beginPath();
          ctx.moveTo(x, 0);
          ctx.lineTo(x, canvas.height);
          ctx.stroke();
        }
        
        // Draw notes
        midi.tracks.forEach((track, trackIndex) => {
          track.notes.forEach((note) => {
            totalNotes++;
            
            // Calculate position
            const x = (note.time / (midi.duration || 4)) * canvas.width;
            const width = Math.max(2, (note.duration / (midi.duration || 4)) * canvas.width);
            const y = canvas.height - ((note.midi / 127) * canvas.height);
            const height = 4;
            
            // Choose color based on pitch
            const hue = (note.midi * 3) % 360;
            ctx.fillStyle = `hsla(${hue}, 70%, 50%, 0.8)`;
            
            // Draw note
            ctx.fillRect(x, y, width, height);
          });
        });
        
        setNoteCount(totalNotes);
        
      } catch (error) {
        console.error('Error loading MIDI for visualization:', error);
      }
    };
    
    loadAndDisplay();
  }, [midiUrl]);

  return (
    <div className="bg-gray-900 rounded-lg p-4">
      <div className="flex justify-between items-center mb-2">
        <h4 className="text-sm font-bold text-gray-400">MIDI Visualization</h4>
        <span className="text-xs text-gray-500">{noteCount} notes</span>
      </div>
      <canvas 
        ref={canvasRef}
        width={800}
        height={100}
        className="w-full h-24 bg-black rounded"
      />
    </div>
  );
}