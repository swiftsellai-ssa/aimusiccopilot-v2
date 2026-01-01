// frontend/app/page-unified.tsx - UNIFIED MUSIC GENERATOR
// Clean, simple interface with Simple and Advanced (DNA) modes

'use client';
import { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-hot-toast';
import MidiPlayerWithAudio from '@/components/MidiPlayerWithAudio';

export default function UnifiedMusicGenerator() {
  // Auth state
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isRegistering, setIsRegistering] = useState(false);
  const [authForm, setAuthForm] = useState({ email: '', password: '' });

  // Generator state
  const [mode, setMode] = useState<'simple' | 'advanced'>('simple');
  const [generationType, setGenerationType] = useState<'drums' | 'bass' | 'melody' | 'full'>('drums');
  const [loading, setLoading] = useState(false);
  const [currentMidiUrl, setCurrentMidiUrl] = useState('');
  const [currentBpm, setCurrentBpm] = useState(128);

  // Simple mode params
  const [description, setDescription] = useState('');
  const [style, setStyle] = useState('techno');
  const [bpm, setBpm] = useState(128);
  const [musicalKey, setMusicalKey] = useState('C');
  const [musicalScale, setMusicalScale] = useState('minor');

  // Advanced DNA params
  const [dnaParams, setDnaParams] = useState({
    density: 0.7,
    complexity: 0.5,
    groove: 0.2,
    evolution: 0.3,
    bars: 4
  });

  // Check auth on load
  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsAuthenticated(!!token);
  }, []);

  // Auth handlers
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const formData = new URLSearchParams();
      formData.append('username', authForm.email);
      formData.append('password', authForm.password);
      const response = await axios.post('http://localhost:8000/token', formData);
      localStorage.setItem('token', response.data.access_token);
      setIsAuthenticated(true);
      toast.success('Logged in successfully!');
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Login failed');
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await axios.post('http://localhost:8000/register', {
        email: authForm.email,
        password: authForm.password
      });
      toast.success('Registration successful! Please login.');
      setIsRegistering(false);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Registration failed');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsAuthenticated(false);
    setCurrentMidiUrl('');
    toast.success('Logged out');
  };

  // Generate handler
  const handleGenerate = async () => {
    if (mode === 'simple' && !description) {
      toast.error('Please describe what you want to generate');
      return;
    }

    setLoading(true);
    try {
      const token = localStorage.getItem('token');

      if (mode === 'simple') {
        // Use Complete Track Generator
        const response = await axios.post(
          'http://localhost:8000/api/generate/midi',
          null,
          {
            params: {
              description,
              instrument: generationType === 'full' ? 'full_drums' : generationType,
              musical_key: musicalKey,
              musical_scale: musicalScale
            },
            headers: { 'Authorization': `Bearer ${token}` }
          }
        );

        if (response.data.file_url) {
          setCurrentMidiUrl(`http://localhost:8000${response.data.file_url}`);
          setCurrentBpm(bpm);
          toast.success('MIDI generated successfully!');
        }
      } else {
        // Use DNA Pattern Generator
        const response = await axios.post(
          'http://localhost:8000/api/integrated-midi/generate',
          {
            description: description || `${style} ${generationType} pattern`,
            style,
            instrument: generationType,
            bpm,
            bars: dnaParams.bars,
            use_dna: true,
            humanize: true,
            density: dnaParams.density,
            complexity: dnaParams.complexity,
            groove: dnaParams.groove,
            evolution: dnaParams.evolution,
            velocity_curve: 'natural',
            musical_key: musicalKey,
            musical_scale: musicalScale
          },
          {
            headers: { 'Authorization': `Bearer ${token}` }
          }
        );

        if (response.data.download_url) {
          setCurrentMidiUrl(`http://localhost:8000${response.data.download_url}`);
          setCurrentBpm(response.data.metadata.bpm);
          toast.success('DNA Pattern generated successfully!');
        }
      }
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Generation failed');
    } finally {
      setLoading(false);
    }
  };

  // Render auth forms if not authenticated
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-black text-white p-8">
        <div className="max-w-md mx-auto">
          <h1 className="text-4xl font-bold text-center mb-2 bg-gradient-to-r from-blue-400 to-purple-500 text-transparent bg-clip-text">
            AI Music Copilot
          </h1>
          <p className="text-center text-gray-400 mb-8">Professional MIDI Pattern Generator</p>

          <div className="bg-gray-900 p-6 rounded-lg border border-gray-800">
            <h2 className="text-2xl font-bold mb-6 text-center">
              {isRegistering ? 'Create Account' : 'Welcome Back'}
            </h2>

            <form onSubmit={isRegistering ? handleRegister : handleLogin} className="space-y-4">
              <div>
                <label className="text-sm text-gray-400 mb-2 block">Email</label>
                <input
                  type="email"
                  value={authForm.email}
                  onChange={(e) => setAuthForm({...authForm, email: e.target.value})}
                  placeholder="your@email.com"
                  className="w-full p-3 bg-gray-800 border border-gray-700 rounded focus:border-blue-500 focus:outline-none"
                  required
                />
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-2 block">Password</label>
                <input
                  type="password"
                  value={authForm.password}
                  onChange={(e) => setAuthForm({...authForm, password: e.target.value})}
                  placeholder="••••••••"
                  className="w-full p-3 bg-gray-800 border border-gray-700 rounded focus:border-blue-500 focus:outline-none"
                  required
                  minLength={6}
                />
              </div>

              <button
                type="submit"
                className="w-full py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:shadow-lg rounded-lg font-semibold transition-all"
              >
                {isRegistering ? 'Create Account' : 'Login'}
              </button>
            </form>

            <div className="mt-4 text-center">
              <button
                onClick={() => setIsRegistering(!isRegistering)}
                className="text-sm text-gray-400 hover:text-white transition-colors"
              >
                {isRegistering ? 'Already have an account? Login' : "Don't have an account? Register"}
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Main generator interface
  return (
    <div className="min-h-screen bg-black text-white p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div className="flex-1 text-center">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 text-transparent bg-clip-text mb-2">
              AI Music Copilot
            </h1>
            <p className="text-gray-400">Professional MIDI Pattern Generator</p>
          </div>
          <button
            onClick={handleLogout}
            className="px-6 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg text-sm"
          >
            Logout
          </button>
        </div>

        {/* Mode Selector */}
        <div className="flex justify-center gap-4 mb-8">
          <button
            onClick={() => setMode('simple')}
            className={`px-8 py-3 rounded-lg font-semibold transition-all ${
              mode === 'simple'
                ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/50'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            🎹 Simple Mode
          </button>
          <button
            onClick={() => setMode('advanced')}
            className={`px-8 py-3 rounded-lg font-semibold transition-all ${
              mode === 'advanced'
                ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/50'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            🧬 DNA Mode (Advanced)
          </button>
        </div>

        {/* Generation Type Selector */}
        <div className="bg-gray-900 p-6 rounded-xl mb-6 border border-gray-800">
          <h2 className="text-xl font-bold mb-4">What to Generate</h2>
          <div className="grid grid-cols-4 gap-4">
            {[
              { type: 'drums', emoji: '🥁', label: 'Drums', desc: 'Kick, Snare, Hats' },
              { type: 'bass', emoji: '🎸', label: 'Bass', desc: 'Sub, 808, Basslines' },
              { type: 'melody', emoji: '🎹', label: 'Melody', desc: 'Leads, Chords' },
              { type: 'full', emoji: '🎼', label: 'Full Track', desc: 'Complete Pattern' }
            ].map(({ type, emoji, label, desc }) => (
              <button
                key={type}
                onClick={() => setGenerationType(type as any)}
                className={`p-4 rounded-lg border-2 transition-all ${
                  generationType === type
                    ? 'border-blue-500 bg-blue-500/20'
                    : 'border-gray-700 hover:border-gray-600'
                }`}
              >
                <div className="text-3xl mb-2">{emoji}</div>
                <div className="font-bold">{label}</div>
                <div className="text-xs text-gray-400">{desc}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Parameters Section */}
        <div className="bg-gray-900 p-6 rounded-xl mb-6 border border-gray-800">
          <h3 className="text-lg font-bold mb-4">
            {mode === 'simple' ? '🎹 Quick Settings' : '🧬 DNA Parameters'}
          </h3>

          <div className="space-y-4">
            {/* Description (both modes) */}
            <div>
              <label className="text-sm text-gray-400 mb-2 block">
                Description {mode === 'simple' && <span className="text-red-400">*</span>}
              </label>
              <input
                type="text"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder={`Describe your ${generationType} pattern...`}
                className="w-full p-3 bg-black border border-gray-700 rounded-lg focus:border-blue-500 focus:outline-none"
              />
            </div>

            {/* Common settings */}
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="text-sm text-gray-400 mb-2 block">Style</label>
                <select
                  value={style}
                  onChange={(e) => setStyle(e.target.value)}
                  className="w-full p-3 bg-black border border-gray-700 rounded-lg focus:border-blue-500 focus:outline-none"
                >
                  <option value="techno">Techno</option>
                  <option value="house">House</option>
                  <option value="trap">Trap</option>
                  <option value="dnb">DnB</option>
                  <option value="lofi">Lo-Fi</option>
                </select>
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-2 block">BPM: {bpm}</label>
                <input
                  type="range"
                  min="60"
                  max="200"
                  value={bpm}
                  onChange={(e) => setBpm(parseInt(e.target.value))}
                  className="w-full h-10 accent-blue-600"
                />
              </div>

              <div>
                <label className="text-sm text-gray-400 mb-2 block">Key & Scale</label>
                <div className="flex gap-2">
                  <select
                    value={musicalKey}
                    onChange={(e) => setMusicalKey(e.target.value)}
                    className="flex-1 p-3 bg-black border border-gray-700 rounded-lg focus:border-blue-500 focus:outline-none"
                  >
                    {['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'].map(key => (
                      <option key={key} value={key}>{key}</option>
                    ))}
                  </select>
                  <select
                    value={musicalScale}
                    onChange={(e) => setMusicalScale(e.target.value)}
                    className="flex-1 p-3 bg-black border border-gray-700 rounded-lg focus:border-blue-500 focus:outline-none"
                  >
                    <option value="minor">Minor</option>
                    <option value="major">Major</option>
                    <option value="dorian">Dorian</option>
                    <option value="phrygian">Phrygian</option>
                  </select>
                </div>
              </div>
            </div>

            {/* DNA Parameters (advanced mode only) */}
            {mode === 'advanced' && (
              <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-700">
                {Object.entries(dnaParams).map(([key, value]) => (
                  <div key={key}>
                    <label className="flex justify-between text-sm mb-2">
                      <span className="capitalize text-gray-400">{key}</span>
                      <span className="text-blue-400">{value.toFixed(2)}</span>
                    </label>
                    <input
                      type="range"
                      min={key === 'bars' ? 1 : 0}
                      max={key === 'bars' ? 16 : 1}
                      step={key === 'bars' ? 1 : 0.05}
                      value={value}
                      onChange={(e) => setDnaParams({
                        ...dnaParams,
                        [key]: parseFloat(e.target.value)
                      })}
                      className="w-full h-8 accent-purple-600"
                    />
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Generate Button */}
          <button
            onClick={handleGenerate}
            disabled={loading}
            className={`w-full py-4 mt-6 rounded-lg font-bold text-lg transition-all ${
              loading
                ? 'bg-gray-600 cursor-not-allowed'
                : mode === 'simple'
                  ? 'bg-gradient-to-r from-blue-600 to-blue-700 hover:shadow-lg hover:shadow-blue-500/50'
                  : 'bg-gradient-to-r from-purple-600 to-purple-700 hover:shadow-lg hover:shadow-purple-500/50'
            }`}
          >
            {loading ? 'Generating...' : `Generate ${generationType.toUpperCase()} Pattern 🎵`}
          </button>
        </div>

        {/* MIDI Player */}
        {currentMidiUrl && (
          <MidiPlayerWithAudio midiUrl={currentMidiUrl} bpm={currentBpm} />
        )}
      </div>
    </div>
  );
}
