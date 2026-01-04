import React, { useState, useRef, useEffect } from 'react';
import * as Tone from 'tone';
import { Midi } from '@tonejs/midi';
import {
    Music, Play, Square, Download, Activity,
    Settings2, Sliders, Drum, Guitar, Piano, Mic2
} from 'lucide-react';

// --- 1. CONFIGURARE STILURI SI OPTIUNI (Din Planul Tau) ---

// --- 1. CONFIGURARE STILURI SI OPTIUNI (Din Planul Tau) ---
// Import styles from source of truth
import { MUSIC_STYLES, getStylesByCategory } from '../constants/musicStyles';

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

// --- 2. COMPONENTA PRINCIPALA ---

export default function EnhancedGenerator() {
    // State pentru UI
    const [style, setStyle] = useState('techno');
    const [instrument, setInstrument] = useState('drums');
    const [subOption, setSubOption] = useState('full_kit'); // Default nou
    const [complexity, setComplexity] = useState('intermediate');
    const [description, setDescription] = useState('');

    // State pentru Playback & Vizualizare
    const [isPlaying, setIsPlaying] = useState(false);
    const [isGenerating, setIsGenerating] = useState(false);
    const [midiUrl, setMidiUrl] = useState<string | null>(null);

    // REFS (Fixul tau pentru Vercel inclus aici)
    const synthsRef = useRef<Tone.PolySynth[]>([]);
    const partsRef = useRef<Tone.Part[]>([]);
    const midiDataRef = useRef<Midi | null>(null);
    const animationFrameRef = useRef<number | null>(null); // ✅ CORECT
    const canvasRef = useRef<HTMLCanvasElement | null>(null); // ✅ CORECT

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

            const payload = {
                description: description || `${style} ${instrument}`,
                style: style,
                instrument: instrument,
                sub_option: subOption,
                complexity: complexity,
                musical_key: 'C',
                musical_scale: 'minor',
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
        drawVisualizer(); // Pornim desenul
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
            drawVisualizer();
        }
    };

    // --- LOGICA VIZUALIZARE (Canvas) ---
    const drawVisualizer = () => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        const draw = () => {
            ctx.fillStyle = 'rgba(17, 24, 39, 0.2)'; // Fade effect
            ctx.fillRect(0, 0, canvas.width, canvas.height);

            if (midiDataRef.current) {
                // Vizualizare simpla bazata pe timp
                const time = Tone.Transport.seconds;
                const notes = midiDataRef.current.tracks[0]?.notes || [];

                notes.forEach(note => {
                    if (time >= note.time && time < note.time + note.duration) {
                        const x = (note.midi % 12) * (canvas.width / 12);
                        const y = canvas.height - (note.midi / 127) * canvas.height;

                        // Velocity-based opacity (Visualizer Update)
                        // User request: velocity < 60 (approx 0.47 in 0-1) -> alpha 0.5
                        const vel127 = note.velocity * 127;
                        ctx.globalAlpha = vel127 < 60 ? 0.5 : 1.0;

                        ctx.fillStyle = instrument === 'drums'
                            ? `rgb(16, 185, 129)`
                            : `rgb(139, 92, 246)`;

                        ctx.beginPath();
                        ctx.arc(x, y, 20, 0, Math.PI * 2);
                        ctx.fill();

                        // Reset alpha
                        ctx.globalAlpha = 1.0;
                    }
                });
            }
            animationFrameRef.current = requestAnimationFrame(draw);
        };
        draw();
    };

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
                </div>

                {/* MAIN CONTROLS CARD */}
                <div className="bg-gray-800 rounded-2xl p-6 shadow-xl border border-gray-700">

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
                        <canvas
                            ref={canvasRef}
                            width={800}
                            height={200}
                            className="w-full h-32 bg-gray-900 rounded-lg mb-4 border border-gray-800"
                        />

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

            </div>

        </div>
    );
}