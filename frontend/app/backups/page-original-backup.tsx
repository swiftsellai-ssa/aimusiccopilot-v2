'use client';
import { useState, useEffect } from 'react';
import axios from 'axios';
import { Toaster, toast } from 'react-hot-toast';
import AuthForm from '../components/AuthForm';
import MusicPlayer from '../components/MusicPlayer';
import MidiVisualizer from '../components/MidiVisualizer';
import RecommendationPanel from '../components/RecommendationPanel';
import { AbletonExport } from '../components/AbletonExport';

// ... Interfața Generation ...
interface Generation {
  id: number;
  description: string;
  created_at: string;
}

export default function Home() {
  const [token, setToken] = useState<string | null>(null);
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState<Generation[]>([]);
  const [midiUrl, setMidiUrl] = useState<string | null>(null);
  const [instrument, setInstrument] = useState('full_drums'); // Instrument selector state
  const [musicalKey, setMusicalKey] = useState('C'); // Musical key selector
  const [musicalScale, setMusicalScale] = useState('minor'); // Musical scale selector
  const [suggestions, setSuggestions] = useState<any[]>([]); // AI recommendations

  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    if (savedToken) {
      setToken(savedToken);
      fetchHistory(savedToken);
    }
  }, []);

  const fetchHistory = async (currentToken: string) => {
    try {
      const res = await axios.get('http://localhost:8000/api/history', {
        headers: { Authorization: `Bearer ${currentToken}` }
      });
      setHistory(res.data);
    } catch (e) {
      console.error("Failed to load history");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setMidiUrl(null); // Resetăm playerul
    toast.success('Logged out');
  };

  // Funcție pentru a cere recomandări AI
  const fetchRecommendations = async () => {
    try {
      const res = await axios.post(
        'http://localhost:8000/api/recommendations',
        {
          instrument,
          style: 'trap', // Default style, AI-ul va analiza
          key: musicalKey,
          scale: musicalScale,
          bpm: 120
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setSuggestions(res.data.suggestions || []);
    } catch (e) {
      console.error("Recommendations error:", e);
    }
  };

  const generateMIDI = async () => {
    if (!description) return toast.error('Describe it first!');

    setLoading(true);
    setMidiUrl(null); // Resetăm playerul în timp ce generăm
    const loadingToast = toast.loading('AI is composing...');

    try {
      const response = await axios.post(
        'http://localhost:8000/api/generate/midi',
        null,
        {
          params: {
            description,
            instrument,
            musical_key: musicalKey,
            musical_scale: musicalScale
          },
          responseType: 'blob',
          headers: { Authorization: `Bearer ${token}` }
        }
      );

      // Creăm URL-ul doar pentru Player
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      setMidiUrl(url);

      toast.success('Track ready! Listen or Download.', { id: loadingToast });
      if (token) fetchHistory(token);
      setDescription('');

      // Cerem recomandări AI bazate pe ce tocmai a generat
      fetchRecommendations();
    } catch (error) {
      console.error(error);
      toast.error('Error generating.', { id: loadingToast });
    }
    setLoading(false);
  };

  // Funcție pentru descărcarea MIDI cu nume corect
  const downloadMidi = (blob: Blob, filename: string) => {
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    // Curățăm numele (scoatem caractere ciudate) și adăugăm extensia
    const safeName = filename.replace(/[^a-z0-9]/gi, '_').toLowerCase();
    a.download = `${safeName}.mid`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
  };

  // Funcție pentru PLAY din Istoric
  const playFromHistory = async (gen: Generation) => {
    // 1. Oprim playerul curent dacă există
    setMidiUrl(null);
    const loadingToast = toast.loading('Loading preview...');

    try {
      console.log(`🎵 Fetching MIDI for ID: ${gen.id}`);

      // 2. Cerem fișierul de la backend
      const response = await axios.get(`http://localhost:8000/api/download/${gen.id}`, {
        responseType: 'blob', // Critic: Trebuie să fie blob!
        headers: { Authorization: `Bearer ${token}` }
      });

      console.log("✅ File received via API");

      // 3. Creăm URL-ul pentru Tone.js
      const blob = new Blob([response.data], { type: 'audio/midi' });
      const url = window.URL.createObjectURL(blob);

      // 4. Setăm URL-ul (asta va declanșa useEffect-ul din MusicPlayer)
      setMidiUrl(url);

      toast.success('Preview ready', { id: loadingToast });
    } catch (e) {
      console.error("❌ Play Error:", e);
      toast.error('Could not load audio. File might be missing.', { id: loadingToast });
    }
  };

  // Funcție pentru generarea variațiilor
  const createVariations = async (genId: number) => {
    const loadingToast = toast.loading('Creating variations...');
    try {
      const res = await axios.post(
        `http://localhost:8000/api/variations/${genId}`,
        {},
        { headers: { Authorization: `Bearer ${token}` } }
      );

      toast.success('Variations created!', { id: loadingToast });
      if (token) fetchHistory(token); // Actualizăm lista să le vedem pe toate
    } catch (e) {
      console.error(e);
      toast.error('Could not create variations', { id: loadingToast });
    }
  };

  // Funcție pentru ștergerea unei generări
  const deleteGeneration = async (id: number) => {
    if (!confirm('Are you sure you want to delete this beat?')) return;

    const loadingToast = toast.loading('Deleting...');
    try {
      await axios.delete(`http://localhost:8000/api/history/${id}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      // Actualizăm lista local (fără refresh la pagină)
      setHistory(prev => prev.filter(item => item.id !== id));
      toast.success('Deleted', { id: loadingToast });
    } catch (e) {
      toast.error('Failed to delete', { id: loadingToast });
    }
  };

  return (
    <main className="min-h-screen bg-neutral-950 text-white flex flex-col items-center justify-center p-4">
      <Toaster position="bottom-center" />
      
      <div className="max-w-xl w-full flex flex-col items-center space-y-8">
        
        <div className="text-center space-y-2">
          <h1 className="text-5xl font-bold bg-gradient-to-r from-blue-400 to-purple-500 text-transparent bg-clip-text">
            AIMusicCopilot
          </h1>
          <p className="text-neutral-400">
            {token ? 'Ready to create.' : 'Login to start creating.'}
          </p>
        </div>

        {!token ? (
          <AuthForm onLoginSuccess={(t) => setToken(t)} />
        ) : (
          <div className="w-full bg-neutral-900 p-6 rounded-2xl border border-neutral-800 shadow-xl space-y-4 animate-in fade-in zoom-in duration-300">
            <div className="flex justify-between items-center mb-2">
               <span className="text-xs text-green-400 font-mono">● SYSTEM ONLINE</span>
               <button onClick={handleLogout} className="text-xs text-red-400 hover:text-red-300">Logout</button>
            </div>

            {/* Instrument Selector */}
            <div className="grid grid-cols-4 gap-2 w-full">
              {[
                { id: 'full_drums', label: '🥁 Drums', color: 'bg-blue-600' },
                { id: 'kick', label: '🦶 Kick', color: 'bg-orange-600' },
                { id: 'bass', label: '🎸 Bass', color: 'bg-purple-600' },
                { id: 'melody', label: '🎹 Melody', color: 'bg-pink-600' }
              ].map((inst) => (
                <button
                  key={inst.id}
                  onClick={() => setInstrument(inst.id)}
                  className={`py-2 rounded-lg text-xs font-bold transition-all border ${
                    instrument === inst.id
                      ? `${inst.color} border-transparent text-white shadow-lg scale-105`
                      : 'bg-neutral-800 border-neutral-700 text-neutral-400 hover:bg-neutral-700'
                  }`}
                >
                  {inst.label}
                </button>
              ))}
            </div>

            {/* Musical Key & Scale Selectors */}
            <div className="flex gap-2 w-full">
              {/* Key Selector */}
              <div className="flex-1">
                <label className="text-[10px] text-neutral-500 uppercase tracking-wider mb-1 block">Key</label>
                <select
                  value={musicalKey}
                  onChange={(e) => setMusicalKey(e.target.value)}
                  className="w-full bg-neutral-800 text-white text-sm font-bold py-2 px-3 rounded-lg border border-neutral-700 outline-none focus:border-blue-500 transition-colors"
                >
                  {['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'].map(k => (
                    <option key={k} value={k}>{k}</option>
                  ))}
                </select>
              </div>

              {/* Scale Selector */}
              <div className="flex-[2]">
                <label className="text-[10px] text-neutral-500 uppercase tracking-wider mb-1 block">Scale</label>
                <select
                  value={musicalScale}
                  onChange={(e) => setMusicalScale(e.target.value)}
                  className="w-full bg-neutral-800 text-white text-sm font-bold py-2 px-3 rounded-lg border border-neutral-700 outline-none focus:border-blue-500 transition-colors"
                >
                  <option value="minor">Minor (Sad/Deep)</option>
                  <option value="major">Major (Happy)</option>
                  <option value="dorian">Dorian (Epic)</option>
                  <option value="phrygian">Phrygian (Dark/Trap)</option>
                </select>
              </div>
            </div>

            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Ex: A fast and aggressive techno rumble..."
              className="w-full p-4 bg-neutral-800 border border-neutral-700 rounded-xl focus:ring-2 focus:ring-blue-500 focus:outline-none transition-all"
              onKeyDown={(e) => e.key === 'Enter' && generateMIDI()}
            />
            
            <button
              onClick={generateMIDI}
              disabled={loading}
              className={`w-full py-4 rounded-xl font-bold text-lg transition-all ${
                loading 
                  ? 'bg-neutral-700 cursor-not-allowed' 
                  : 'bg-blue-600 hover:bg-blue-500 active:scale-95'
              }`}
            >
              {loading ? 'Composing...' : 'Generate MIDI 🎵'}
            </button>

            {/* <--- 4. AICI ESTE PLAYERUL */}
            <MusicPlayer midiUrl={midiUrl} />

            {/* MIDI Visualizer */}
            <MidiVisualizer midiUrl={midiUrl} instrument={instrument} />

            {/* Ableton Export */}
            <AbletonExport bpm={128} pattern={{ genre: 'techno' }} />

            {/* AI Recommendations */}
            <RecommendationPanel
              suggestions={suggestions}
              onSelect={(s) => {
                setInstrument(s.instrument);
                setDescription(s.prompt);
                setSuggestions([]);
                toast('Settings applied! Press Generate.', { icon: '✨' });
              }}
            />

          </div>
        )}

        {/* Istoricul */}
        {token && (
          <div className="w-full mt-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <h3 className="text-neutral-500 text-xs font-bold mb-3 uppercase tracking-wider text-center">
              Library ({history.length})
            </h3>

            {/* CONTAINER SCROLLABIL ȘI LIMITAT CA LĂȚIME */}
            <div className="max-h-[400px] overflow-y-auto pr-2 space-y-3 custom-scrollbar">

              {history.length === 0 && (
                <p className="text-center text-neutral-600 text-sm py-4">No beats yet. Start creating!</p>
              )}

              {history.map((gen) => (
                <div key={gen.id} className="group relative bg-neutral-900/80 border border-neutral-800 rounded-lg p-3 hover:border-neutral-700 transition-all">

                  {/* Header Compact */}
                  <div className="flex justify-between items-start mb-3 pr-6">
                    <div>
                      <span className="text-sm font-medium text-neutral-200 block truncate max-w-[280px]">
                        {gen.description}
                      </span>
                      <span className="text-[10px] text-neutral-500 uppercase">
                        {new Date(gen.created_at).toLocaleDateString()} • MIDI
                      </span>
                    </div>
                  </div>

                  {/* Buton de Ștergere (Apare doar la Hover sau e discret) */}
                  <button
                    onClick={(e) => { e.stopPropagation(); deleteGeneration(gen.id); }}
                    className="absolute top-3 right-3 text-neutral-600 hover:text-red-500 transition-colors p-1"
                    title="Delete Track"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-4 h-4">
                      <path strokeLinecap="round" strokeLinejoin="round" d="m14.74 9-.346 9m-4.788 0L9.26 9m9.968-3.21c.342.052.682.107 1.022.166m-1.022-.165L18.16 19.673a2.25 2.25 0 0 1-2.244 2.077H8.084a2.25 2.25 0 0 1-2.244-2.077L4.772 5.79m14.456 0a48.108 48.108 0 0 0-3.478-.397m-12 .562c.34-.059.68-.114 1.022-.165m0 0a48.11 48.11 0 0 1 3.478-.397m7.5 0v-.916c0-1.18-.91-2.164-2.09-2.201a51.964 51.964 0 0 0-3.32 0c-1.18.037-2.09 1.022-2.09 2.201v.916m7.5 0a48.667 48.667 0 0 0-7.5 0" />
                    </svg>
                  </button>

                  {/* Bara de Acțiuni (Butoane mai mici) */}
                  <div className="grid grid-cols-4 gap-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation(); // Previne click-ul pe tot cardul
                        playFromHistory(gen);
                      }}
                      className="bg-neutral-800 hover:bg-green-900/30 text-neutral-300 hover:text-green-400 py-1.5 rounded text-[10px] font-bold transition-colors flex items-center justify-center gap-1 border border-transparent hover:border-green-800/50"
                    >
                      ▶ Play
                    </button>

                    <button
                      onClick={async () => {
                        try {
                          const res = await axios.get(`http://localhost:8000/api/download/${gen.id}`, {
                            responseType: 'blob',
                            headers: { Authorization: `Bearer ${token}` }
                          });
                          downloadMidi(res.data, gen.description);
                        } catch (e) {
                          toast.error('Download failed');
                        }
                      }}
                      className="bg-neutral-800 hover:bg-neutral-700 text-neutral-300 py-1.5 rounded text-[10px] font-bold transition-colors border border-neutral-800"
                    >
                      ⬇ MIDI
                    </button>

                    <button
                      onClick={async () => {
                        const loading = toast.loading("Packing project...");
                        try {
                          const res = await axios.get(`http://localhost:8000/api/download/project/${gen.id}`, {
                            responseType: 'blob',
                            headers: { Authorization: `Bearer ${token}` }
                          });

                          const url = window.URL.createObjectURL(new Blob([res.data]));
                          const a = document.createElement('a');
                          a.href = url;
                          a.download = `AIMusic_Project_${gen.id}.zip`;
                          document.body.appendChild(a);
                          a.click();
                          document.body.removeChild(a);
                          window.URL.revokeObjectURL(url);

                          toast.success("Project Downloaded!", { id: loading });
                        } catch (e) {
                          toast.error('Download failed', { id: loading });
                        }
                      }}
                      className="bg-neutral-800 hover:bg-blue-900/30 text-neutral-300 hover:text-blue-400 py-1.5 rounded text-[10px] font-bold transition-colors border border-transparent hover:border-blue-800/50"
                    >
                      📦 ZIP
                    </button>

                    <button
                      onClick={() => createVariations(gen.id)}
                      className="bg-neutral-800 hover:bg-purple-900/30 text-neutral-300 hover:text-purple-400 py-1.5 rounded text-[10px] font-bold transition-colors border border-transparent hover:border-purple-800/50"
                    >
                      ⚡ Remix
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Un mic fade out jos ca să arate că e scrollable (opțional) */}
            <div className="h-4 bg-gradient-to-t from-neutral-950 to-transparent -mt-4 pointer-events-none relative z-10"></div>
          </div>
        )}
      </div>
    </main>
  );
}