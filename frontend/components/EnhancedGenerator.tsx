import React, { useState, useRef, useEffect } from 'react';
import * as Tone from 'tone';
import { Midi } from '@tonejs/midi';
import {
    Music, Play, Square, Download, Activity,
    Settings2, Sliders, Drum, Guitar, Piano, Mic2, Info,
    Upload, CheckCircle2, X
} from 'lucide-react';

// --- 1. CONFIGURARE STILURI SI OPTIUNI (Din Planul Tau) ---

// --- 1. CONFIGURARE STILURI SI OPTIUNI (Din Planul Tau) ---
// Import styles from source of truth
import { MUSIC_STYLES, getStylesByCategory } from '../constants/musicStyles';
import MidiVisualizer from './MidiVisualizer';
import ArrangementSequencer from './ArrangementSequencer';

const GENERATION_OPTIONS = {
    drums: {
        icon: <Drum size={20} />,
        label: 'Drums',
        subOptions: [
            { id: 'chorus', label: 'Chorus (Energy)' },
            { id: 'verse', label: 'Verse' },
            { id: 'intro', label: 'Intro' },
            { id: 'drop', label: 'Drop (Build-up)' },
            { id: 'full_kit', label: 'Full Groove' },
            { id: 'kick_only', label: 'Kick Only' },
            { id: 'hat_pattern', label: 'Hats' }
        ]
    },
    bass: {
        icon: <Guitar size={20} />,
        label: 'Bass',
        subOptions: [
            { id: '808', label: '808 Bass' },
            { id: 'sub_bass', label: 'Sub Bass' },
            { id: 'groove_bass', label: 'Groove' }
        ]
    },
    melody: {
        icon: <Piano size={20} />,
        label: 'Melody',
        subOptions: [
            { id: 'chords', label: 'Chords' }, // NOU: Music Theory
            { id: 'lead', label: 'Lead Melody' },
            { id: 'arp', label: 'Arpeggio' },
            { id: 'pad', label: 'Atmosphere' }
        ]
    }
};

const COMPLEXITY_LEVELS = [
    { id: 'beginner', label: 'Simple', val: 0.3 },
    { id: 'intermediate', label: 'Medium', val: 0.6 },
    { id: 'expert', label: 'Complex', val: 1.0 }
];

const MUSICAL_KEYS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
const MUSICAL_SCALES = [
    { id: 'major', label: 'Major' },
    { id: 'minor', label: 'Minor (Natural)' },
    { id: 'harmonic_minor', label: 'Harmonic Minor' },
    { id: 'melodic_minor', label: 'Melodic Minor' },
    { id: 'dorian', label: 'Dorian' },
    { id: 'phrygian', label: 'Phrygian' },
    { id: 'lydian', label: 'Lydian' },
    { id: 'mixolydian', label: 'Mixolydian' },
    { id: 'locrian', label: 'Locrian' }
];

// --- 2. COMPONENTA PRINCIPALA ---

export default function EnhancedGenerator() {
    // State pentru UI
    const [style, setStyle] = useState('techno');
    const [instrument, setInstrument] = useState('drums');
    const [subOption, setSubOption] = useState('full_kit'); // Default nou
    const [complexity, setComplexity] = useState('intermediate');
    const [description, setDescription] = useState('');

    // Mode State
    const [appMode, setAppMode] = useState<'loop' | 'arrangement'>('loop');

    // Music Theory State
    const [musicalKey, setMusicalKey] = useState('C');
    const [musicalScale, setMusicalScale] = useState('minor');

    // Context Awareness State
    const [analysisResult, setAnalysisResult] = useState<any>(null);

    // State pentru Playback & Vizualizare
    const [isPlaying, setIsPlaying] = useState(false);
    const [isGenerating, setIsGenerating] = useState(false);
    const [midiUrl, setMidiUrl] = useState<string | null>(null);

    // REFS (Fixul tau pentru Vercel inclus aici)
    const synthsRef = useRef<Tone.PolySynth[]>([]);
    const partsRef = useRef<Tone.Part[]>([]);
    const midiDataRef = useRef<Midi | null>(null);
    const animationFrameRef = useRef<number | null>(null); // ✅ CORECT
    // const canvasRef = useRef<HTMLCanvasElement | null>(null); // Removed

    // --- UPLOAD HANDLER ---
    const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        try {
            const formData = new FormData();
            formData.append('file', file);

            const token = localStorage.getItem('token');
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/analyze/midi`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData
            });

            if (!response.ok) throw new Error('Analysis failed');

            const result = await response.json();
            console.log("Analysis Result:", result);
            setAnalysisResult(result);

            // Auto-Apply Results
            if (result.bars && result.bars.length > 0) {
                // Try to guess key from first chord
                const firstChord = result.bars[0].chord;
                const parts = firstChord.split(' ');
                if (parts.length >= 2) {
                    const key = parts[0];
                    const type = parts[1];
                    if (MUSICAL_KEYS.includes(key)) setMusicalKey(key);
                    if (type === 'min') setMusicalScale('minor');
                    if (type === 'maj') setMusicalScale('major');
                }
            }

        } catch (error) {
            console.error("Upload Error:", error);
            alert("Failed to analyze MIDI file.");
        }
    };

    // --- LOGICA DE GENERARE ---
    const handleGenerate = async () => {
        // Fix: Start AudioContext immediately on user gesture
        await Tone.start();

        setIsGenerating(true);
        stopPlayback();

        // 1. Recuperăm Token-ul (Biletul de intrare)
        const token = localStorage.getItem('token'); // sau 'access_token'

        if (!token) {
            alert("You are not authenticated! Please login again.");
            setIsGenerating(false);
            return;
        }

        try {
            // Map complexity to advanced parameters
            let structure = 'AABB';
            let passing_tones = false;
            let ghost_notes = true; // Default true for most? Or map carefully.

            if (complexity === 'beginner') {
                structure = 'AABB';
                ghost_notes = false;
            } else if (complexity === 'intermediate') {
                structure = 'AABA';
                ghost_notes = true;
            } else if (complexity === 'expert') {
                structure = 'AABA';
                passing_tones = true;
                ghost_notes = true;
            }

            const payload: any = {
                description: description || `${style} ${instrument}`,
                style: style,
                instrument: instrument,
                sub_option: subOption,
                complexity: complexity,
                musical_key: musicalKey,
                musical_scale: musicalScale,
                // Advanced V2 Params
                structure: structure,
                passing_tones: passing_tones,
                ghost_notes: ghost_notes
            };

            // [NEW] Inject smart BPM default based on style
            const selectedStyleConfig = MUSIC_STYLES.find(s => s.id === style);
            if (selectedStyleConfig) {
                // @ts-ignore
                payload.bpm = selectedStyleConfig.bpm;
            }

            // [NEW PHASE 7] Context Overrides
            if (analysisResult) {
                payload.bpm = analysisResult.bpm; // Override BPM
                // @ts-ignore
                payload.context_chords = analysisResult.bars; // Send chords to backend
            }

            console.log("🚀 Sending to backend:", payload);

            const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/generate/midi`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}` // ✅ AICI ESTE CHEIA FIX-ULUI
                },
                body: JSON.stringify(payload),
            });

            if (response.status === 401) {
                throw new Error("Session expired. Please refresh and login again.");
            }

            if (!response.ok) throw new Error('Generation failed');

            const data = await response.json();
            console.log("✅ Received:", data);

            if (data.url) {
                const fullUrl = data.url.startsWith('http')
                    ? data.url
                    : `${process.env.NEXT_PUBLIC_API_URL}${data.url}`;

                setMidiUrl(fullUrl);
                await loadMidi(fullUrl);
            }

        } catch (error) {
            console.error("Eroare:", error);
            alert(error instanceof Error ? error.message : "Something went wrong.");
        } finally {
            setIsGenerating(false);
        }
    };

    // --- LOGICA AUDIO (Tone.js) ---
    const loadMidi = async (url: string) => {
        const midi = await Midi.fromUrl(url);
        midiDataRef.current = midi;

        // Curatam vechiul sunet
        partsRef.current.forEach(p => p.dispose());
        synthsRef.current.forEach(s => s.dispose());
        partsRef.current = [];
        synthsRef.current = [];

        // Pregatim instrumentele
        const now = Tone.now() + 0.5;

        midi.tracks.forEach((track) => {
            // Alegem sintetizator in functie de instrument
            let synth;
            if (instrument === 'drums') {
                synth = new Tone.PolySynth(Tone.MembraneSynth).toDestination();
            } else {
                synth = new Tone.PolySynth(Tone.Synth, {
                    oscillator: { type: "triangle" },
                    envelope: { attack: 0.02, decay: 0.1, sustain: 0.3, release: 1 }
                }).toDestination();
            }

            synthsRef.current.push(synth);

            // Cream Partitura
            const part = new Tone.Part((time, note) => {
                synth.triggerAttackRelease(note.name, note.duration, time, note.velocity);
            }, track.notes.map(n => ({
                time: n.time,
                name: n.name,
                duration: n.duration,
                velocity: n.velocity
            })));

            part.start(0);
            partsRef.current.push(part);
        });

        Tone.Transport.start();
        setIsPlaying(true);
        Tone.Transport.start();
        setIsPlaying(true);
        // drawVisualizer(); // Handled by component
    };

    const stopPlayback = () => {
        Tone.Transport.stop();
        Tone.Transport.cancel();
        // Fix: Ensure non-negative time to prevent RangeError with tiny float values
        const safeTime = Math.max(0, Tone.now());
        partsRef.current.forEach(p => p.stop(safeTime));
        setIsPlaying(false);
        if (animationFrameRef.current) {
            cancelAnimationFrame(animationFrameRef.current);
        }
    };

    const togglePlay = async () => {
        await Tone.start();
        if (isPlaying) {
            stopPlayback();
        } else {
            Tone.Transport.start();
            setIsPlaying(true);
            Tone.Transport.start();
            setIsPlaying(true);
            // drawVisualizer(); // Handled by component
        }
    };

    // --- LOGICA VIZUALIZARE (MidiVisualizer Component handles this now) ---
    // const drawVisualizer = () => { ... } // Removed
    // Effects simplified
    useEffect(() => {
        // Just sync playing state if needed or ensure Tone is happy
    }, []);

    // --- INTERFATA (JSX) ---
    return (
        <div className="min-h-screen bg-gray-900 text-white p-4 md:p-8">
            <div className="max-w-4xl mx-auto space-y-8">

                {/* HEADER */}
                {/* HEADER */}
                <div className="text-center space-y-2">
                    <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-purple-500">
                        amc - AI Music Co-pilot v2
                    </h1>
                    <p className="text-gray-400">Professional MIDI & Audio Generation</p>
                    <div className="flex justify-center gap-4 mt-4">
                        <button
                            onClick={() => setAppMode('loop')}
                            className={`px-6 py-2 rounded-full font-bold text-sm transition-all ${appMode === 'loop'
                                ? 'bg-blue-600 text-white shadow-lg'
                                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'}`}
                        >
                            Loop Generator
                        </button>
                        <button
                            onClick={() => setAppMode('arrangement')}
                            className={`px-6 py-2 rounded-full font-bold text-sm transition-all ${appMode === 'arrangement'
                                ? 'bg-purple-600 text-white shadow-lg'
                                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'}`}
                        >
                            Song Arranger
                        </button>
                    </div>
                </div>

                {appMode === 'arrangement' ? (
                    <div className="animate-in fade-in zoom-in duration-300">
                        <ArrangementSequencer />
                    </div>
                ) : (
                    <>
                    /* MAIN CONTROLS CARD */
                        <div className="bg-gray-800 rounded-2xl p-6 shadow-xl border border-gray-700 animate-in fade-in slide-in-from-bottom-4 duration-300">

                            {/* 1. SELECTARE STIL */}
                            <div className="mb-8">
                                <label className="text-sm font-semibold text-gray-400 mb-3 block">GENRE</label>
                                <div className="flex flex-wrap gap-2">
                                    {['Electronic', 'Pop/Rock', 'Urban', 'Jazz/Soul', 'World', 'Hard', 'Score'].map(cat => (
                                        <div key={cat} className="w-full mb-2">
                                            <span className="text-xs uppercase tracking-widest text-gray-500 font-bold ml-1 block mb-2">{cat}</span>
                                            <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2">
                                                {MUSIC_STYLES.filter(s => s.category === cat).map((s) => (
                                                    <button
                                                        key={s.id}
                                                        onClick={() => setStyle(s.id)}
                                                        className={`p-2 rounded-lg text-xs font-medium transition-all ${style === s.id
                                                            ? 'bg-blue-600 text-white shadow-lg scale-105'
                                                            : 'bg-gray-700/50 text-gray-300 hover:bg-gray-600'
                                                            }`}
                                                    >
                                                        {s.label}
                                                    </button>
                                                ))}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* STYLE HINT BADGE */}
                            {style === 'cinematic' && (
                                <div className="mt-4 p-3 bg-indigo-900/50 border border-indigo-500/30 rounded-lg flex items-center gap-2">
                                    <span className="text-xl">🌌</span>
                                    <span className="text-sm text-indigo-200">
                                        <strong>Atmospheric Mode:</strong> Evolving pads & sparse structures enabled.
                                    </span>
                                </div>
                            )}
                            {style === 'lofi' && (
                                <div className="mt-4 p-3 bg-amber-900/40 border border-amber-500/30 rounded-lg flex items-center gap-2">
                                    <span className="text-xl">☕</span>
                                    <span className="text-sm text-amber-200">
                                        <strong>Chill Mode:</strong> Drunk drummer swing & vinyl crackle velocity.
                                    </span>
                                </div>
                            )}


                            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">

                                {/* 2. INSTRUMENT & SUB-OPTIONS */}
                                <div>
                                    <label className="text-sm font-semibold text-gray-400 mb-3 block">INSTRUMENT</label>
                                    <div className="flex gap-4 mb-4">
                                        {Object.entries(GENERATION_OPTIONS).map(([key, data]) => (
                                            <button
                                                key={key}
                                                onClick={() => {
                                                    setInstrument(key);
                                                    setSubOption(data.subOptions[0].id); // Reset sub-option
                                                }}
                                                className={`flex-1 flex flex-col items-center gap-2 p-3 rounded-xl border-2 transition-all ${instrument === key
                                                    ? 'border-purple-500 bg-purple-500/20 text-white'
                                                    : 'border-gray-600 bg-gray-700/50 text-gray-400 hover:border-gray-500'
                                                    }`}
                                            >
                                                {data.icon}
                                                <span className="text-xs font-bold">{data.label}</span>
                                            </button>
                                        ))}
                                    </div>

                                    {/* SUB OPTIONS PILLS */}
                                    <div className="flex flex-wrap gap-2">
                                        {GENERATION_OPTIONS[instrument as keyof typeof GENERATION_OPTIONS].subOptions.map((sub) => (
                                            <button
                                                key={sub.id}
                                                onClick={() => setSubOption(sub.id)}
                                                className={`px-3 py-1 rounded-full text-xs font-medium transition-colors ${subOption === sub.id
                                                    ? 'bg-purple-500 text-white'
                                                    : 'bg-gray-700 text-gray-400 hover:bg-gray-600'
                                                    }`}
                                            >
                                                {sub.label}
                                            </button>
                                        ))}
                                    </div>
                                </div>

                                <div className="space-y-6">
                                    <div>
                                        <label className="text-sm font-semibold text-gray-400 mb-3 block flex items-center gap-2">
                                            <Activity size={16} /> COMPLEXITY
                                        </label>
                                        <div className="flex justify-between bg-gray-700 rounded-lg p-1">
                                            {COMPLEXITY_LEVELS.map((level) => (
                                                <button
                                                    key={level.id}
                                                    onClick={() => setComplexity(level.id)}
                                                    className={`flex-1 py-1 rounded text-xs transition-all ${complexity === level.id
                                                        ? 'bg-blue-500 text-white shadow'
                                                        : 'text-gray-400 hover:text-white'
                                                        }`}
                                                >
                                                    {level.label}
                                                </button>
                                            ))}
                                        </div>
                                    </div>

                                    {/* KEY & SCALE CONTROLS */}
                                    <div>
                                        <label className="text-sm font-semibold text-gray-400 mb-3 block flex items-center gap-2">
                                            <Activity size={16} /> KEY & SCALE
                                        </label>
                                        <div className="flex gap-2">
                                            <select
                                                value={musicalKey}
                                                onChange={(e) => setMusicalKey(e.target.value)}
                                                className="bg-gray-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500 border border-transparent"
                                            >
                                                {MUSICAL_KEYS.map(k => <option key={k} value={k}>{k}</option>)}
                                            </select>
                                            <select
                                                value={musicalScale}
                                                onChange={(e) => setMusicalScale(e.target.value)}
                                                className="flex-1 bg-gray-700 text-white rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-blue-500 border border-transparent"
                                            >
                                                {MUSICAL_SCALES.map(s => <option key={s.id} value={s.id}>{s.label}</option>)}
                                            </select>
                                        </div>
                                    </div>

                                    {/* CONTEXT AWARENESS & UPLOAD */}
                                    <div className="bg-gray-700/30 rounded-xl p-4 border border-gray-600">
                                        <label className="text-sm font-semibold text-gray-400 mb-3 flex items-center gap-2">
                                            <Mic2 size={16} /> CONTEXT REFERENCE (Remix Mode)
                                        </label>

                                        {!analysisResult ? (
                                            <div className="relative border-2 border-dashed border-gray-600 rounded-lg p-6 text-center hover:border-blue-500 hover:bg-gray-700/50 transition-all group">
                                                <input
                                                    type="file"
                                                    accept=".mid,.midi"
                                                    onChange={handleFileUpload}
                                                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                                />
                                                <div className="space-y-2 pointer-events-none">
                                                    <div className="flex justify-center text-gray-400 group-hover:text-blue-400">
                                                        <Upload size={32} />
                                                    </div>
                                                    <p className="text-xs text-gray-300 font-medium">Drop MIDI here to analyze</p>
                                                    <p className="text-[10px] text-gray-500">Detects Key, BPM & Chords</p>
                                                </div>
                                            </div>
                                        ) : (
                                            <div className="space-y-3 animate-in fade-in slide-in-from-top-2">
                                                <div className="flex items-center justify-between bg-green-900/40 border border-green-500/30 p-3 rounded-lg">
                                                    <div className="flex items-center gap-3">
                                                        <div className="p-2 bg-green-500/20 rounded-full text-green-400">
                                                            <CheckCircle2 size={18} />
                                                        </div>
                                                        <div>
                                                            <p className="text-sm font-bold text-green-100">Analysis Complete</p>
                                                            <p className="text-xs text-green-300">
                                                                {analysisResult.bpm} BPM • {analysisResult.bars.length} Bars Detected
                                                            </p>
                                                        </div>
                                                    </div>
                                                    <button
                                                        onClick={() => setAnalysisResult(null)}
                                                        className="p-1 hover:text-white text-gray-400"
                                                        title="Clear Context"
                                                    >
                                                        <X size={16} />
                                                    </button>
                                                </div>

                                                <div className="flex gap-2">
                                                    <div className="flex-1 bg-gray-800 p-2 rounded text-xs text-center border border-gray-600">
                                                        <span className="block text-gray-500 text-[10px] uppercase">Detected Key</span>
                                                        <span className="font-mono font-bold text-blue-300">{musicalKey} {musicalScale}</span>
                                                    </div>
                                                    <div className="flex-1 bg-gray-800 p-2 rounded text-xs text-center border border-gray-600">
                                                        <span className="block text-gray-500 text-[10px] uppercase">Locked</span>
                                                        <span className="font-mono font-bold text-purple-300">Chord Stream</span>
                                                    </div>
                                                </div>
                                            </div>
                                        )}
                                    </div>

                                    <div>
                                        <label className="text-sm font-semibold text-gray-400 mb-2 block">STYLE DESCRIPTION (Optional)</label>
                                        <input
                                            type="text"
                                            placeholder="ex: dark, happy, fast..."
                                            value={description}
                                            onChange={(e) => setDescription(e.target.value)}
                                            className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-blue-500"
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* GENERATE BUTTON */}
                            <button
                                onClick={handleGenerate}
                                disabled={isGenerating}
                                className={`w-full mt-8 py-4 rounded-xl font-bold text-lg flex items-center justify-center gap-3 transition-all ${isGenerating
                                    ? 'bg-gray-600 cursor-not-allowed'
                                    : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:scale-[1.02] shadow-lg shadow-purple-500/30'
                                    }`}
                            >
                                {isGenerating ? (
                                    <>Generating...</>
                                ) : (
                                    <>
                                        <Music size={24} /> GENERATE AUDIO
                                    </>
                                )}
                            </button>
                        </div>

                        {/* VISUALIZER & PLAYER */}
                        {midiUrl && (
                            <div className="bg-gray-800 rounded-2xl p-6 border border-gray-700 animate-fade-in">

                                {/* METADATA ROW */}
                                <div className="flex flex-wrap justify-center items-center gap-4 mb-6 bg-black/30 p-3 rounded-xl border border-white/10 backdrop-blur-sm">
                                    <div className="flex items-center gap-2">
                                        <span className="text-gray-500 text-xs uppercase font-bold tracking-wider">Key</span>
                                        <span className="text-cyan-400 font-mono font-bold text-lg">
                                            {musicalKey} {musicalScale === 'minor' ? 'Minor' : MUSICAL_SCALES.find(s => s.id === musicalScale)?.label}
                                        </span>
                                    </div>
                                    <div className="w-px h-8 bg-white/10 hidden md:block"></div>
                                    <div className="flex items-center gap-2">
                                        <span className="text-gray-500 text-xs uppercase font-bold tracking-wider">BPM</span>
                                        <span className="text-yellow-400 font-mono font-bold text-lg">
                                            {MUSIC_STYLES.find(s => s.id === style)?.bpm || 120}
                                        </span>
                                    </div>
                                    <div className="w-px h-8 bg-white/10 hidden md:block"></div>
                                    <div className="flex items-center gap-2 relative group cursor-help">
                                        <span className="text-gray-500 text-xs uppercase font-bold tracking-wider">Style</span>
                                        <span className="text-white font-bold text-lg flex items-center gap-2">
                                            {MUSIC_STYLES.find(s => s.id === style)?.label || style}
                                            <Info size={14} className="text-blue-400 opacity-50 group-hover:opacity-100 transition-opacity" />
                                        </span>

                                        {/* Glass Box Tooltip */}
                                        <div className="absolute bottom-full mb-2 left-1/2 -translate-x-1/2 w-48 p-3 bg-gray-900/90 backdrop-blur-md border border-gray-700 rounded-lg shadow-xl opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none text-xs text-center z-20">
                                            <strong className="text-blue-400 block mb-1">Rhythm Engine v2.1</strong>
                                            Syncopation & Pickups Active 🥁
                                            <div className="absolute top-full left-1/2 -translate-x-1/2 border-8 border-transparent border-t-gray-900/90"></div>
                                        </div>
                                    </div>
                                </div>

                                <div className="mb-4">
                                    <MidiVisualizer
                                        midiUrl={midiUrl}
                                        instrument={instrument}
                                        height={200}
                                        musicalKey={musicalKey}
                                        musicalScale={musicalScale}
                                    />
                                </div>

                                <div className="flex justify-center gap-4">
                                    <button
                                        onClick={togglePlay}
                                        className="w-16 h-16 rounded-full bg-white text-black flex items-center justify-center hover:scale-110 transition-transform"
                                    >
                                        {isPlaying ? <Square fill="black" /> : <Play fill="black" />}
                                    </button>

                                    <a
                                        href={midiUrl}
                                        download
                                        className="flex items-center gap-2 px-6 py-2 bg-gray-700 rounded-full hover:bg-gray-600 transition-colors"
                                    >
                                        <Download size={20} /> Download MIDI
                                    </a>
                                </div>
                            </div>
                        )}
                    </>
                )}

            </div>

        </div>
    );
}