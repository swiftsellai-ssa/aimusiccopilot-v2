import React, { useState } from 'react';
import { DragDropContext, Droppable, Draggable, DropResult } from '@hello-pangea/dnd';
import { Plus, X, Music, Play, Box } from 'lucide-react';
import { MUSIC_STYLES } from '../constants/musicStyles';

// Types
interface Block {
    id: string; // unique
    type: string; // intro, verse, chorus...
    bars: number;
    color: string;
}

const BLOCK_TYPES = [
    { type: 'intro', label: 'Intro', defBars: 4, color: 'bg-emerald-600' },
    { type: 'verse', label: 'Verse', defBars: 8, color: 'bg-blue-600' },
    { type: 'chorus', label: 'Chorus', defBars: 8, color: 'bg-purple-600' },
    { type: 'bridge', label: 'Bridge', defBars: 4, color: 'bg-orange-600' },
    { type: 'outro', label: 'Outro', defBars: 4, color: 'bg-red-600' }
];

export default function ArrangementSequencer() {
    // State
    const [blocks, setBlocks] = useState<Block[]>([]);
    const [style, setStyle] = useState('techno');
    const [bpm, setBpm] = useState(124);
    const [isGenerating, setIsGenerating] = useState(false);
    const [downloadUrl, setDownloadUrl] = useState<string | null>(null);

    // DND Handler
    const onDragEnd = (result: DropResult) => {
        if (!result.destination) return;

        const items = Array.from(blocks);
        const [reorderedItem] = items.splice(result.source.index, 1);
        items.splice(result.destination.index, 0, reorderedItem);

        setBlocks(items);
    };

    // Actions
    const addBlock = (typeObj: typeof BLOCK_TYPES[0]) => {
        const newBlock: Block = {
            id: `${typeObj.type}-${Date.now()}`,
            type: typeObj.type,
            bars: typeObj.defBars,
            color: typeObj.color
        };
        setBlocks([...blocks, newBlock]);
    };

    const removeBlock = (id: string) => {
        setBlocks(blocks.filter(b => b.id !== id));
    };

    const updateBars = (id: string, newBars: number) => {
        setBlocks(blocks.map(b => b.id === id ? { ...b, bars: newBars } : b));
    };

    const handleGenerate = async () => {
        if (blocks.length === 0) return alert("Add some blocks first!");

        setIsGenerating(true);
        setDownloadUrl(null);

        try {
            const token = localStorage.getItem('token');
            const payload = {
                name: "My Arrangement",
                style: style,
                instrument: "full_kit",
                bpm: bpm,
                blocks: blocks.map(b => ({ type: b.type, bars: b.bars }))
            };

            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/generate/arrangement/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (!res.ok) throw new Error("Generation failed");

            const data = await res.json();
            setDownloadUrl(data.url.startsWith('http') ? data.url : `${process.env.NEXT_PUBLIC_API_URL}${data.url}`);

        } catch (e) {
            console.error(e);
            alert("Failed to generate arrangement");
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <div className="w-full bg-gray-800 rounded-2xl p-6 border border-gray-700">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Box className="text-purple-400" /> Arrangement Builder
            </h2>

            {/* Config Row */}
            <div className="flex gap-4 mb-6 bg-gray-900/50 p-4 rounded-xl">
                <div>
                    <label className="text-xs text-gray-400 font-bold block mb-1">STYLE</label>
                    <select value={style} onChange={e => setStyle(e.target.value)} className="bg-gray-700 rounded px-2 py-1 text-sm">
                        {/* Simplified list or import functionality */}
                        <option value="techno">Techno</option>
                        <option value="house">House</option>
                        <option value="hip_hop">Hip Hop</option>
                        <option value="jazz">Jazz</option>
                    </select>
                </div>
                <div>
                    <label className="text-xs text-gray-400 font-bold block mb-1">BPM</label>
                    <input
                        type="number"
                        value={bpm}
                        onChange={e => setBpm(Number(e.target.value))}
                        className="bg-gray-700 rounded px-2 py-1 text-sm w-16"
                    />
                </div>
            </div>

            {/* Palette */}
            <div className="flex flex-wrap gap-2 mb-6">
                {BLOCK_TYPES.map(bt => (
                    <button
                        key={bt.type}
                        onClick={() => addBlock(bt)}
                        className={`px-3 py-2 rounded-lg text-xs font-bold uppercase hover:scale-105 transition-transform ${bt.color}`}
                    >
                        + {bt.label}
                    </button>
                ))}
            </div>

            {/* Timeline (Drag Area) */}
            <DragDropContext onDragEnd={onDragEnd}>
                <Droppable droppableId="timeline" direction="horizontal">
                    {(provided) => (
                        <div
                            {...provided.droppableProps}
                            ref={provided.innerRef}
                            className="flex gap-2 overflow-x-auto min-h-[120px] bg-black/40 p-4 rounded-xl items-center mb-6 border border-dashed border-gray-600"
                        >
                            {blocks.length === 0 && (
                                <span className="text-gray-500 w-full text-center italic">Drag blocks here or click buttons above</span>
                            )}

                            {blocks.map((block, index) => (
                                <Draggable key={block.id} draggableId={block.id} index={index}>
                                    {(provided) => (
                                        <div
                                            ref={provided.innerRef}
                                            {...provided.draggableProps}
                                            {...provided.dragHandleProps}
                                            className={`flex-shrink-0 w-32 h-24 rounded-xl p-3 relative group ${block.color} shadow-lg`}
                                        >
                                            <div className="flex justify-between items-start mb-2">
                                                <span className="font-bold text-sm uppercase">{block.type}</span>
                                                <button onClick={() => removeBlock(block.id)} className="text-white/50 hover:text-white"><X size={14} /></button>
                                            </div>

                                            <div className="absolute bottom-3 left-3 right-3">
                                                <label className="text-[10px] text-white/70 block">BARS</label>
                                                <input
                                                    type="number"
                                                    value={block.bars}
                                                    onChange={(e) => updateBars(block.id, Number(e.target.value))}
                                                    className="w-full bg-white/20 rounded px-1 text-xs text-white text-center"
                                                />
                                            </div>
                                        </div>
                                    )}
                                </Draggable>
                            ))}
                            {provided.placeholder}
                        </div>
                    )}
                </Droppable>
            </DragDropContext>

            {/* Actions */}
            <div className="flex justify-end">
                {downloadUrl ? (
                    <a
                        href={downloadUrl}
                        download="arrangement.mid"
                        className="bg-green-600 hover:bg-green-500 text-white px-6 py-3 rounded-xl font-bold flex items-center gap-2 animate-bounce"
                    >
                        <Music size={20} /> DOwnload Arrangement
                    </a>
                ) : (
                    <button
                        onClick={handleGenerate}
                        disabled={isGenerating || blocks.length === 0}
                        className={`px-6 py-3 rounded-xl font-bold flex items-center gap-2 ${isGenerating ? 'bg-gray-600' : 'bg-gradient-to-r from-blue-500 to-purple-600 hover:shadow-lg hover:shadow-purple-500/20'}`}
                    >
                        {isGenerating ? 'Stitching...' : <><Play size={20} /> Generate Song</>}
                    </button>
                )}
            </div>
        </div>
    );
}
