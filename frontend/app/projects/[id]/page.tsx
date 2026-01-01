'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-hot-toast';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import MidiPlayerWithAudio from '@/components/MidiPlayerWithAudio';

interface Project {
  id: number;
  name: string;
  description: string | null;
  bpm: number;
  key: string;
  scale: string;
  total_bars: number;
  is_public: boolean;
  created_at: string;
  updated_at: string;
  tracks: Track[];
}

interface Track {
  id: number;
  project_id: number;
  name: string;
  type: string;
  midi_url: string;
  density: number;
  complexity: number;
  groove: number;
  evolution: number;
  bars: number;
  volume: number;
  pan: number;
  muted: boolean;
  solo: boolean;
  order: number;
  created_at: string;
  updated_at: string;
}

export default function ProjectEditorPage() {
  const router = useRouter();
  const params = useParams();
  const projectId = params.id as string;

  const [project, setProject] = useState<Project | null>(null);
  const [loading, setLoading] = useState(true);
  const [exportedUrl, setExportedUrl] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);
  const [variationModalOpen, setVariationModalOpen] = useState(false);
  const [selectedTrackForVariation, setSelectedTrackForVariation] = useState<Track | null>(null);
  const [variationStrategy, setVariationStrategy] = useState<'subtle' | 'moderate' | 'extreme'>('moderate');
  const [preserveFeel, setPreserveFeel] = useState(true);
  const [generatingVariation, setGeneratingVariation] = useState(false);

  useEffect(() => {
    loadProject();
  }, [projectId]);

  const loadProject = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        toast.error('Please log in to view projects');
        router.push('/');
        return;
      }

      const response = await axios.get(`http://localhost:8000/api/projects/${projectId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProject(response.data);
    } catch (err: any) {
      console.error('Error loading project:', err);
      if (err.response?.status === 404) {
        toast.error('Project not found');
        router.push('/projects');
      } else if (err.response?.status === 401) {
        toast.error('Session expired. Please log in again.');
        router.push('/');
      } else {
        toast.error('Failed to load project');
      }
    } finally {
      setLoading(false);
    }
  };

  const updateTrack = async (trackId: number, updates: Partial<Track>) => {
    try {
      const token = localStorage.getItem('token');
      await axios.put(
        `http://localhost:8000/api/projects/${projectId}/tracks/${trackId}`,
        updates,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      loadProject(); // Reload to get updated data
    } catch (err: any) {
      console.error('Error updating track:', err);
      toast.error('Failed to update track');
    }
  };

  const deleteTrack = async (trackId: number, trackName: string) => {
    if (!confirm(`Delete track "${trackName}"?`)) return;

    try {
      const token = localStorage.getItem('token');
      await axios.delete(
        `http://localhost:8000/api/projects/${projectId}/tracks/${trackId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      toast.success('Track deleted');
      loadProject();
    } catch (err: any) {
      console.error('Error deleting track:', err);
      toast.error('Failed to delete track');
    }
  };

  const exportProject = async () => {
    if (!project || project.tracks.length === 0) {
      toast.error('Add at least one track before exporting');
      return;
    }

    setExporting(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get(
        `http://localhost:8000/api/projects/${projectId}/export`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      const fileUrl = `http://localhost:8000${response.data.file_url}`;
      setExportedUrl(fileUrl);
      toast.success(`Multi-track MIDI exported! (${response.data.track_count} tracks)`);
    } catch (err: any) {
      console.error('Error exporting project:', err);
      toast.error(err.response?.data?.detail || 'Failed to export project');
    } finally {
      setExporting(false);
    }
  };

  const downloadExport = () => {
    if (!exportedUrl) return;
    window.open(exportedUrl, '_blank');
  };

  const openVariationModal = (track: Track) => {
    setSelectedTrackForVariation(track);
    setVariationStrategy('moderate');
    setPreserveFeel(true);
    setVariationModalOpen(true);
  };

  const closeVariationModal = () => {
    setVariationModalOpen(false);
    setSelectedTrackForVariation(null);
  };

  const generateVariation = async () => {
    if (!selectedTrackForVariation) return;

    setGeneratingVariation(true);
    try {
      const token = localStorage.getItem('token');

      // Step 1: Generate mutated DNA parameters from backend
      const variationResponse = await axios.post(
        `http://localhost:8000/api/projects/${projectId}/tracks/${selectedTrackForVariation.id}/variations`,
        {
          strategy: variationStrategy,
          preserve_feel: preserveFeel
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      const mutatedParams = variationResponse.data;
      toast.success(`Variation DNA generated! (${variationStrategy} strategy)`);

      // Step 2: Generate MIDI with mutated parameters
      const generateResponse = await axios.post(
        'http://localhost:8000/api/generate',
        {
          type: selectedTrackForVariation.type,
          mode: 'advanced',
          style: 'techno', // You might want to preserve original style
          bpm: project?.bpm || 120,
          key: project?.key || 'C',
          scale: project?.scale || 'minor',
          dna_density: mutatedParams.density,
          dna_complexity: mutatedParams.complexity,
          dna_groove: mutatedParams.groove,
          dna_evolution: mutatedParams.evolution,
          bars: mutatedParams.bars
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      const newMidiUrl = generateResponse.data.midi_url;
      toast.success('Variation MIDI generated!');

      // Step 3: Add variation as new track
      const trackResponse = await axios.post(
        `http://localhost:8000/api/projects/${projectId}/tracks`,
        {
          name: `${selectedTrackForVariation.name} (${variationStrategy})`,
          type: selectedTrackForVariation.type,
          midi_url: newMidiUrl,
          mode: 'advanced',
          style: 'techno',
          density: mutatedParams.density,
          complexity: mutatedParams.complexity,
          groove: mutatedParams.groove,
          evolution: mutatedParams.evolution,
          bars: mutatedParams.bars,
          volume: selectedTrackForVariation.volume,
          pan: selectedTrackForVariation.pan,
          muted: false,
          solo: false
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      toast.success('Variation added to project!');
      closeVariationModal();
      loadProject(); // Reload to show new track
    } catch (err: any) {
      console.error('Error generating variation:', err);
      toast.error(err.response?.data?.detail || 'Failed to generate variation');
    } finally {
      setGeneratingVariation(false);
    }
  };

  const getTypeColor = (type: string) => {
    const colors: { [key: string]: string } = {
      drums: 'bg-red-500',
      bass: 'bg-blue-500',
      melody: 'bg-green-500',
      chords: 'bg-purple-500',
      fx: 'bg-yellow-500'
    };
    return colors[type] || 'bg-gray-500';
  };

  const getTypeIcon = (type: string) => {
    const icons: { [key: string]: string } = {
      drums: '🥁',
      bass: '🎸',
      melody: '🎹',
      chords: '🎼',
      fx: '✨'
    };
    return icons[type] || '🎵';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-2xl">Loading project...</div>
      </div>
    );
  }

  if (!project) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 p-8">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <Link
              href="/projects"
              className="text-purple-300 hover:text-purple-200 transition mb-2 inline-block"
            >
              ← Back to Projects
            </Link>
            <h1 className="text-4xl font-bold text-white mb-2">{project.name}</h1>
            {project.description && (
              <p className="text-purple-200">{project.description}</p>
            )}
          </div>

          <div className="flex gap-4">
            <Link
              href={`/?project=${projectId}`}
              className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 text-white font-semibold rounded-lg shadow-lg transition"
            >
              + Add Track
            </Link>
            <button
              onClick={exportProject}
              disabled={exporting || project.tracks.length === 0}
              className="px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white font-semibold rounded-lg shadow-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {exporting ? 'Exporting...' : '💾 Export Multi-Track MIDI'}
            </button>
          </div>
        </div>

        {/* Project Info */}
        <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 mb-6">
          <div className="grid grid-cols-4 gap-6">
            <div>
              <div className="text-purple-300 text-sm mb-1">BPM</div>
              <div className="text-white text-2xl font-bold">{project.bpm}</div>
            </div>
            <div>
              <div className="text-purple-300 text-sm mb-1">Key</div>
              <div className="text-white text-2xl font-bold">
                {project.key} {project.scale}
              </div>
            </div>
            <div>
              <div className="text-purple-300 text-sm mb-1">Total Bars</div>
              <div className="text-white text-2xl font-bold">{project.total_bars}</div>
            </div>
            <div>
              <div className="text-purple-300 text-sm mb-1">Tracks</div>
              <div className="text-white text-2xl font-bold">{project.tracks.length}</div>
            </div>
          </div>
        </div>

        {/* Exported File */}
        {exportedUrl && (
          <div className="bg-green-500/20 backdrop-blur-md rounded-xl p-6 mb-6 border border-green-400/30">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-green-300 text-sm mb-1">Multi-Track MIDI Ready!</div>
                <div className="text-white font-semibold">
                  {project.tracks.length} tracks merged into Type 1 MIDI file
                </div>
              </div>
              <div className="flex gap-4">
                <button
                  onClick={downloadExport}
                  className="px-6 py-2 bg-green-500 hover:bg-green-600 text-white font-semibold rounded-lg transition"
                >
                  ⬇️ Download
                </button>
                <MidiPlayerWithAudio midiUrl={exportedUrl} bpm={project.bpm} />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Track Timeline */}
      <div className="max-w-7xl mx-auto">
        <h2 className="text-2xl font-bold text-white mb-4">Tracks</h2>

        {project.tracks.length === 0 ? (
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-12 text-center">
            <div className="text-6xl mb-4">🎼</div>
            <h3 className="text-2xl font-bold text-white mb-2">No tracks yet</h3>
            <p className="text-purple-200 mb-6">
              Generate patterns from the main generator and add them to this project
            </p>
            <Link
              href={`/?project=${projectId}`}
              className="inline-block px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 text-white font-semibold rounded-lg shadow-lg transition"
            >
              Generate Your First Track
            </Link>
          </div>
        ) : (
          <div className="space-y-4">
            {project.tracks
              .sort((a, b) => a.order - b.order)
              .map((track) => (
                <div
                  key={track.id}
                  className="bg-white/10 backdrop-blur-md rounded-xl p-6 hover:bg-white/15 transition"
                >
                  <div className="flex items-center gap-4">
                    {/* Track Type Indicator */}
                    <div
                      className={`w-16 h-16 ${getTypeColor(track.type)} rounded-lg flex items-center justify-center text-3xl`}
                    >
                      {getTypeIcon(track.type)}
                    </div>

                    {/* Track Info */}
                    <div className="flex-1">
                      <div className="flex items-center gap-4 mb-2">
                        <h3 className="text-xl font-bold text-white">{track.name}</h3>
                        <span className="text-sm text-purple-300 capitalize">{track.type}</span>
                      </div>

                      {/* DNA Parameters */}
                      <div className="flex gap-4 text-sm mb-2">
                        <span className="text-purple-300">
                          Density: <span className="text-white">{(track.density * 100).toFixed(0)}%</span>
                        </span>
                        <span className="text-purple-300">
                          Complexity: <span className="text-white">{(track.complexity * 100).toFixed(0)}%</span>
                        </span>
                        <span className="text-purple-300">
                          Groove: <span className="text-white">{(track.groove * 100).toFixed(0)}%</span>
                        </span>
                        <span className="text-purple-300">
                          Bars: <span className="text-white">{track.bars}</span>
                        </span>
                      </div>

                      {/* Mixer Controls */}
                      <div className="flex gap-6 items-center">
                        {/* Volume */}
                        <div className="flex items-center gap-2">
                          <span className="text-purple-300 text-sm w-16">Volume:</span>
                          <input
                            type="range"
                            min="0"
                            max="100"
                            value={track.volume * 100}
                            onChange={(e) =>
                              updateTrack(track.id, { volume: parseInt(e.target.value) / 100 })
                            }
                            className="w-32"
                          />
                          <span className="text-white text-sm w-12">
                            {(track.volume * 100).toFixed(0)}%
                          </span>
                        </div>

                        {/* Pan */}
                        <div className="flex items-center gap-2">
                          <span className="text-purple-300 text-sm w-12">Pan:</span>
                          <input
                            type="range"
                            min="0"
                            max="100"
                            value={track.pan * 100}
                            onChange={(e) =>
                              updateTrack(track.id, { pan: parseInt(e.target.value) / 100 })
                            }
                            className="w-32"
                          />
                          <span className="text-white text-sm w-12">
                            {track.pan === 0.5 ? 'C' : track.pan < 0.5 ? 'L' : 'R'}
                          </span>
                        </div>

                        {/* Mute/Solo */}
                        <button
                          onClick={() => updateTrack(track.id, { muted: !track.muted })}
                          className={`px-3 py-1 rounded ${
                            track.muted
                              ? 'bg-red-500 text-white'
                              : 'bg-gray-600 text-gray-300 hover:bg-gray-500'
                          } text-sm font-semibold transition`}
                        >
                          M
                        </button>
                        <button
                          onClick={() => updateTrack(track.id, { solo: !track.solo })}
                          className={`px-3 py-1 rounded ${
                            track.solo
                              ? 'bg-yellow-500 text-white'
                              : 'bg-gray-600 text-gray-300 hover:bg-gray-500'
                          } text-sm font-semibold transition`}
                        >
                          S
                        </button>
                      </div>
                    </div>

                    {/* Track Actions */}
                    <div className="flex flex-col gap-2">
                      <MidiPlayerWithAudio
                        midiUrl={track.midi_url.startsWith('http') ? track.midi_url : `http://localhost:8000${track.midi_url}`}
                        bpm={project.bpm}
                      />
                      <button
                        onClick={() => openVariationModal(track)}
                        className="px-4 py-2 bg-purple-500/20 hover:bg-purple-500/30 text-purple-300 hover:text-purple-200 rounded-lg transition text-sm"
                      >
                        🎲 Variation
                      </button>
                      <button
                        onClick={() => deleteTrack(track.id, track.name)}
                        className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-300 hover:text-red-200 rounded-lg transition text-sm"
                      >
                        🗑️ Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))}
          </div>
        )}
      </div>

      {/* Variation Modal */}
      {variationModalOpen && selectedTrackForVariation && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 rounded-2xl p-8 max-w-2xl w-full border border-purple-500/30">
            <h2 className="text-3xl font-bold text-white mb-6">
              🎲 Generate Variation
            </h2>

            {/* Original Track Info */}
            <div className="bg-white/10 backdrop-blur-md rounded-xl p-6 mb-6">
              <h3 className="text-xl font-bold text-white mb-4">Original Track</h3>
              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="text-purple-300">Name</div>
                  <div className="text-white font-semibold">{selectedTrackForVariation.name}</div>
                </div>
                <div>
                  <div className="text-purple-300">Type</div>
                  <div className="text-white font-semibold capitalize">{selectedTrackForVariation.type}</div>
                </div>
                <div>
                  <div className="text-purple-300">Density</div>
                  <div className="text-white font-semibold">{(selectedTrackForVariation.density * 100).toFixed(0)}%</div>
                </div>
                <div>
                  <div className="text-purple-300">Complexity</div>
                  <div className="text-white font-semibold">{(selectedTrackForVariation.complexity * 100).toFixed(0)}%</div>
                </div>
                <div>
                  <div className="text-purple-300">Groove</div>
                  <div className="text-white font-semibold">{(selectedTrackForVariation.groove * 100).toFixed(0)}%</div>
                </div>
                <div>
                  <div className="text-purple-300">Bars</div>
                  <div className="text-white font-semibold">{selectedTrackForVariation.bars}</div>
                </div>
              </div>
            </div>

            {/* Strategy Selection */}
            <div className="mb-6">
              <label className="block text-purple-300 mb-3 font-semibold">Variation Strategy</label>
              <div className="grid grid-cols-3 gap-4">
                <button
                  onClick={() => setVariationStrategy('subtle')}
                  className={`p-4 rounded-xl transition ${
                    variationStrategy === 'subtle'
                      ? 'bg-green-500 text-white'
                      : 'bg-white/10 text-purple-300 hover:bg-white/20'
                  }`}
                >
                  <div className="text-2xl mb-2">🌱</div>
                  <div className="font-bold">Subtle</div>
                  <div className="text-xs mt-1 opacity-80">5-10% change</div>
                </button>
                <button
                  onClick={() => setVariationStrategy('moderate')}
                  className={`p-4 rounded-xl transition ${
                    variationStrategy === 'moderate'
                      ? 'bg-blue-500 text-white'
                      : 'bg-white/10 text-purple-300 hover:bg-white/20'
                  }`}
                >
                  <div className="text-2xl mb-2">⚡</div>
                  <div className="font-bold">Moderate</div>
                  <div className="text-xs mt-1 opacity-80">10-20% change</div>
                </button>
                <button
                  onClick={() => setVariationStrategy('extreme')}
                  className={`p-4 rounded-xl transition ${
                    variationStrategy === 'extreme'
                      ? 'bg-red-500 text-white'
                      : 'bg-white/10 text-purple-300 hover:bg-white/20'
                  }`}
                >
                  <div className="text-2xl mb-2">🔥</div>
                  <div className="font-bold">Extreme</div>
                  <div className="text-xs mt-1 opacity-80">20-40% change</div>
                </button>
              </div>
            </div>

            {/* Preserve Feel Option */}
            <div className="mb-6">
              <label className="flex items-center gap-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={preserveFeel}
                  onChange={(e) => setPreserveFeel(e.target.checked)}
                  className="w-5 h-5"
                />
                <div>
                  <div className="text-white font-semibold">Preserve Feel</div>
                  <div className="text-purple-300 text-sm">
                    Keep groove and evolution closer to the original
                  </div>
                </div>
              </label>
            </div>

            {/* Info Box */}
            <div className="bg-blue-500/20 border border-blue-400/30 rounded-xl p-4 mb-6">
              <div className="text-blue-300 text-sm">
                <strong>How it works:</strong> The variation engine will intelligently mutate the DNA parameters
                to create a related but different version of your track. The new track will be added to your project.
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4">
              <button
                onClick={closeVariationModal}
                disabled={generatingVariation}
                className="flex-1 px-6 py-3 bg-gray-600 hover:bg-gray-500 text-white font-semibold rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Cancel
              </button>
              <button
                onClick={generateVariation}
                disabled={generatingVariation}
                className="flex-1 px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 text-white font-semibold rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {generatingVariation ? 'Generating...' : '🎲 Generate Variation'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
