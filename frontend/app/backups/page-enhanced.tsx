// frontend/app/page.tsx - ENHANCED VERSION WITH PATTERN GENERATOR
// This combines your existing complete track generator with the new DNA pattern generator

'use client';
import { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-hot-toast';
import IntegratedMidiGenerator from '@/components/IntegratedMidiGenerator';
import MidiPlayer from '@/components/MidiPlayer';

export default function Home() {
  // State management
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(false);
  const [description, setDescription] = useState('');
  const [selectedInstrument, setSelectedInstrument] = useState('drums');
  const [selectedKey, setSelectedKey] = useState('C');
  const [selectedScale, setSelectedScale] = useState('minor');
  const [bpm, setBpm] = useState(128);
  const [currentMidiUrl, setCurrentMidiUrl] = useState('');
  const [recommendations, setRecommendations] = useState([]);

  // New: Tab state for switching between generators
  const [activeTab, setActiveTab] = useState<'complete' | 'pattern'>('complete');

  // Check authentication on load
  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsAuthenticated(!!token);
  }, []);

  // Main generation function (your existing)
  const generateMIDI = async () => {
    if (!description) {
      toast.error('Please describe what you want to generate');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');

      // Call your actual backend endpoint
      const response = await axios.post(
        'http://localhost:8000/api/generate',
        {
          description: description,
          instrument: selectedInstrument,
          musical_key: selectedKey,
          musical_scale: selectedScale,
          bpm: bpm
        },
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      // Get the file URL from response
      if (response.data.file_url) {
        setCurrentMidiUrl(`http://localhost:8000${response.data.file_url}`);
        toast.success('MIDI generated successfully!');

        // Get recommendations
        if (response.data.suggestions) {
          setRecommendations(response.data.suggestions);
        }
      }

    } catch (error) {
      console.error('Generation failed:', error);
      toast.error('Failed to generate MIDI. Check backend connection.');
    } finally {
      setLoading(false);
    }
  };

  // Download function
  const downloadProject = async () => {
    if (!currentMidiUrl) {
      toast.error('Generate a track first');
      return;
    }

    try {
      const token = localStorage.getItem('token');

      const response = await axios.post(
        'http://localhost:8000/api/download/package',
        {
          project_name: description || 'AI Generated',
          bpm: bpm,
          style: selectedInstrument,
          metadata: {
            key: selectedKey,
            scale: selectedScale
          }
        },
        {
          responseType: 'blob',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      // Create download link
      const url = window.URL.createObjectURL(response.data);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${selectedInstrument}_${bpm}bpm.zip`;
      a.click();

      toast.success('Project downloaded!');
    } catch (error) {
      toast.error('Download failed');
    }
  };

  // Simple login for testing
  const quickLogin = async () => {
    try {
      const formData = new URLSearchParams();
      formData.append('username', 'test@test.com');
      formData.append('password', 'testpass');

      const response = await axios.post(
        'http://localhost:8000/token',
        formData
      );

      localStorage.setItem('token', response.data.access_token);
      setIsAuthenticated(true);
      toast.success('Logged in!');
    } catch (error) {
      toast.error('Login failed - check backend');
    }
  };

  return (
    <div className="min-h-screen bg-black text-white p-8">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 text-transparent bg-clip-text mb-2">
          AIMusicCopilot
        </h1>
        <p className="text-gray-400">AI-Powered Music Generation Platform</p>
      </div>

      {/* Auth Check */}
      {!isAuthenticated && (
        <div className="max-w-2xl mx-auto mb-8">
          <button
            onClick={quickLogin}
            className="w-full py-3 bg-red-600 hover:bg-red-700 rounded-lg"
          >
            Login First (Click for Test Account)
          </button>
        </div>
      )}

      {isAuthenticated && (
        <>
          {/* Tab Navigation */}
          <div className="max-w-4xl mx-auto mb-6">
            <div className="flex gap-4 bg-gray-900 p-2 rounded-lg">
              <button
                onClick={() => setActiveTab('complete')}
                className={`flex-1 py-3 px-6 rounded-lg font-semibold transition-all ${
                  activeTab === 'complete'
                    ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg shadow-blue-500/50'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white'
                }`}
              >
                🎼 Complete Track Generator
              </button>
              <button
                onClick={() => setActiveTab('pattern')}
                className={`flex-1 py-3 px-6 rounded-lg font-semibold transition-all ${
                  activeTab === 'pattern'
                    ? 'bg-gradient-to-r from-purple-600 to-purple-700 text-white shadow-lg shadow-purple-500/50'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-white'
                }`}
              >
                🧬 DNA Pattern Generator
              </button>
            </div>

            {/* Info Banner */}
            <div className="mt-4 p-4 bg-gray-900/50 border border-gray-800 rounded-lg">
              <div className="flex items-start gap-3">
                <div className="text-2xl">
                  {activeTab === 'complete' ? '🎵' : '🧬'}
                </div>
                <div>
                  <h3 className="font-semibold mb-1">
                    {activeTab === 'complete'
                      ? 'Complete Track Generation'
                      : 'Individual Pattern Generation'
                    }
                  </h3>
                  <p className="text-sm text-gray-400">
                    {activeTab === 'complete'
                      ? 'Generate full multi-track compositions with AI-powered arrangements and recommendations.'
                      : 'Create individual MIDI patterns (kicks, hats, bass, etc.) with advanced DNA parameters for precise control.'
                    }
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Content Area */}
          {activeTab === 'complete' ? (
            // YOUR EXISTING COMPLETE TRACK GENERATOR
            <div className="max-w-4xl mx-auto space-y-6">
              {/* Generation Controls */}
              <div className="bg-gray-900 p-6 rounded-lg border border-gray-800">
                <h2 className="text-xl font-bold mb-4">Generate Music</h2>

                {/* Instrument Selection */}
                <div className="grid grid-cols-4 gap-2 mb-4">
                  {['drums', 'bass', 'melody', 'full'].map(inst => (
                    <button
                      key={inst}
                      onClick={() => setSelectedInstrument(inst)}
                      className={`py-2 px-4 rounded transition-all ${
                        selectedInstrument === inst
                          ? 'bg-blue-600 shadow-lg shadow-blue-500/50'
                          : 'bg-gray-800 hover:bg-gray-700'
                      }`}
                    >
                      {inst.charAt(0).toUpperCase() + inst.slice(1)}
                    </button>
                  ))}
                </div>

                {/* Key and Scale */}
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <label className="text-sm text-gray-400 mb-2 block">Key</label>
                    <select
                      value={selectedKey}
                      onChange={(e) => setSelectedKey(e.target.value)}
                      className="w-full p-2 bg-gray-800 border border-gray-700 rounded focus:border-blue-500 focus:outline-none"
                    >
                      {['C', 'D', 'E', 'F', 'G', 'A', 'B', 'F#', 'Bb'].map(key => (
                        <option key={key} value={key}>{key}</option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="text-sm text-gray-400 mb-2 block">Scale</label>
                    <select
                      value={selectedScale}
                      onChange={(e) => setSelectedScale(e.target.value)}
                      className="w-full p-2 bg-gray-800 border border-gray-700 rounded focus:border-blue-500 focus:outline-none"
                    >
                      {['major', 'minor', 'phrygian', 'dorian'].map(scale => (
                        <option key={scale} value={scale}>
                          {scale.charAt(0).toUpperCase() + scale.slice(1)}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* BPM Control */}
                <div className="mb-4">
                  <label className="text-sm text-gray-400 mb-2 block">BPM: {bpm}</label>
                  <input
                    type="range"
                    min="60"
                    max="180"
                    value={bpm}
                    onChange={(e) => setBpm(parseInt(e.target.value))}
                    className="w-full accent-blue-600"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>60</span>
                    <span>180</span>
                  </div>
                </div>

                {/* Description */}
                <div className="mb-4">
                  <label className="text-sm text-gray-400 mb-2 block">Description</label>
                  <textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Ex: A fast and aggressive techno rumble..."
                    className="w-full p-3 bg-gray-800 border border-gray-700 rounded focus:border-blue-500 focus:outline-none"
                    rows={3}
                  />
                </div>

                {/* Generate Button */}
                <button
                  onClick={generateMIDI}
                  disabled={loading}
                  className={`w-full py-3 rounded-lg font-bold transition-all ${
                    loading
                      ? 'bg-gray-600 cursor-not-allowed'
                      : 'bg-gradient-to-r from-blue-600 to-blue-700 hover:shadow-lg hover:shadow-blue-500/50'
                  }`}
                >
                  {loading ? 'Generating...' : 'Generate MIDI 🎵'}
                </button>
              </div>

              {/* Audio Preview with Working Player */}
              {currentMidiUrl && (
                <MidiPlayer
                  midiUrl={currentMidiUrl}
                  bpm={bpm}
                />
              )}

              {/* Export Section */}
              {currentMidiUrl && (
                <div className="bg-gray-900 p-6 rounded-lg border border-gray-800">
                  <h3 className="text-xl font-bold mb-4">Export Project</h3>

                  <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                    <div className="bg-gray-800 p-3 rounded">
                      <span className="text-gray-400">Style:</span>
                      <p className="font-bold">{selectedInstrument}</p>
                    </div>
                    <div className="bg-gray-800 p-3 rounded">
                      <span className="text-gray-400">Tempo:</span>
                      <p className="font-bold">{bpm} BPM</p>
                    </div>
                    <div className="bg-gray-800 p-3 rounded">
                      <span className="text-gray-400">Key:</span>
                      <p className="font-bold">{selectedKey} {selectedScale}</p>
                    </div>
                    <div className="bg-gray-800 p-3 rounded">
                      <span className="text-gray-400">Type:</span>
                      <p className="font-bold">Full Project</p>
                    </div>
                  </div>

                  <button
                    onClick={downloadProject}
                    className="w-full py-3 bg-gradient-to-r from-green-600 to-green-700 hover:shadow-lg hover:shadow-green-500/50 rounded-lg font-bold transition-all"
                  >
                    📦 Download Project Pack
                  </button>

                  <div className="mt-3 text-xs text-gray-500 space-y-1">
                    <p>✓ MIDI files for all tracks</p>
                    <p>✓ Project structure & README</p>
                    <p>✓ Ready for Ableton Live 11/12</p>
                  </div>
                </div>
              )}

              {/* Recommendations */}
              {recommendations.length > 0 && (
                <div className="bg-gray-900 p-6 rounded-lg border border-gray-800">
                  <h3 className="text-xl font-bold mb-4">AI Recommendations</h3>
                  <div className="grid grid-cols-2 gap-4">
                    {recommendations.map((rec, idx) => (
                      <button
                        key={idx}
                        onClick={() => {
                          setDescription(rec.prompt);
                          toast('Recommendation loaded! Click Generate to create.');
                        }}
                        className="p-4 bg-gray-800 hover:bg-gray-700 rounded-lg text-left transition-all border border-gray-700 hover:border-blue-500"
                      >
                        <h4 className="font-bold mb-1">{rec.title}</h4>
                        <p className="text-sm text-gray-400">{rec.description}</p>
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            // NEW DNA PATTERN GENERATOR
            <div className="max-w-4xl mx-auto">
              <IntegratedMidiGenerator />
            </div>
          )}
        </>
      )}

      {/* Footer Info */}
      {isAuthenticated && (
        <div className="max-w-4xl mx-auto mt-12 p-6 bg-gray-900/50 border border-gray-800 rounded-lg">
          <h3 className="font-semibold mb-3 text-center">💡 Quick Guide</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <h4 className="font-semibold text-blue-400 mb-2">Complete Track Generator</h4>
              <ul className="space-y-1 text-gray-400">
                <li>• Generate full multi-track compositions</li>
                <li>• AI-powered arrangements</li>
                <li>• Get recommendations</li>
                <li>• Export as project pack</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold text-purple-400 mb-2">DNA Pattern Generator</h4>
              <ul className="space-y-1 text-gray-400">
                <li>• Individual instrument patterns</li>
                <li>• Advanced DNA parameters</li>
                <li>• Humanization engine</li>
                <li>• Multiple style support</li>
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
