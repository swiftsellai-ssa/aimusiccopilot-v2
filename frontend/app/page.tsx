// frontend/app/page-unified.tsx - UNIFIED MUSIC GENERATOR
// Clean, simple interface with Simple and Advanced (DNA) modes
// Features: Keyboard Shortcuts, Generation History, Preset Patterns

'use client';
import { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { toast } from 'react-hot-toast';
import MidiPlayerWithAudio from '@/components/MidiPlayerWithAudio';
import AnalyticsDashboard from '@/components/AnalyticsDashboard';
import { analytics } from '@/lib/analytics';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Preset Patterns
const PRESETS = [
  {
    name: '🔥 Minimal Techno',
    description: 'Minimal techno kick pattern',
    mode: 'advanced' as const,
    type: 'drums' as const,
    style: 'techno',
    bpm: 128,
    key: 'C',
    scale: 'minor',
    dna: { density: 0.3, complexity: 0.4, groove: 0.2, evolution: 0.1, bars: 4 }
  },
  {
    name: '⚡ Hard Techno',
    description: 'Hard techno with heavy kicks',
    mode: 'advanced' as const,
    type: 'drums' as const,
    style: 'techno',
    bpm: 145,
    key: 'D',
    scale: 'minor',
    dna: { density: 0.8, complexity: 0.7, groove: 0.3, evolution: 0.4, bars: 4 }
  },
  {
    name: '🏠 Deep House',
    description: 'Deep house groove with bass',
    mode: 'advanced' as const,
    type: 'full' as const,
    style: 'house',
    bpm: 122,
    key: 'A',
    scale: 'minor',
    dna: { density: 0.6, complexity: 0.5, groove: 0.7, evolution: 0.3, bars: 8 }
  },
  {
    name: '🎯 Trap Beats',
    description: 'Modern trap with 808s',
    mode: 'advanced' as const,
    type: 'full' as const,
    style: 'trap',
    bpm: 140,
    key: 'G',
    scale: 'minor',
    dna: { density: 0.5, complexity: 0.6, groove: 0.4, evolution: 0.5, bars: 4 }
  },
  {
    name: '🌙 Lo-Fi Chill',
    description: 'Relaxed lo-fi vibes',
    mode: 'advanced' as const,
    type: 'melody' as const,
    style: 'lofi',
    bpm: 85,
    key: 'C',
    scale: 'major',
    dna: { density: 0.4, complexity: 0.3, groove: 0.5, evolution: 0.2, bars: 8 }
  }
];

// Generation History Item
interface HistoryItem {
  id: string;
  timestamp: number;
  mode: 'simple' | 'advanced';
  type: 'drums' | 'bass' | 'melody' | 'full';
  style: string;
  bpm: number;
  url: string;
  description: string;
  dna?: any;
  key: string;
  scale: string;
  starred?: boolean;
}

// Custom Preset Item
interface CustomPreset {
  id: string;
  name: string;
  description: string;
  mode: 'simple' | 'advanced';
  type: 'drums' | 'bass' | 'melody' | 'full';
  style: string;
  bpm: number;
  key: string;
  scale: string;
  dna: {
    density: number;
    complexity: number;
    groove: number;
    evolution: number;
    bars: number;
  };
  createdAt: number;
}

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
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [showPresets, setShowPresets] = useState(false);
  const [showKeyboardHelp, setShowKeyboardHelp] = useState(false);
  const [showSavePreset, setShowSavePreset] = useState(false);
  const [presetName, setPresetName] = useState('');
  const [showShareModal, setShowShareModal] = useState(false);
  const [shareTitle, setShareTitle] = useState('');
  const [shareDescription, setShareDescription] = useState('');
  const [shareLink, setShareLink] = useState('');

  // Multi-track project state
  const [showProjectModal, setShowProjectModal] = useState(false);
  const [userProjects, setUserProjects] = useState<any[]>([]);
  const [selectedProject, setSelectedProject] = useState<number | null>(null);
  const [trackName, setTrackName] = useState('');

  // Generation History
  const [history, setHistory] = useState<HistoryItem[]>([]);

  // Custom Presets
  const [customPresets, setCustomPresets] = useState<CustomPreset[]>([]);

  // Ref for MidiPlayer to access play/pause/download functions
  const playerRef = useRef<any>(null);

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

  // Load history and custom presets from localStorage
  useEffect(() => {
    const savedHistory = localStorage.getItem('generationHistory');
    if (savedHistory) {
      try {
        setHistory(JSON.parse(savedHistory));
      } catch (e) {
        console.error('Failed to load history:', e);
      }
    }

    const savedPresets = localStorage.getItem('customPresets');
    if (savedPresets) {
      try {
        setCustomPresets(JSON.parse(savedPresets));
      } catch (e) {
        console.error('Failed to load custom presets:', e);
      }
    }
  }, []);

  // Check auth on load and start analytics session
  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsAuthenticated(!!token);

    // Start analytics session if authenticated
    if (token) {
      analytics.startSession();
    }

    // End session on unmount
    return () => {
      if (token) {
        analytics.endSession();
      }
    };
  }, []);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if typing in input/textarea
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      // Spacebar: Generate
      if (e.code === 'Space') {
        e.preventDefault();
        if (!loading && isAuthenticated) {
          handleGenerate();
          toast.success('⌨️ Spacebar: Generate', { duration: 1000 });
        }
      }

      // Ctrl+D: Download
      if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
        e.preventDefault();
        if (currentMidiUrl && playerRef.current?.handleDownload) {
          playerRef.current.handleDownload();
          toast.success('⌨️ Ctrl+D: Download', { duration: 1000 });
        }
      }

      // Ctrl+P: Play/Pause
      if ((e.ctrlKey || e.metaKey) && e.key === 'p') {
        e.preventDefault();
        if (currentMidiUrl && playerRef.current?.togglePlayPause) {
          playerRef.current.togglePlayPause();
          toast.success('⌨️ Ctrl+P: Play/Pause', { duration: 1000 });
        }
      }

      // Ctrl+S: Stop
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        if (currentMidiUrl && playerRef.current?.handleStop) {
          playerRef.current.handleStop();
          toast.success('⌨️ Ctrl+S: Stop', { duration: 1000 });
        }
      }

      // ?: Show keyboard help
      if (e.shiftKey && e.key === '?') {
        e.preventDefault();
        setShowKeyboardHelp(true);
      }

      // Escape: Close modals
      if (e.key === 'Escape') {
        setShowKeyboardHelp(false);
        setShowHistory(false);
        setShowPresets(false);
        setShowSavePreset(false);
      }

      // Ctrl+Shift+S: Save as preset
      if ((e.ctrlKey || e.metaKey) && e.shiftKey && e.key === 'S') {
        e.preventDefault();
        if (isAuthenticated) {
          setShowSavePreset(true);
          toast.success('⌨️ Ctrl+Shift+S: Save Preset', { duration: 1000 });
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [loading, isAuthenticated, currentMidiUrl]);

  // Auth handlers
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const formData = new URLSearchParams();
      formData.append('username', authForm.email);
      formData.append('password', authForm.password);
      const response = await axios.post(`${API_URL}/token`, formData);
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
      await axios.post(`${API_URL}/register`, {
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

  // Save generation to history
  const saveToHistory = (url: string, metadata: any) => {
    const newItem: HistoryItem = {
      id: Date.now().toString(),
      timestamp: Date.now(),
      mode,
      type: generationType,
      style,
      bpm: metadata.bpm || bpm,
      url,
      description: description || `${style} ${generationType}`,
      dna: mode === 'advanced' ? dnaParams : undefined,
      key: musicalKey,
      scale: musicalScale
    };

    const updatedHistory = [newItem, ...history].slice(0, 10); // Keep last 10
    setHistory(updatedHistory);
    localStorage.setItem('generationHistory', JSON.stringify(updatedHistory));
  };

  // Load from history
  const loadFromHistory = (item: HistoryItem) => {
    setMode(item.mode);
    setGenerationType(item.type);
    setStyle(item.style);
    setBpm(item.bpm);
    setMusicalKey(item.key);
    setMusicalScale(item.scale);
    setDescription(item.description);
    if (item.dna) {
      setDnaParams(item.dna);
    }
    setCurrentMidiUrl(item.url);
    setCurrentBpm(item.bpm);
    setShowHistory(false);
    toast.success(`Loaded: ${item.description}`);
  };

  // Load preset (works for both built-in and custom)
  const loadPreset = (preset: typeof PRESETS[0] | CustomPreset) => {
    setMode(preset.mode);
    setGenerationType(preset.type);
    setStyle(preset.style);
    setBpm(preset.bpm);
    setMusicalKey(preset.key);
    setMusicalScale(preset.scale);
    setDescription(preset.description);
    setDnaParams(preset.dna);
    setShowPresets(false);
    toast.success(`Preset loaded: ${preset.name}`);
  };

  // Save current settings as custom preset
  const saveAsPreset = () => {
    if (!presetName.trim()) {
      toast.error('Please enter a preset name');
      return;
    }

    const newPreset: CustomPreset = {
      id: Date.now().toString(),
      name: presetName.trim(),
      description: description || `${style} ${generationType} pattern`,
      mode,
      type: generationType,
      style,
      bpm,
      key: musicalKey,
      scale: musicalScale,
      dna: { ...dnaParams },
      createdAt: Date.now()
    };

    const updatedPresets = [newPreset, ...customPresets];
    setCustomPresets(updatedPresets);
    localStorage.setItem('customPresets', JSON.stringify(updatedPresets));

    setShowSavePreset(false);
    setPresetName('');
    toast.success(`Preset saved: ${newPreset.name}`);
  };

  // Delete custom preset
  const deletePreset = (presetId: string) => {
    const updatedPresets = customPresets.filter(p => p.id !== presetId);
    setCustomPresets(updatedPresets);
    localStorage.setItem('customPresets', JSON.stringify(updatedPresets));
    toast.success('Preset deleted');
  };

  // Toggle star on history item
  const toggleStar = (itemId: string) => {
    const updatedHistory = history.map(item =>
      item.id === itemId ? { ...item, starred: !item.starred } : item
    );
    setHistory(updatedHistory);
    localStorage.setItem('generationHistory', JSON.stringify(updatedHistory));

    const item = updatedHistory.find(i => i.id === itemId);
    toast.success(item?.starred ? '⭐ Starred!' : 'Star removed', { duration: 1000 });
  };

  // Share current generation
  const shareGeneration = async () => {
    if (!shareTitle.trim()) {
      toast.error('Please enter a title for your shared generation');
      return;
    }

    if (!currentMidiUrl) {
      toast.error('No generation to share. Please generate a pattern first.');
      return;
    }

    // Check authentication
    const token = localStorage.getItem('token');
    if (!token || !isAuthenticated) {
      toast.error('Please log in to share generations');
      setShowShareModal(false);
      return;
    }

    try {
      const response = await axios.post(
        `${API_URL}/social/generations/share`,
        {
          title: shareTitle.trim(),
          description: shareDescription.trim() || null,
          mode,
          type: generationType,
          style,
          bpm,
          key: musicalKey,
          scale: musicalScale,
          density: mode === 'advanced' ? dnaParams.density : null,
          complexity: mode === 'advanced' ? dnaParams.complexity : null,
          groove: mode === 'advanced' ? dnaParams.groove : null,
          evolution: mode === 'advanced' ? dnaParams.evolution : null,
          bars: mode === 'advanced' ? dnaParams.bars : null,
          midi_url: currentMidiUrl
        },
        { headers: { 'Authorization': `Bearer ${token}` } }
      );

      const shareUrl = `${window.location.origin}/share/${response.data.share_id}`;
      setShareLink(shareUrl);

      // Copy to clipboard
      navigator.clipboard.writeText(shareUrl);
      toast.success('🔗 Share link copied to clipboard!');
    } catch (err: any) {
      console.error('Failed to share generation:', err);

      // Handle specific error cases
      if (err.response?.status === 401) {
        toast.error('Session expired. Please log in again.');
        handleLogout();
      } else {
        toast.error(err.response?.data?.detail || 'Failed to share generation');
      }
    }
  };

  // Load user projects for "Add to Project" modal
  const loadUserProjects = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const response = await axios.get(`${API_URL}/api/projects`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setUserProjects(response.data);
    } catch (err: any) {
      console.error('Error loading projects:', err);
    }
  };

  // Add current generation as a track to selected project
  const addToProject = async () => {
    if (!selectedProject) {
      toast.error('Please select a project');
      return;
    }

    if (!trackName.trim()) {
      toast.error('Please enter a track name');
      return;
    }

    if (!currentMidiUrl) {
      toast.error('No generation to add. Please generate a pattern first.');
      return;
    }

    const token = localStorage.getItem('token');
    if (!token || !isAuthenticated) {
      toast.error('Please log in to add tracks to projects');
      setShowProjectModal(false);
      return;
    }

    try {
      await axios.post(
        `${API_URL}/api/projects/${selectedProject}/tracks`,
        {
          name: trackName.trim(),
          type: generationType,
          midi_url: currentMidiUrl,
          mode: mode,
          style: style,
          density: mode === 'advanced' ? dnaParams.density : 0.5,
          complexity: mode === 'advanced' ? dnaParams.complexity : 0.5,
          groove: mode === 'advanced' ? dnaParams.groove : 0.5,
          evolution: mode === 'advanced' ? dnaParams.evolution : 0.3,
          bars: mode === 'advanced' ? dnaParams.bars : 4,
          volume: 0.8,
          pan: 0.5,
          muted: false,
          solo: false
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      toast.success('Track added to project!');
      setShowProjectModal(false);
      setTrackName('');
      setSelectedProject(null);

      // Optionally navigate to project
      const project = userProjects.find(p => p.id === selectedProject);
      if (project && confirm(`Track added! View project "${project.name}"?`)) {
        window.location.href = `/projects/${selectedProject}`;
      }
    } catch (err: any) {
      console.error('Failed to add track to project:', err);
      if (err.response?.status === 401) {
        toast.error('Session expired. Please log in again.');
        handleLogout();
      } else {
        toast.error(err.response?.data?.detail || 'Failed to add track to project');
      }
    }
  };

  // Generate handler
  const handleGenerate = async () => {
    if (mode === 'simple' && !description) {
      toast.error('Please describe what you want to generate');
      return;
    }

    const startTime = Date.now();
    setLoading(true);

    try {
      const token = localStorage.getItem('token');

      if (mode === 'simple') {
        // Use Complete Track Generator
        const response = await axios.post(
          `${API_URL}/api/generate/midi`,
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
          const generationTime = Date.now() - startTime;

          // Track successful generation
          const eventId = await analytics.trackGeneration({
            mode,
            generation_type: generationType,
            style,
            bpm,
            musical_key: musicalKey,
            musical_scale: musicalScale,
            success: true,
            generation_time_ms: generationTime
          });

          const fileUrl = `${API_URL}${response.data.file_url}`;
          setCurrentMidiUrl(fileUrl);
          setCurrentBpm(bpm);
          saveToHistory(fileUrl, { bpm });
          toast.success('MIDI generated successfully!');
        }
      } else {
        // Use DNA Pattern Generator
        const response = await axios.post(
          `${API_URL}/api/integrated-midi/generate`,
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
          const generationTime = Date.now() - startTime;

          // Track successful generation with DNA params
          const eventId = await analytics.trackGeneration({
            mode,
            generation_type: generationType,
            style,
            bpm,
            musical_key: musicalKey,
            musical_scale: musicalScale,
            density: dnaParams.density,
            complexity: dnaParams.complexity,
            groove: dnaParams.groove,
            evolution: dnaParams.evolution,
            bars: dnaParams.bars,
            success: true,
            generation_time_ms: generationTime
          });

          const fileUrl = `${API_URL}${response.data.download_url}`;
          setCurrentMidiUrl(fileUrl);
          setCurrentBpm(response.data.metadata.bpm);
          saveToHistory(fileUrl, response.data.metadata);
          toast.success('DNA Pattern generated successfully!');
        }
      }
    } catch (error: any) {
      const generationTime = Date.now() - startTime;

      // Track failed generation
      await analytics.trackGeneration({
        mode,
        generation_type: generationType,
        style,
        bpm,
        musical_key: musicalKey,
        musical_scale: musicalScale,
        density: mode === 'advanced' ? dnaParams.density : undefined,
        complexity: mode === 'advanced' ? dnaParams.complexity : undefined,
        groove: mode === 'advanced' ? dnaParams.groove : undefined,
        evolution: mode === 'advanced' ? dnaParams.evolution : undefined,
        bars: mode === 'advanced' ? dnaParams.bars : undefined,
        success: false,
        error_message: error.response?.data?.detail || 'Generation failed',
        generation_time_ms: generationTime
      });

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
                  onChange={(e) => setAuthForm({ ...authForm, email: e.target.value })}
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
                  onChange={(e) => setAuthForm({ ...authForm, password: e.target.value })}
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
    <div className="flex h-screen bg-black text-white overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-900 border-r border-gray-800 flex flex-col flex-shrink-0">
        <div className="p-6 border-b border-gray-800">
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 text-transparent bg-clip-text">
            AIMusic
          </h1>
          <p className="text-xs text-gray-400 mt-1">Copilot</p>
        </div>

        <nav className="flex-1 p-4 space-y-2 overflow-y-auto">
          <a href="#" className="flex items-center gap-3 px-4 py-3 bg-gray-800 text-white rounded-lg transition-all font-medium border border-gray-700">
            <span className="text-xl">🎹</span> Generator
          </a>
          <a href="/projects" className="flex items-center gap-3 px-4 py-3 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-all font-medium">
            <span className="text-xl">🎼</span> Projects
          </a>
          <a href="/gallery" className="flex items-center gap-3 px-4 py-3 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-all font-medium">
            <span className="text-xl">🎵</span> Gallery
          </a>
          <a href="/marketplace" className="flex items-center gap-3 px-4 py-3 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-all font-medium">
            <span className="text-xl">🛒</span> Marketplace
          </a>
        </nav>

        <div className="p-4 border-t border-gray-800">
          <div className="flex items-center gap-3 px-4 py-3 text-gray-400">
            <div className="w-8 h-8 rounded-full bg-blue-600 flex items-center justify-center text-white font-bold text-xs">
              {isAuthenticated ? 'U' : '?'}
            </div>
            <div className="flex-1 overflow-hidden">
              <div className="text-sm font-bold truncate">User</div>
              <div className="text-xs text-gray-500">Free Plan</div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Topbar */}
        <header className="h-16 border-b border-gray-800 flex items-center justify-between px-8 bg-black/50 backdrop-blur z-10 flex-shrink-0">
          <div className="flex items-center gap-2 text-gray-400 text-sm">
            <span className="text-gray-500">Dashboard</span>
            <span>/</span>
            <span className="text-white">Generator</span>
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={() => setShowPresets(!showPresets)}
              className={`px-4 py-2 rounded-lg text-sm transition-all flex items-center gap-2 ${showPresets
                ? 'bg-purple-600 hover:bg-purple-700 text-white'
                : 'text-gray-400 hover:text-white hover:bg-gray-800'
                }`}
              title="Load preset patterns"
            >
              <span>🎨</span> My Presets
            </button>
            <button
              onClick={() => setShowHistory(!showHistory)}
              className={`px-4 py-2 rounded-lg text-sm transition-all flex items-center gap-2 ${showHistory
                ? 'bg-blue-600 hover:bg-blue-700 text-white'
                : 'text-gray-400 hover:text-white hover:bg-gray-800'
                }`}
              title="View generation history"
            >
              <span>📜</span> History {history.length > 0 && `(${history.length})`}
            </button>
            <button
              onClick={() => setShowAnalytics(!showAnalytics)}
              className={`p-2 rounded-lg transition-all ${showAnalytics ? 'text-blue-400 bg-blue-400/10' : 'text-gray-400 hover:text-white hover:bg-gray-800'}`}
              title="View analytics"
            >
              📊
            </button>

            <button
              onClick={() => setShowKeyboardHelp(true)}
              className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-all"
              title="Keyboard shortcuts"
            >
              ⌨️
            </button>

            <div className="h-6 w-px bg-gray-800 mx-2"></div>

            <button
              onClick={handleLogout}
              className="px-4 py-2 text-red-400 hover:text-red-300 hover:bg-red-400/10 rounded-lg text-sm transition-all font-medium"
            >
              Logout
            </button>
          </div>
        </header>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-8 relative">
          <div className="max-w-5xl mx-auto pb-24">

            {/* Mode Selector */}
            <div className="flex justify-center gap-4 mb-8">
              <button
                onClick={() => setMode('simple')}
                className={`px-8 py-3 rounded-lg font-semibold transition-all ${mode === 'simple'
                  ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/50'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                  }`}
              >
                🎹 Simple Mode
              </button>
              <button
                onClick={() => setMode('advanced')}
                className={`px-8 py-3 rounded-lg font-semibold transition-all ${mode === 'advanced'
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
                    className={`p-4 rounded-lg border-2 transition-all ${generationType === type
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
                      <option value="modern_trap">Modern Trap</option>
                      <option value="cinematic">Cinematic / Ambient</option>
                      <option value="deep_house">Deep House</option>
                      <option value="liquid_dnb">Liquid DnB</option>
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

              {/* Action Buttons */}
              <div className="flex gap-3 mt-6">
                <button
                  onClick={handleGenerate}
                  disabled={loading}
                  className={`flex-1 py-4 rounded-lg font-bold text-lg transition-all ${loading
                    ? 'bg-gray-600 cursor-not-allowed'
                    : mode === 'simple'
                      ? 'bg-gradient-to-r from-blue-600 to-blue-700 hover:shadow-lg hover:shadow-blue-500/50'
                      : 'bg-gradient-to-r from-purple-600 to-purple-700 hover:shadow-lg hover:shadow-purple-500/50'
                    }`}
                >
                  {loading ? 'Generating...' : `Generate ${generationType.toUpperCase()} Pattern 🎵`}
                </button>

                <button
                  onClick={() => setShowSavePreset(true)}
                  className="px-6 py-4 bg-gray-800 hover:bg-gray-700 rounded-lg font-semibold transition-all border border-gray-700 hover:border-purple-500"
                  title="Save current settings as preset (Ctrl+Shift+S)"
                >
                  💾 Save Preset
                </button>

                <button
                  onClick={() => {
                    if (!currentMidiUrl) {
                      toast.error('Generate a pattern first to share');
                      return;
                    }
                    setShowShareModal(true);
                    setShareTitle(description || `${style} ${generationType}`);
                    setShareDescription('');
                    setShareLink('');
                  }}
                  disabled={!currentMidiUrl}
                  className={`px-6 py-4 rounded-lg font-semibold transition-all border ${currentMidiUrl
                    ? 'bg-blue-600 hover:bg-blue-700 border-blue-500 text-white'
                    : 'bg-gray-700 border-gray-600 text-gray-500 cursor-not-allowed'
                    }`}
                  title="Share this generation publicly"
                >
                  🔗 Share
                </button>

                <button
                  onClick={() => {
                    if (!currentMidiUrl) {
                      toast.error('Generate a pattern first to add to project');
                      return;
                    }
                    setShowProjectModal(true);
                    setTrackName(`${generationType} - ${style}`);
                    setSelectedProject(null);
                    loadUserProjects();
                  }}
                  disabled={!currentMidiUrl}
                  className={`px-6 py-4 rounded-lg font-semibold transition-all border ${currentMidiUrl
                    ? 'bg-purple-600 hover:bg-purple-700 border-purple-500 text-white'
                    : 'bg-gray-700 border-gray-600 text-gray-500 cursor-not-allowed'
                    }`}
                  title="Add this track to a multi-track project"
                >
                  🎼 Add to Project
                </button>
              </div>
            </div>

            {/* MIDI Player */}
            {currentMidiUrl && (
              <MidiPlayerWithAudio ref={playerRef} midiUrl={currentMidiUrl} bpm={currentBpm} />
            )}

            {/* Keyboard Shortcuts Help Modal */}
            {showKeyboardHelp && (
              <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-8">
                <div className="bg-gray-900 p-6 rounded-lg border border-gray-700 max-w-md w-full">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-xl font-bold">⌨️ Keyboard Shortcuts</h3>
                    <button
                      onClick={() => setShowKeyboardHelp(false)}
                      className="text-gray-400 hover:text-white"
                    >
                      ✕
                    </button>
                  </div>
                  <div className="space-y-3">
                    <div className="flex justify-between items-center p-3 bg-gray-800 rounded">
                      <span className="text-gray-300">Generate</span>
                      <kbd className="px-3 py-1 bg-black rounded text-sm">Space</kbd>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-gray-800 rounded">
                      <span className="text-gray-300">Download</span>
                      <kbd className="px-3 py-1 bg-black rounded text-sm">Ctrl + D</kbd>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-gray-800 rounded">
                      <span className="text-gray-300">Play / Pause</span>
                      <kbd className="px-3 py-1 bg-black rounded text-sm">Ctrl + P</kbd>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-gray-800 rounded">
                      <span className="text-gray-300">Stop</span>
                      <kbd className="px-3 py-1 bg-black rounded text-sm">Ctrl + S</kbd>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-gray-800 rounded">
                      <span className="text-gray-300">Save Preset</span>
                      <kbd className="px-3 py-1 bg-black rounded text-sm">Ctrl + Shift + S</kbd>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-gray-800 rounded">
                      <span className="text-gray-300">Show Help</span>
                      <kbd className="px-3 py-1 bg-black rounded text-sm">Shift + ?</kbd>
                    </div>
                    <div className="flex justify-between items-center p-3 bg-gray-800 rounded">
                      <span className="text-gray-300">Close Modals</span>
                      <kbd className="px-3 py-1 bg-black rounded text-sm">Esc</kbd>
                    </div>
                  </div>
                  <button
                    onClick={() => setShowKeyboardHelp(false)}
                    className="w-full mt-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg"
                  >
                    Got it!
                  </button>
                </div>
              </div>
            )}

            {/* Presets Modal */}
            {showPresets && (
              <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-8">
                <div className="bg-gray-900 p-6 rounded-lg border border-gray-700 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-xl font-bold">🎨 Preset Patterns</h3>
                    <button
                      onClick={() => setShowPresets(false)}
                      className="text-gray-400 hover:text-white"
                    >
                      ✕
                    </button>
                  </div>

                  {/* Custom Presets Section */}
                  {customPresets.length > 0 && (
                    <>
                      <h4 className="text-sm font-bold text-purple-400 mb-2 mt-4">My Presets ({customPresets.length})</h4>
                      <div className="grid gap-3 mb-6">
                        {customPresets.map((preset) => (
                          <div
                            key={preset.id}
                            className="p-4 bg-gray-800 rounded-lg border border-gray-700 hover:border-purple-500 transition-all"
                          >
                            <div className="flex justify-between items-start mb-2">
                              <button
                                onClick={() => loadPreset(preset)}
                                className="flex-1 text-left"
                              >
                                <h4 className="font-bold text-lg">{preset.name}</h4>
                              </button>
                              <div className="flex gap-2">
                                <span className="text-xs px-2 py-1 bg-purple-600 rounded">{preset.type.toUpperCase()}</span>
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    if (confirm(`Delete preset "${preset.name}"?`)) {
                                      deletePreset(preset.id);
                                    }
                                  }}
                                  className="text-red-400 hover:text-red-300 px-2"
                                  title="Delete preset"
                                >
                                  🗑️
                                </button>
                              </div>
                            </div>
                            <button
                              onClick={() => loadPreset(preset)}
                              className="w-full text-left"
                            >
                              <p className="text-sm text-gray-400 mb-2">{preset.description}</p>
                              <div className="flex gap-2 text-xs text-gray-500">
                                <span>{preset.style}</span>
                                <span>•</span>
                                <span>{preset.bpm} BPM</span>
                                <span>•</span>
                                <span>{preset.key} {preset.scale}</span>
                                <span>•</span>
                                <span>{preset.dna.bars} bars</span>
                              </div>
                            </button>
                          </div>
                        ))}
                      </div>
                    </>
                  )}

                  {/* Built-in Presets Section */}
                  <h4 className="text-sm font-bold text-blue-400 mb-2">Built-in Presets</h4>
                  <div className="grid gap-3">
                    {PRESETS.map((preset, idx) => (
                      <button
                        key={idx}
                        onClick={() => loadPreset(preset)}
                        className="p-4 bg-gray-800 hover:bg-gray-700 rounded-lg border border-gray-700 hover:border-purple-500 transition-all text-left"
                      >
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="font-bold text-lg">{preset.name}</h4>
                          <span className="text-xs px-2 py-1 bg-purple-600 rounded">{preset.type.toUpperCase()}</span>
                        </div>
                        <p className="text-sm text-gray-400 mb-2">{preset.description}</p>
                        <div className="flex gap-2 text-xs text-gray-500">
                          <span>{preset.style}</span>
                          <span>•</span>
                          <span>{preset.bpm} BPM</span>
                          <span>•</span>
                          <span>{preset.key} {preset.scale}</span>
                          <span>•</span>
                          <span>{preset.dna.bars} bars</span>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Save Preset Modal */}
            {showSavePreset && (
              <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-8">
                <div className="bg-gray-900 p-6 rounded-lg border border-gray-700 max-w-md w-full">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-xl font-bold">💾 Save as Preset</h3>
                    <button
                      onClick={() => {
                        setShowSavePreset(false);
                        setPresetName('');
                      }}
                      className="text-gray-400 hover:text-white"
                    >
                      ✕
                    </button>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <label className="text-sm text-gray-400 mb-2 block">Preset Name</label>
                      <input
                        type="text"
                        value={presetName}
                        onChange={(e) => setPresetName(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            saveAsPreset();
                          }
                        }}
                        placeholder="e.g., My Dark Techno"
                        className="w-full p-3 bg-black border border-gray-700 rounded-lg focus:border-purple-500 focus:outline-none"
                        autoFocus
                      />
                    </div>

                    <div className="bg-gray-800 p-3 rounded-lg space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Mode:</span>
                        <span className="text-white">{mode === 'simple' ? '🎹 Simple' : '🧬 DNA'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Type:</span>
                        <span className="text-white">{generationType.toUpperCase()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Style:</span>
                        <span className="text-white capitalize">{style}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">BPM:</span>
                        <span className="text-white">{bpm}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Key:</span>
                        <span className="text-white">{musicalKey} {musicalScale}</span>
                      </div>
                      {mode === 'advanced' && (
                        <>
                          <div className="border-t border-gray-700 my-2 pt-2"></div>
                          <div className="text-xs text-gray-500">
                            Density: {dnaParams.density.toFixed(2)} •
                            Complexity: {dnaParams.complexity.toFixed(2)} •
                            Groove: {dnaParams.groove.toFixed(2)} •
                            Evolution: {dnaParams.evolution.toFixed(2)} •
                            Bars: {dnaParams.bars}
                          </div>
                        </>
                      )}
                    </div>

                    <div className="flex gap-3">
                      <button
                        onClick={() => {
                          setShowSavePreset(false);
                          setPresetName('');
                        }}
                        className="flex-1 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={saveAsPreset}
                        className="flex-1 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold"
                      >
                        Save Preset
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Share Modal */}
            {showShareModal && (
              <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-8">
                <div className="bg-gray-900 p-6 rounded-lg border border-gray-700 max-w-md w-full">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-xl font-bold">🔗 Share Generation</h3>
                    <button
                      onClick={() => {
                        setShowShareModal(false);
                        setShareTitle('');
                        setShareDescription('');
                        setShareLink('');
                      }}
                      className="text-gray-400 hover:text-white"
                    >
                      ✕
                    </button>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <label className="text-sm text-gray-400 mb-2 block">Title *</label>
                      <input
                        type="text"
                        value={shareTitle}
                        onChange={(e) => setShareTitle(e.target.value)}
                        placeholder="e.g., Epic Techno Kick Pattern"
                        className="w-full p-3 bg-black border border-gray-700 rounded-lg focus:border-blue-500 focus:outline-none"
                        autoFocus
                      />
                    </div>

                    <div>
                      <label className="text-sm text-gray-400 mb-2 block">Description (optional)</label>
                      <textarea
                        value={shareDescription}
                        onChange={(e) => setShareDescription(e.target.value)}
                        placeholder="Tell others about this pattern..."
                        className="w-full p-3 bg-black border border-gray-700 rounded-lg focus:border-blue-500 focus:outline-none resize-none"
                        rows={3}
                      />
                    </div>

                    <div className="bg-gray-800 p-3 rounded-lg space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Mode:</span>
                        <span className="text-white">{mode === 'simple' ? '🎹 Simple' : '🧬 DNA'}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Type:</span>
                        <span className="text-white">{generationType.toUpperCase()}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Style:</span>
                        <span className="text-white capitalize">{style}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">BPM:</span>
                        <span className="text-white">{bpm}</span>
                      </div>
                    </div>

                    {shareLink && (
                      <div className="bg-green-900/30 border border-green-700 p-3 rounded-lg">
                        <div className="text-sm text-green-400 mb-2">✅ Share link created and copied!</div>
                        <div className="flex gap-2">
                          <input
                            type="text"
                            value={shareLink}
                            readOnly
                            className="flex-1 p-2 bg-black border border-green-700 rounded text-sm text-green-400"
                          />
                          <button
                            onClick={() => {
                              navigator.clipboard.writeText(shareLink);
                              toast.success('Link copied!');
                            }}
                            className="px-3 py-2 bg-green-600 hover:bg-green-700 rounded text-sm font-semibold"
                          >
                            Copy
                          </button>
                        </div>
                      </div>
                    )}

                    <div className="flex gap-3">
                      <button
                        onClick={() => {
                          setShowShareModal(false);
                          setShareTitle('');
                          setShareDescription('');
                          setShareLink('');
                        }}
                        className="flex-1 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg"
                      >
                        {shareLink ? 'Close' : 'Cancel'}
                      </button>
                      {!shareLink && (
                        <button
                          onClick={shareGeneration}
                          disabled={!shareTitle.trim()}
                          className={`flex-1 py-2 rounded-lg font-semibold ${shareTitle.trim()
                            ? 'bg-blue-600 hover:bg-blue-700'
                            : 'bg-gray-700 text-gray-500 cursor-not-allowed'
                            }`}
                        >
                          Share Publicly
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Add to Project Modal */}
            {showProjectModal && (
              <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-8">
                <div className="bg-gray-900 p-6 rounded-lg border border-gray-700 max-w-md w-full">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-xl font-bold">🎼 Add to Project</h3>
                    <button
                      onClick={() => {
                        setShowProjectModal(false);
                        setTrackName('');
                        setSelectedProject(null);
                      }}
                      className="text-gray-400 hover:text-white"
                    >
                      ✕
                    </button>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <label className="text-sm text-gray-400 mb-2 block">Track Name *</label>
                      <input
                        type="text"
                        value={trackName}
                        onChange={(e) => setTrackName(e.target.value)}
                        placeholder="e.g., Kick Pattern 1"
                        className="w-full p-3 bg-black border border-gray-700 rounded-lg focus:border-purple-500 focus:outline-none"
                        autoFocus
                      />
                    </div>

                    <div>
                      <label className="text-sm text-gray-400 mb-2 block">Select Project *</label>
                      {userProjects.length === 0 ? (
                        <div className="bg-gray-800 p-4 rounded-lg text-center">
                          <p className="text-gray-400 mb-3">No projects yet</p>
                          <a
                            href="/projects"
                            className="inline-block px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg text-sm font-semibold"
                          >
                            Create Your First Project
                          </a>
                        </div>
                      ) : (
                        <div className="space-y-2 max-h-60 overflow-y-auto">
                          {userProjects.map((project) => (
                            <button
                              key={project.id}
                              onClick={() => setSelectedProject(project.id)}
                              className={`w-full text-left p-3 rounded-lg border transition ${selectedProject === project.id
                                ? 'bg-purple-600 border-purple-500'
                                : 'bg-gray-800 border-gray-700 hover:border-purple-500'
                                }`}
                            >
                              <div className="font-semibold">{project.name}</div>
                              <div className="text-sm text-gray-400 mt-1">
                                {project.tracks.length} tracks • {project.bpm} BPM • {project.key} {project.scale}
                              </div>
                            </button>
                          ))}
                        </div>
                      )}
                    </div>

                    <div className="bg-gray-800 p-3 rounded-lg space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-400">Track Type:</span>
                        <span className="text-white capitalize">{generationType}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-400">Style:</span>
                        <span className="text-white capitalize">{style}</span>
                      </div>
                      {mode === 'advanced' && (
                        <>
                          <div className="flex justify-between">
                            <span className="text-gray-400">DNA Density:</span>
                            <span className="text-white">{(dnaParams.density * 100).toFixed(0)}%</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-gray-400">DNA Complexity:</span>
                            <span className="text-white">{(dnaParams.complexity * 100).toFixed(0)}%</span>
                          </div>
                        </>
                      )}
                    </div>

                    <div className="flex gap-3">
                      <button
                        onClick={() => {
                          setShowProjectModal(false);
                          setTrackName('');
                          setSelectedProject(null);
                        }}
                        className="flex-1 py-2 bg-gray-800 hover:bg-gray-700 rounded-lg"
                      >
                        Cancel
                      </button>
                      {userProjects.length > 0 && (
                        <button
                          onClick={addToProject}
                          disabled={!selectedProject || !trackName.trim()}
                          className={`flex-1 py-2 rounded-lg font-semibold ${selectedProject && trackName.trim()
                            ? 'bg-purple-600 hover:bg-purple-700'
                            : 'bg-gray-700 text-gray-500 cursor-not-allowed'
                            }`}
                        >
                          Add Track
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* History Modal */}
            {showHistory && (
              <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-8">
                <div className="bg-gray-900 p-6 rounded-lg border border-gray-700 max-w-2xl w-full max-h-[80vh] overflow-y-auto">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-xl font-bold">📜 Generation History</h3>
                    <button
                      onClick={() => setShowHistory(false)}
                      className="text-gray-400 hover:text-white"
                    >
                      ✕
                    </button>
                  </div>
                  {history.length === 0 ? (
                    <div className="text-center py-8 text-gray-400">
                      <p>No generation history yet</p>
                      <p className="text-sm mt-2">Generate some patterns to see them here!</p>
                    </div>
                  ) : (
                    <>
                      {/* Starred Items */}
                      {history.filter(item => item.starred).length > 0 && (
                        <>
                          <h4 className="text-sm font-bold text-yellow-400 mb-2 flex items-center gap-2">
                            ⭐ Starred ({history.filter(item => item.starred).length})
                          </h4>
                          <div className="grid gap-3 mb-6">
                            {history.filter(item => item.starred).map((item) => (
                              <div
                                key={item.id}
                                className="p-4 bg-gray-800 rounded-lg border border-yellow-500/30 hover:border-yellow-500 transition-all"
                              >
                                <div className="flex justify-between items-start mb-2">
                                  <button
                                    onClick={() => loadFromHistory(item)}
                                    className="flex-1 text-left"
                                  >
                                    <h4 className="font-bold">{item.description}</h4>
                                    <p className="text-xs text-gray-500 mt-1">
                                      {new Date(item.timestamp).toLocaleString()}
                                    </p>
                                  </button>
                                  <div className="flex gap-2 items-center">
                                    <button
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        toggleStar(item.id);
                                      }}
                                      className="text-xl hover:scale-110 transition-transform"
                                      title="Remove star"
                                    >
                                      ⭐
                                    </button>
                                    <span className="text-xs px-2 py-1 bg-blue-600 rounded">
                                      {item.mode === 'simple' ? '🎹' : '🧬'}
                                    </span>
                                    <span className="text-xs px-2 py-1 bg-purple-600 rounded">
                                      {item.type.toUpperCase()}
                                    </span>
                                  </div>
                                </div>
                                <button
                                  onClick={() => loadFromHistory(item)}
                                  className="w-full text-left"
                                >
                                  <div className="flex gap-2 text-xs text-gray-500">
                                    <span>{item.style}</span>
                                    <span>•</span>
                                    <span>{item.bpm} BPM</span>
                                    <span>•</span>
                                    <span>{item.key} {item.scale}</span>
                                    {item.dna && (
                                      <>
                                        <span>•</span>
                                        <span>D:{item.dna.density.toFixed(1)} C:{item.dna.complexity.toFixed(1)}</span>
                                      </>
                                    )}
                                  </div>
                                </button>
                              </div>
                            ))}
                          </div>
                        </>
                      )}

                      {/* All History Items */}
                      <h4 className="text-sm font-bold text-gray-400 mb-2">
                        All History ({history.length})
                      </h4>
                      <div className="grid gap-3">
                        {history.map((item) => (
                          <div
                            key={item.id}
                            className="p-4 bg-gray-800 rounded-lg border border-gray-700 hover:border-blue-500 transition-all"
                          >
                            <div className="flex justify-between items-start mb-2">
                              <button
                                onClick={() => loadFromHistory(item)}
                                className="flex-1 text-left"
                              >
                                <h4 className="font-bold">{item.description}</h4>
                                <p className="text-xs text-gray-500 mt-1">
                                  {new Date(item.timestamp).toLocaleString()}
                                </p>
                              </button>
                              <div className="flex gap-2 items-center">
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    toggleStar(item.id);
                                  }}
                                  className="text-xl hover:scale-110 transition-transform"
                                  title={item.starred ? 'Remove star' : 'Add star'}
                                >
                                  {item.starred ? '⭐' : '☆'}
                                </button>
                                <span className="text-xs px-2 py-1 bg-blue-600 rounded">
                                  {item.mode === 'simple' ? '🎹' : '🧬'}
                                </span>
                                <span className="text-xs px-2 py-1 bg-purple-600 rounded">
                                  {item.type.toUpperCase()}
                                </span>
                              </div>
                            </div>
                            <button
                              onClick={() => loadFromHistory(item)}
                              className="w-full text-left"
                            >
                              <div className="flex gap-2 text-xs text-gray-500">
                                <span>{item.style}</span>
                                <span>•</span>
                                <span>{item.bpm} BPM</span>
                                <span>•</span>
                                <span>{item.key} {item.scale}</span>
                                {item.dna && (
                                  <>
                                    <span>•</span>
                                    <span>D:{item.dna.density.toFixed(1)} C:{item.dna.complexity.toFixed(1)}</span>
                                  </>
                                )}
                              </div>
                            </button>
                          </div>
                        ))}
                      </div>
                    </>
                  )}
                </div>
              </div>
            )}

            {/* Analytics Dashboard */}
            {showAnalytics && (
              <div className="mt-6">
                <AnalyticsDashboard />
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}
