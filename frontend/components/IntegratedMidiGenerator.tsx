'use client';

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import MidiPlayerWithAudio from './MidiPlayerWithAudio';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const IntegratedMidiGenerator = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [styles, setStyles] = useState<string[]>(['lofi', 'house', 'cinematic', 'trap', 'dnb', 'modern_trap', 'liquid_dnb', 'deep_house', 'techno']);
  const [instruments, setInstruments] = useState<{ drums: string[], melodic: string[] }>({ drums: [], melodic: [] });
  const [presets, setPresets] = useState<any>({});

  // NEW: Generation Options Configuration
  const GENERATION_OPTIONS = {
    drums: {
      label: "Drums & Percussion",
      icon: "🥁",
      variants: [
        { id: "kick", label: "Kick Only (Techno/House)" },
        { id: "full_kit", label: "Full Drum Kit" },
        { id: "hat_pattern", label: "Hi-Hat Pattern" },
        { id: "perc", label: "Percussion Loop" }
      ]
    },
    bass: {
      label: "Bassline",
      icon: "🎸",
      variants: [
        { id: "sub_bass", label: "Sub Bass (808)" },
        { id: "acid_bass", label: "Acid / Synth Bass" },
        { id: "slap_bass", label: "Funky/Slap Bass" },
        { id: "simple_bass", label: "Simple Root Notes" }
      ]
    },
    melody: {
      label: "Melody & Chords",
      icon: "🎹",
      variants: [
        { id: "lead", label: "Lead Melody" },
        { id: "chords", label: "Chord Progression" },
        { id: "arp", label: "Arpeggio" },
        { id: "pad", label: "Atmospheric Pad" }
      ]
    }
  };

  const COMPLEXITY_LEVELS = [
    { id: "beginner", label: "Beginner", density: 0.3, complexity: 0.2 },
    { id: "intermediate", label: "Intermediate", density: 0.6, complexity: 0.5 },
    { id: "advanced", label: "Advanced", density: 0.8, complexity: 0.8 },
    { id: "expert", label: "expert", density: 0.9, complexity: 0.95 }
  ];

  const [params, setParams] = useState({
    description: "dark techno kick",
    style: "techno",
    category: "drums", // 'drums', 'bass', 'melody'
    instrument_variant: "kick", // Specific variant
    bpm: 130,
    bars: 4,
    use_dna: true,
    humanize: true,
    density: 0.7,
    complexity: 0.5,
    groove: 0.2,
    evolution: 0.3,
    velocity_curve: "natural",
    musical_key: "C",
    musical_scale: "minor"
  });

  // Load metadata on mount
  useEffect(() => {
    loadMetadata();
  }, []);

  const loadMetadata = async () => {
    try {
      const [stylesRes, instrumentsRes, presetsRes] = await Promise.all([
        axios.get(`${API_URL}/api/integrated-midi/styles`),
        axios.get(`${API_URL}/api/integrated-midi/instruments`),
        axios.get(`${API_URL}/api/integrated-midi/presets`)
      ]);

      setStyles(stylesRes.data.styles);
      setInstruments({
        drums: instrumentsRes.data.drum_instruments,
        melodic: instrumentsRes.data.melodic_instruments
      });
      setPresets(presetsRes.data.presets);
    } catch (error) {
      console.error('Failed to load metadata:', error);
    }
  };

  const handleComplexityChange = (levelId: string) => {
    const level = COMPLEXITY_LEVELS.find(l => l.id === levelId);
    if (level) {
      setParams(prev => ({
        ...prev,
        density: level.density,
        complexity: level.complexity
      }));
    }
  };

  const handleGenerate = async () => {
    setLoading(true);
    setResult(null);

    // Sync params
    const payload = getPayload();

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API_URL}/api/integrated-midi/generate`, payload, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      setResult(response.data);
    } catch (error: any) {
      console.error('Generation failed:', error);
      alert(error.response?.data?.detail || 'Failed to generate MIDI');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickGenerate = async () => {
    setLoading(true);
    setResult(null);

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(`${API_URL}/api/integrated-midi/quick-generate`, null, {
        params: {
          description: params.description,
          style: params.style
        },
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      setResult(response.data);
    } catch (error: any) {
      console.error('Quick generation failed:', error);
      alert(error.response?.data?.detail || 'Failed to generate MIDI');
    } finally {
      setLoading(false);
    }
  };

  const applyPreset = (presetName: string) => {
    const preset = presets[presetName];
    if (preset) {
      setParams(prev => ({
        ...prev,
        ...preset
      }));
    }
  };

  const handleDownload = () => {
    if (result?.download_url) {
      window.location.href = `${API_URL}${result.download_url}`;
    }
  };

  // Update params.instrument when category or variant changes
  useEffect(() => {
    // This maps the UI 'category/variant' to the backend 'instrument' parameter
    // Logic: backend expects a string like 'kick', 'bass', 'hat', etc.
    // We try to pass the variant ID, but fallback to category if needed.
    // Ideally backend handles these specific IDs.
  }, [params.category, params.instrument_variant]);

  // Wrapper to sync state before generate
  const getPayload = () => {
    return {
      ...params,
      instrument: params.instrument_variant // Map variant to instrument for backend
    };
  };

  // ... (update generate function to use getPayload) ...

  return (
    <div className="bg-gray-900 p-6 rounded-lg border border-gray-800 shadow-xl">
      <div className="mb-8 text-center">
        <h2 className="text-3xl font-bold bg-gradient-to-r from-purple-400 via-pink-500 to-red-500 text-transparent bg-clip-text mb-2 animate-gradient-x">
          🧬 GABRIEL Engine v2
        </h2>
        <p className="text-gray-400">Professional AI Music Analysis & Generation</p>
      </div>

      <div className="space-y-8">
        {/* Quick Generate Section */}
        <div className="bg-gray-800/50 backdrop-blur-sm p-6 rounded-xl border border-gray-700/50">
          <h3 className="text-lg font-semibold mb-3">⚡ Quick Generate</h3>
          <div className="flex gap-3">
            <input
              type="text"
              value={params.description}
              onChange={(e) => setParams({ ...params, description: e.target.value })}
              placeholder="Describe your pattern (e.g., 'dark techno kick')"
              className="flex-1 p-2 bg-gray-900 border border-gray-700 rounded focus:border-purple-500 focus:outline-none"
            />
            <select
              value={params.style}
              onChange={(e) => setParams({ ...params, style: e.target.value })}
              className="p-2 bg-gray-900 border border-gray-700 rounded focus:border-purple-500 focus:outline-none"
            >
              {styles.map(style => (
                <option key={style} value={style}>{style.toUpperCase()}</option>
              ))}
            </select>
            <button
              onClick={handleQuickGenerate}
              disabled={loading}
              className="px-6 py-2 bg-gradient-to-r from-purple-600 to-blue-600 hover:shadow-lg hover:shadow-purple-500/50 rounded font-semibold disabled:opacity-50 transition-all"
            >
              Generate
            </button>
          </div>
        </div>

        {/* 1. Category Selection */}
        <div className="grid grid-cols-3 gap-4">
          {Object.entries(GENERATION_OPTIONS).map(([key, option]) => (
            <button
              key={key}
              onClick={() => setParams({ ...params, category: key, instrument_variant: option.variants[0].id })}
              className={`p-4 rounded-xl border transition-all duration-300 flex flex-col items-center gap-2 ${params.category === key
                ? 'bg-purple-900/50 border-purple-500 shadow-lg shadow-purple-900/20'
                : 'bg-gray-800 border-gray-700 hover:border-gray-500 hover:bg-gray-750'
                }`}
            >
              <span className="text-3xl">{option.icon}</span>
              <span className="font-semibold text-gray-200">{option.label}</span>
            </button>
          ))}
        </div>

        {/* 2. Variant Selection */}
        <div className="bg-gray-800 p-4 rounded-xl border border-gray-700">
          <label className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-3 block">Sound Type</label>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {GENERATION_OPTIONS[params.category as keyof typeof GENERATION_OPTIONS].variants.map(variant => (
              <button
                key={variant.id}
                onClick={() => setParams({ ...params, instrument_variant: variant.id })}
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${params.instrument_variant === variant.id
                  ? 'bg-purple-600 text-white shadow-md'
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
              >
                {variant.label}
              </button>
            ))}
          </div>
        </div>

        {/* 3. Complexity Selector */}
        <div className="bg-gray-800 p-4 rounded-xl border border-gray-700">
          <label className="text-sm font-bold text-gray-400 uppercase tracking-wider mb-3 block">Complexity Level</label>
          <div className="flex justify-between items-center gap-2 bg-gray-900 p-1 rounded-lg relative">
            {COMPLEXITY_LEVELS.map((level) => {
              const isActive = Math.abs(params.density - level.density) < 0.1;
              return (
                <button
                  key={level.id}
                  onClick={() => handleComplexityChange(level.id)}
                  className={`flex-1 py-2 rounded-md text-sm transition-all z-10 ${isActive
                    ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-md'
                    : 'text-gray-400 hover:text-white'
                    }`}
                >
                  {level.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Advanced Parameters Details */}
        <details className="bg-gray-800 p-4 rounded-lg">
          <summary className="text-lg font-semibold cursor-pointer hover:text-purple-400 transition-colors">
            Advanced Parameters & DNA
          </summary>

          <div className="mt-4 space-y-4">
            {/* Presets */}
            <div>
              <label className="text-sm text-gray-400 mb-2 block">DNA Presets:</label>
              <div className="flex gap-2 flex-wrap">
                {Object.keys(presets).map(presetName => (
                  <button
                    key={presetName}
                    onClick={() => applyPreset(presetName)}
                    className="px-3 py-1 bg-gray-700 hover:bg-gray-600 rounded text-sm transition-colors"
                    title={presets[presetName]?.description}
                  >
                    {presetName}
                  </button>
                ))}
              </div>
            </div>

            {/* Basic Parameters */}
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="text-sm text-gray-400 mb-2 block">BPM: {params.bpm}</label>
                <input
                  type="range"
                  min="60"
                  max="200"
                  value={params.bpm}
                  onChange={(e) => setParams({ ...params, bpm: parseInt(e.target.value) })}
                  className="w-full accent-purple-600"
                />
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-2 block">Bars: {params.bars}</label>
                <input
                  type="range"
                  min="1"
                  max="16"
                  value={params.bars}
                  onChange={(e) => setParams({ ...params, bars: parseInt(e.target.value) })}
                  className="w-full accent-purple-600"
                />
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-2 block">Key:</label>
                <select
                  value={params.musical_key}
                  onChange={(e) => setParams({ ...params, musical_key: e.target.value })}
                  className="w-full p-2 bg-gray-900 border border-gray-700 rounded focus:border-purple-500 focus:outline-none"
                >
                  {['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'].map(key => (
                    <option key={key} value={key}>{key}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* DNA Parameters */}
            <div className="space-y-3">
              <h4 className="font-semibold text-purple-400">DNA Parameters</h4>

              <div>
                <label className="text-sm text-gray-400 mb-1 block">Density: {params.density.toFixed(2)}</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={params.density}
                  onChange={(e) => setParams({ ...params, density: parseFloat(e.target.value) })}
                  className="w-full accent-purple-600"
                />
                <small className="text-xs text-gray-500">How many notes (0 = sparse, 1 = dense)</small>
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-1 block">Complexity: {params.complexity.toFixed(2)}</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={params.complexity}
                  onChange={(e) => setParams({ ...params, complexity: parseFloat(e.target.value) })}
                  className="w-full accent-purple-600"
                />
                <small className="text-xs text-gray-500">Pattern variation (0 = simple, 1 = complex)</small>
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-1 block">Groove: {params.groove.toFixed(2)}</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={params.groove}
                  onChange={(e) => setParams({ ...params, groove: parseFloat(e.target.value) })}
                  className="w-full accent-purple-600"
                />
                <small className="text-xs text-gray-500">Swing amount (0 = straight, 1 = swung)</small>
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-1 block">Evolution: {params.evolution.toFixed(2)}</label>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={params.evolution}
                  onChange={(e) => setParams({ ...params, evolution: parseFloat(e.target.value) })}
                  className="w-full accent-purple-600"
                />
                <small className="text-xs text-gray-500">Pattern evolution (0 = static, 1 = evolving)</small>
              </div>
            </div>
          </div>
        </details>

        {/* Options */}
        <div className="flex justify-between bg-gray-800 p-4 rounded-xl border border-gray-700">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={params.use_dna}
              onChange={(e) => setParams({ ...params, use_dna: e.target.checked })}
              className="accent-purple-600 w-5 h-5"
            />
            <span className="font-medium">🧬 Use DNA Generation</span>
          </label>

          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={params.humanize}
              onChange={(e) => setParams({ ...params, humanize: e.target.checked })}
              className="accent-purple-600 w-5 h-5"
            />
            <span className="font-medium">🤖 Humanize</span>
          </label>
        </div>

        {/* Generate Button */}
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="w-full py-4 bg-gradient-to-r from-purple-600 to-blue-600 hover:shadow-lg hover:shadow-purple-500/50 rounded-xl font-bold text-xl disabled:opacity-50 transition-all transform hover:scale-[1.02]"
        >
          {loading ? '🎵 Generating Magic...' : '🎹 Generate MIDI Pattern'}
        </button>

        {/* Results with Player */}
        {result && (
          <div className="space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-4">
              <h3 className="text-lg font-bold text-green-400 mb-3 flex items-center gap-2">
                <span>✓</span> Generated: {result.metadata.description}
              </h3>
              <div className="flex flex-wrap gap-4 text-xs text-green-300/80">
                <span className="bg-green-900/40 px-2 py-1 rounded">{result.metadata.bpm} BPM</span>
                <span className="bg-green-900/40 px-2 py-1 rounded">{result.metadata.key} {result.metadata.scale}</span>
                <span className="bg-green-900/40 px-2 py-1 rounded">{result.metadata.bars} Bars</span>
              </div>
            </div>

            <MidiPlayerWithAudio
              midiUrl={`${API_URL}${result.download_url}`}
              bpm={result.metadata.bpm}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default IntegratedMidiGenerator;
