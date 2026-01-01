// frontend/app/share/[shareId]/page.tsx
'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import axios from 'axios';
import MidiPlayerWithAudio from '@/components/MidiPlayerWithAudio';
import toast from 'react-hot-toast';

interface SharedGeneration {
  id: number;
  share_id: string;
  user_email: string;
  title: string;
  description: string | null;
  mode: string;
  type: string;
  style: string;
  bpm: number;
  key: string;
  scale: string;
  density: number | null;
  complexity: number | null;
  groove: number | null;
  evolution: number | null;
  bars: number | null;
  midi_url: string;
  view_count: number;
  play_count: number;
  download_count: number;
  upvotes: number;
  downvotes: number;
  score: number;
  created_at: string;
  user_vote: string | null;
}

export default function SharedGenerationPage() {
  const params = useParams();
  const shareId = params.shareId as string;

  const [generation, setGeneration] = useState<SharedGeneration | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [hasVoted, setHasVoted] = useState(false);

  useEffect(() => {
    loadSharedGeneration();
  }, [shareId]);

  const loadSharedGeneration = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`http://localhost:8000/social/generations/${shareId}`);
      setGeneration(response.data);
      setHasVoted(!!response.data.user_vote);
    } catch (err: any) {
      console.error('Failed to load shared generation:', err);
      setError(err.response?.data?.detail || 'Failed to load shared generation');
      toast.error('Failed to load shared generation');
    } finally {
      setLoading(false);
    }
  };

  const handleVote = async (voteType: 'upvote' | 'downvote') => {
    const token = localStorage.getItem('token');
    if (!token) {
      toast.error('Please log in to vote');
      return;
    }

    try {
      const response = await axios.post(
        `http://localhost:8000/social/generations/${shareId}/vote`,
        { vote_type: voteType },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Update local state
      setGeneration(prev => prev ? {
        ...prev,
        upvotes: response.data.upvotes,
        downvotes: response.data.downvotes,
        score: response.data.score,
        user_vote: voteType
      } : null);

      setHasVoted(true);
      toast.success(voteType === 'upvote' ? '👍 Upvoted!' : '👎 Downvoted');
    } catch (err: any) {
      console.error('Failed to vote:', err);
      toast.error(err.response?.data?.detail || 'Failed to vote');
    }
  };

  const handlePlay = async () => {
    try {
      await axios.post(`http://localhost:8000/social/generations/${shareId}/play`);
      // Update play count locally
      setGeneration(prev => prev ? { ...prev, play_count: prev.play_count + 1 } : null);
    } catch (err) {
      console.error('Failed to track play:', err);
    }
  };

  const handleDownload = async () => {
    try {
      await axios.post(`http://localhost:8000/social/generations/${shareId}/download`);
      // Update download count locally
      setGeneration(prev => prev ? { ...prev, download_count: prev.download_count + 1 } : null);
    } catch (err) {
      console.error('Failed to track download:', err);
    }
  };

  const copyShareLink = () => {
    const url = window.location.href;
    navigator.clipboard.writeText(url);
    toast.success('Share link copied to clipboard!');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin text-6xl mb-4">🎵</div>
          <p className="text-white text-xl">Loading shared generation...</p>
        </div>
      </div>
    );
  }

  if (error || !generation) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 flex items-center justify-center">
        <div className="text-center bg-gray-800 p-8 rounded-lg border border-red-500">
          <div className="text-6xl mb-4">❌</div>
          <h1 className="text-2xl font-bold text-white mb-2">Generation Not Found</h1>
          <p className="text-gray-400 mb-4">{error || 'This shared generation does not exist or has been removed.'}</p>
          <a href="/" className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all inline-block">
            Go to Home
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700 mb-6">
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <h1 className="text-3xl font-bold text-white mb-2">{generation.title}</h1>
              {generation.description && (
                <p className="text-gray-400 mb-4">{generation.description}</p>
              )}
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <span>Shared by {generation.user_email.split('@')[0]}</span>
                <span>•</span>
                <span>{new Date(generation.created_at).toLocaleDateString()}</span>
              </div>
            </div>

            {/* Share Button */}
            <button
              onClick={copyShareLink}
              className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-all flex items-center gap-2"
            >
              <span>🔗</span>
              <span>Share</span>
            </button>
          </div>

          {/* Badges */}
          <div className="flex flex-wrap gap-2 mb-4">
            <span className={`px-3 py-1 rounded-full text-xs font-bold ${
              generation.mode === 'simple' ? 'bg-blue-600 text-white' : 'bg-purple-600 text-white'
            }`}>
              {generation.mode === 'simple' ? '🎹 Simple' : '🧬 DNA'}
            </span>
            <span className="px-3 py-1 bg-gray-700 text-gray-300 rounded-full text-xs font-bold capitalize">
              {generation.type === 'drums' && '🥁'}
              {generation.type === 'bass' && '🎸'}
              {generation.type === 'melody' && '🎹'}
              {generation.type === 'full' && '🎼'}
              {' '}
              {generation.type}
            </span>
            <span className="px-3 py-1 bg-gray-700 text-gray-300 rounded-full text-xs font-bold capitalize">
              {generation.style}
            </span>
            <span className="px-3 py-1 bg-gray-700 text-gray-300 rounded-full text-xs font-bold">
              {generation.bpm} BPM
            </span>
            <span className="px-3 py-1 bg-gray-700 text-gray-300 rounded-full text-xs font-bold">
              {generation.key} {generation.scale}
            </span>
          </div>

          {/* DNA Parameters (if advanced mode) */}
          {generation.mode === 'advanced' && generation.density !== null && (
            <div className="bg-gray-900 p-4 rounded-lg border border-gray-700">
              <h3 className="text-sm font-bold text-purple-400 mb-3">DNA Parameters</h3>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
                <div>
                  <div className="text-xs text-gray-400 mb-1">Density</div>
                  <div className="text-lg font-bold text-white">{generation.density?.toFixed(2)}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-400 mb-1">Complexity</div>
                  <div className="text-lg font-bold text-white">{generation.complexity?.toFixed(2)}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-400 mb-1">Groove</div>
                  <div className="text-lg font-bold text-white">{generation.groove?.toFixed(2)}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-400 mb-1">Evolution</div>
                  <div className="text-lg font-bold text-white">{generation.evolution?.toFixed(2)}</div>
                </div>
                <div>
                  <div className="text-xs text-gray-400 mb-1">Bars</div>
                  <div className="text-lg font-bold text-white">{generation.bars}</div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* MIDI Player */}
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700 mb-6">
          <h2 className="text-xl font-bold text-white mb-4">🎵 Listen & Download</h2>
          <MidiPlayerWithAudio
            midiUrl={`http://localhost:8000${generation.midi_url}`}
            bpm={generation.bpm}
            onPlay={handlePlay}
            onDownload={handleDownload}
          />
        </div>

        {/* Voting and Stats */}
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <div className="flex items-center justify-between">
            {/* Voting Buttons */}
            <div className="flex items-center gap-4">
              <button
                onClick={() => handleVote('upvote')}
                disabled={hasVoted && generation.user_vote === 'upvote'}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                  generation.user_vote === 'upvote'
                    ? 'bg-green-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-green-600 hover:text-white'
                }`}
              >
                <span>👍</span>
                <span className="font-bold">{generation.upvotes}</span>
              </button>

              <button
                onClick={() => handleVote('downvote')}
                disabled={hasVoted && generation.user_vote === 'downvote'}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                  generation.user_vote === 'downvote'
                    ? 'bg-red-600 text-white'
                    : 'bg-gray-700 text-gray-300 hover:bg-red-600 hover:text-white'
                }`}
              >
                <span>👎</span>
                <span className="font-bold">{generation.downvotes}</span>
              </button>

              <div className="px-4 py-2 bg-purple-600 text-white rounded-lg font-bold">
                Score: {generation.score}
              </div>
            </div>

            {/* Stats */}
            <div className="flex items-center gap-6 text-sm text-gray-400">
              <div className="flex items-center gap-2">
                <span>👁️</span>
                <span>{generation.view_count} views</span>
              </div>
              <div className="flex items-center gap-2">
                <span>▶️</span>
                <span>{generation.play_count} plays</span>
              </div>
              <div className="flex items-center gap-2">
                <span>⬇️</span>
                <span>{generation.download_count} downloads</span>
              </div>
            </div>
          </div>
        </div>

        {/* Call to Action */}
        <div className="mt-8 bg-gradient-to-r from-purple-600 to-blue-600 p-6 rounded-lg text-center">
          <h2 className="text-2xl font-bold text-white mb-2">Create Your Own AI Music</h2>
          <p className="text-purple-100 mb-4">Join AI Music Copilot and start generating unique patterns</p>
          <a
            href="/"
            className="inline-block px-8 py-3 bg-white text-purple-600 font-bold rounded-lg hover:bg-gray-100 transition-all"
          >
            Get Started Free
          </a>
        </div>
      </div>
    </div>
  );
}
