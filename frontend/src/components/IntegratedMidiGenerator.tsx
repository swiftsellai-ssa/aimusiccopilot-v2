'use client';

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './IntegratedMidiGenerator.css';
import MidiPlayer from './MidiPlayer';

const IntegratedMidiGenerator = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [styles, setStyles] = useState<string[]>([]);
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
        axios.get('/api/integrated-midi/styles'),
        axios.get('/api/integrated-midi/instruments'),
        axios.get('/api/integrated-midi/presets')
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
      const response = await axios.post('/api/integrated-midi/generate', params, {
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
      const response = await axios.post('/api/integrated-midi/quick-generate', null, {
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
      const token = localStorage.getItem('token');
      window.location.href = `${result.download_url}?token=${token}`;
    }
  };

  return (
    <div className="integrated-midi-generator">
      <div className="generator-header">
        <h2>🎵 Integrated MIDI Generator</h2>
        <p>Advanced pattern generation with DNA-based algorithms</p>
      </div>

      <div className="generator-content">
        {/* Quick Generate Section */}
        <div className="quick-section">
          <h3>Quick Generate</h3>
          <div className="form-row">
            <input
              type="text"
              value={params.description}
              onChange={(e) => setParams({...params, description: e.target.value})}
              placeholder="Describe your pattern..."
              className="description-input"
            />
            <select
              value={params.style}
              onChange={(e) => setParams({...params, style: e.target.value})}
              className="style-select"
            >
              {styles.map(style => (
                <option key={style} value={style}>{style.toUpperCase()}</option>
              ))}
            </select>
            <button
              onClick={handleQuickGenerate}
              disabled={loading}
              className="btn btn-quick"
            >
              ⚡ Quick Generate
            </button>
          </div>
        </div>

        {/* Advanced Parameters */}
        <details className="advanced-section">
          <summary>Advanced Parameters</summary>

          {/* Presets */}
          <div className="presets-section">
            <label>DNA Presets:</label>
            <div className="preset-buttons">
              {Object.keys(presets).map(presetName => (
                <button
                  key={presetName}
                  onClick={() => applyPreset(presetName)}
                  className="btn btn-preset"
                  title={presets[presetName]?.description}
                >
                  {presetName}
                </button>
              ))}
            </div>
          </div>

          {/* Basic Parameters */}
          <div className="param-group">
            <h4>Basic Parameters</h4>

            <div className="form-group">
              <label>Instrument:</label>
              <select
                value={params.instrument}
                onChange={(e) => setParams({...params, instrument: e.target.value})}
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

            <div className="form-group">
              <label>BPM: {params.bpm}</label>
              <input
                type="range"
                min="60"
                max="200"
                value={params.bpm}
                onChange={(e) => setParams({...params, bpm: parseInt(e.target.value)})}
              />
            </div>

            <div className="form-group">
              <label>Bars: {params.bars}</label>
              <input
                type="range"
                min="1"
                max="16"
                value={params.bars}
                onChange={(e) => setParams({...params, bars: parseInt(e.target.value)})}
              />
            </div>

            <div className="form-group">
              <label>Key:</label>
              <select
                value={params.musical_key}
                onChange={(e) => setParams({...params, musical_key: e.target.value})}
              >
                {['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'].map(key => (
                  <option key={key} value={key}>{key}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label>Scale:</label>
              <select
                value={params.musical_scale}
                onChange={(e) => setParams({...params, musical_scale: e.target.value})}
              >
                <option value="major">Major</option>
                <option value="minor">Minor</option>
                <option value="dorian">Dorian</option>
                <option value="phrygian">Phrygian</option>
              </select>
            </div>
          </div>

          {/* DNA Parameters */}
          <div className="param-group">
            <h4>DNA Parameters</h4>

            <div className="form-group">
              <label>Density: {params.density.toFixed(2)}</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={params.density}
                onChange={(e) => setParams({...params, density: parseFloat(e.target.value)})}
              />
              <small>How many notes (0 = sparse, 1 = dense)</small>
            </div>

            <div className="form-group">
              <label>Complexity: {params.complexity.toFixed(2)}</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={params.complexity}
                onChange={(e) => setParams({...params, complexity: parseFloat(e.target.value)})}
              />
              <small>Pattern variation (0 = simple, 1 = complex)</small>
            </div>

            <div className="form-group">
              <label>Groove: {params.groove.toFixed(2)}</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={params.groove}
                onChange={(e) => setParams({...params, groove: parseFloat(e.target.value)})}
              />
              <small>Swing amount (0 = straight, 1 = swung)</small>
            </div>

            <div className="form-group">
              <label>Evolution: {params.evolution.toFixed(2)}</label>
              <input
                type="range"
                min="0"
                max="1"
                step="0.05"
                value={params.evolution}
                onChange={(e) => setParams({...params, evolution: parseFloat(e.target.value)})}
              />
              <small>Pattern evolution (0 = static, 1 = evolving)</small>
            </div>

            <div className="form-group">
              <label>Velocity Curve:</label>
              <select
                value={params.velocity_curve}
                onChange={(e) => setParams({...params, velocity_curve: e.target.value})}
              >
                <option value="natural">Natural</option>
                <option value="accent">Accent</option>
                <option value="exponential">Exponential</option>
                <option value="random">Random</option>
              </select>
            </div>
          </div>

          {/* Options */}
          <div className="param-group">
            <h4>Options</h4>

            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={params.use_dna}
                  onChange={(e) => setParams({...params, use_dna: e.target.checked})}
                />
                Use DNA Generation
              </label>
              <small>Enable advanced pattern DNA (recommended)</small>
            </div>

            <div className="form-group checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={params.humanize}
                  onChange={(e) => setParams({...params, humanize: e.target.checked})}
                />
                Humanize
              </label>
              <small>Add natural timing variations</small>
            </div>
          </div>
        </details>

        {/* Generate Button */}
        <div className="generate-section">
          <button
            onClick={handleGenerate}
            disabled={loading}
            className="btn btn-generate"
          >
            {loading ? '🎵 Generating...' : '🎹 Generate MIDI'}
          </button>
        </div>

        {/* Results with Player */}
        {result && (
          <div className="result-section">
            <h3>✓ Generated Successfully!</h3>

            {/* Metadata */}
            <div className="result-details">
              <p><strong>Description:</strong> {result.metadata.description}</p>
              <p><strong>Style:</strong> {result.metadata.style}</p>
              <p><strong>Instrument:</strong> {result.metadata.instrument}</p>
              <p><strong>BPM:</strong> {result.metadata.bpm}</p>
              <p><strong>Bars:</strong> {result.metadata.bars}</p>
              <p><strong>Key:</strong> {result.metadata.key} {result.metadata.scale}</p>
              <p><strong>Tracks:</strong> {result.metadata.tracks}</p>
              <p><strong>DNA:</strong> {result.metadata.used_dna ? 'Yes' : 'No'}</p>
              <p><strong>Humanized:</strong> {result.metadata.humanized ? 'Yes' : 'No'}</p>
            </div>

            {/* MIDI Player */}
            <div className="mt-4">
              <MidiPlayer
                midiUrl={result.download_url}
                bpm={result.metadata.bpm}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default IntegratedMidiGenerator;
