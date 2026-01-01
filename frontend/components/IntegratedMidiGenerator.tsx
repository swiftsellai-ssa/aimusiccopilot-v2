'use client';

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import MidiPlayerWithAudio from './MidiPlayerWithAudio';

const IntegratedMidiGenerator = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [styles, setStyles] = useState<string[]>(['lofi', 'house', 'cinematic', 'trap', 'dnb', 'modern_trap', 'liquid_dnb', 'deep_house', 'techno']);
  const [instruments, setInstruments] = useState<{ drums: string[], melodic: string[] }>({ drums: [], melodic: [] });
  const [presets, setPresets] = useState<any>({});

  const [params, setParams] = useState({
    description: "dark techno kick",
    style: "techno",
    instrument: "kick",
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
        axios.get('http://localhost:8000/api/integrated-midi/styles'),
        axios.get('http://localhost:8000/api/integrated-midi/instruments'),
        axios.get('http://localhost:8000/api/integrated-midi/presets')
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

  const handleGenerate = async () => {
    setLoading(true);
    setResult(null);

    try {
      const token = localStorage.getItem('token');
      const response = await axios.post('http://localhost:8000/api/integrated-midi/generate', params, {
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
      const response = await axios.post('http://localhost:8000/api/integrated-midi/quick-generate', null, {
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
      // Download URL is now a static file path, no auth needed
      window.location.href = `http://localhost:8000${result.download_url}`;
    }
  };

  return (
    <div className="bg-gray-900 p-6 rounded-lg border border-gray-800">
      <div className="mb-6">
        <h2 className="text-2xl font-bold bg-gradient-to-r from-purple-400 to-blue-500 text-transparent bg-clip-text mb-2">
          🧬 GABRIEL Generator
        </h2>
        <p className="text-gray-400 text-sm">Advanced pattern generation with DNA-based algorithms</p>
      </div>

      <div className="space-y-6">
        {/* Quick Generate Section */}
        <div className="bg-gray-800 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-3">⚡ Quick Generate</h3>
          <div className="flex gap-3">
            <input
              type="text"
              value={params.description}
              onChange={(e) => setParams({ ...params, description: e.target.value })}
              placeholder="Describe your pattern..."
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
              ⚡ Generate
            </button>
          </div>
        </div>

        {/* Advanced Parameters */}
        <details className="bg-gray-800 p-4 rounded-lg">
          <summary className="text-lg font-semibold cursor-pointer hover:text-purple-400 transition-colors">
            Advanced Parameters
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
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-gray-400 mb-2 block">Instrument:</label>
                <select
                  value={params.instrument}
                  onChange={(e) => setParams({ ...params, instrument: e.target.value })}
                  className="w-full p-2 bg-gray-900 border border-gray-700 rounded focus:border-purple-500 focus:outline-none"
                >
                  <optgroup label="Drums">
                    {instruments.drums.map(inst => (
                      <option key={inst} value={inst}>{inst}</option>
                    ))}
                  </optgroup>
                  <optgroup label="Melodic">
                    {instruments.melodic.map(inst => (
                      <option key={inst} value={inst}>{inst}</option>
                    ))}
                  </optgroup>
                </select>
              </div>

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

            {/* Options */}
            <div className="space-y-2">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={params.use_dna}
                  onChange={(e) => setParams({ ...params, use_dna: e.target.checked })}
                  className="accent-purple-600"
                />
                <span className="text-sm">Use DNA Generation</span>
              </label>

              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={params.humanize}
                  onChange={(e) => setParams({ ...params, humanize: e.target.checked })}
                  className="accent-purple-600"
                />
                <span className="text-sm">Humanize</span>
              </label>
            </div>
          </div>
        </details>

        {/* Generate Button */}
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="w-full py-3 bg-gradient-to-r from-purple-600 to-blue-600 hover:shadow-lg hover:shadow-purple-500/50 rounded-lg font-bold disabled:opacity-50 transition-all"
        >
          {loading ? '🎵 Generating...' : '🎹 Generate MIDI'}
        </button>

        {/* Results with Player */}
        {result && (
          <div className="space-y-4">
            <div className="bg-green-900/20 border border-green-500/30 rounded-lg p-4">
              <h3 className="text-lg font-bold text-green-400 mb-3">✓ Generated Successfully!</h3>

              <div className="grid grid-cols-2 gap-2 text-sm">
                <div><strong>Style:</strong> {result.metadata.style}</div>
                <div><strong>Instrument:</strong> {result.metadata.instrument}</div>
                <div><strong>BPM:</strong> {result.metadata.bpm}</div>
                <div><strong>Bars:</strong> {result.metadata.bars}</div>
                <div><strong>Key:</strong> {result.metadata.key} {result.metadata.scale}</div>
                <div><strong>Tracks:</strong> {result.metadata.tracks}</div>
              </div>
            </div>

            {/* MIDI Player with Real Audio */}
            <MidiPlayerWithAudio
              midiUrl={`http://localhost:8000${result.download_url}`}
              bpm={result.metadata.bpm}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default IntegratedMidiGenerator;
