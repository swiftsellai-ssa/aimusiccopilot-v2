// frontend/components/PatternDNA.tsx
import React, { useState } from 'react';

interface DNA {
  density: number;
  complexity: number;
  groove: number;
  evolution: number;
}

interface PatternDNAControlsProps {
  onChange: (dna: DNA) => void;
}

export function PatternDNAControls({ onChange }: PatternDNAControlsProps) {
  const [dna, setDna] = useState<DNA>({
    density: 0.7,
    complexity: 0.5,
    groove: 0.2,
    evolution: 0.3
  });

  const updateDna = (key: keyof DNA, value: number) => {
    const newDna = { ...dna, [key]: value };
    setDna(newDna);
    onChange(newDna);
  };

  return (
    <div className="grid grid-cols-2 gap-4 p-4 bg-neutral-900 rounded-lg">
      <div className="space-y-1">
        <label className="text-xs text-gray-400">Density</label>
        <input
          type="range"
          min="0" max="1" step="0.1"
          value={dna.density}
          onChange={(e) => updateDna('density', parseFloat(e.target.value))}
          className="w-full h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer"
        />
        <div className="text-right text-xs text-gray-500">{dna.density}</div>
      </div>

      <div className="space-y-1">
        <label className="text-xs text-gray-400">Complexity</label>
        <input
          type="range"
          min="0" max="1" step="0.1"
          value={dna.complexity}
          onChange={(e) => updateDna('complexity', parseFloat(e.target.value))}
          className="w-full h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer"
        />
        <div className="text-right text-xs text-gray-500">{dna.complexity}</div>
      </div>

      <div className="space-y-1">
        <label className="text-xs text-gray-400">Groove</label>
        <input
          type="range"
          min="0" max="1" step="0.1"
          value={dna.groove}
          onChange={(e) => updateDna('groove', parseFloat(e.target.value))}
          className="w-full h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer"
        />
        <div className="text-right text-xs text-gray-500">{dna.groove}</div>
      </div>

      <div className="space-y-1">
        <label className="text-xs text-gray-400">Evolution</label>
        <input
          type="range"
          min="0" max="1" step="0.1"
          value={dna.evolution}
          onChange={(e) => updateDna('evolution', parseFloat(e.target.value))}
          className="w-full h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer"
        />
        <div className="text-right text-xs text-gray-500">{dna.evolution}</div>
      </div>
    </div>
  );
}