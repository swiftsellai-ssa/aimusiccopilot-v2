// frontend/components/PatternDNA.tsx
export function PatternDNAControls({ onChange }) {
  const [dna, setDna] = useState({
    density: 0.7,
    complexity: 0.5,
    groove: 0.2,
    evolution: 0.3
  });
  
  return (
    <div className="grid grid-cols-2 gap-4 p-4 bg-neutral-900 rounded-lg">
      <div>
        <label className="text-xs">Density</label>
        <input 
          type="range" 
          min="0" max="1" step="0.1"
          value={dna.density}
          onChange={(e) => {
            setDna({...dna, density: parseFloat(e.target.value)});
            onChange(dna);
          }}
          className="w-full"
        />
      </div>
      {/* Add other sliders */}
    </div>
  );
}