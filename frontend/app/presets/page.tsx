// frontend/app/presets/page.tsx
'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

interface SharedPreset {
  id: number;
  share_id: string;
  user_email: string;
  name: string;
  description: string | null;
  mode: string;
  type: string;
  style: string;
  bpm: number;
  key: string;
  scale: string;
  density: number;
  complexity: number;
  groove: number;
  evolution: number;
  bars: number;
  tags: string | null;
  genre: string | null;
  view_count: number;
  use_count: number;
  upvotes: number;
  downvotes: number;
  score: number;
  created_at: string;
  user_vote: string | null;
}

export default function PresetMarketplacePage() {
  const [presets, setPresets] = useState<SharedPreset[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState('trending');
  const [filterGenre, setFilterGenre] = useState('');
  const [filterType, setFilterType] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('token');
    setIsAuthenticated(!!token);

    loadPresets();
  }, [sortBy, filterGenre, filterType]);

  const loadPresets = async () => {
    try {
      setLoading(true);
      const params: any = { sort_by: sortBy };
      if (filterGenre) params.genre = filterGenre;
      if (filterType) params.type = filterType;

      const token = localStorage.getItem('token');
      const headers = token ? { Authorization: `Bearer ${token}` } : {};

      const response = await axios.get('http://localhost:8000/social/presets', {
        params,
        headers
      });
      setPresets(response.data);
    } catch (err) {
      console.error('Failed to load presets:', err);
      toast.error('Failed to load presets');
    } finally {
      setLoading(false);
    }
  };

  const usePreset = async (preset: SharedPreset) => {
    if (!isAuthenticated) {
      toast.error('Please log in to use presets');
      return;
    }

    try {
      // Track usage
      await axios.post(`http://localhost:8000/social/presets/${preset.share_id}/use`);

      // Save to localStorage as custom preset
      const customPresets = JSON.parse(localStorage.getItem('customPresets') || '[]');
      const newPreset = {
        id: Date.now().toString(),
        name: `${preset.name} (from marketplace)`,
        description: preset.description || '',
        mode: preset.mode,
        type: preset.type,
        style: preset.style,
        bpm: preset.bpm,
        key: preset.key,
        scale: preset.scale,
        dna: {
          density: preset.density,
          complexity: preset.complexity,
          groove: preset.groove,
          evolution: preset.evolution,
          bars: preset.bars
        },
        createdAt: Date.now()
      };

      customPresets.unshift(newPreset);
      localStorage.setItem('customPresets', JSON.stringify(customPresets));

      toast.success(`✅ Preset "${preset.name}" added to your presets!`);

      // Redirect to main page
      window.location.href = '/';
    } catch (err) {
      console.error('Failed to use preset:', err);
      toast.error('Failed to use preset');
    }
  };

  const voteOnPreset = async (presetId: string, voteType: 'upvote' | 'downvote') => {
    if (!isAuthenticated) {
      toast.error('Please log in to vote');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      await axios.post(
        `http://localhost:8000/social/presets/${presetId}/vote`,
        { vote_type: voteType },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Reload presets
      loadPresets();
      toast.success(voteType === 'upvote' ? '👍 Upvoted!' : '👎 Downvoted');
    } catch (err: any) {
      console.error('Failed to vote:', err);
      toast.error(err.response?.data?.detail || 'Failed to vote');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin text-6xl mb-4">🎨</div>
          <p className="text-white text-xl">Loading preset marketplace...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-5xl font-bold text-white mb-2">🎨 Preset Marketplace</h1>
          <p className="text-xl text-gray-400">Discover and use community-shared presets</p>
        </div>

        {/* Filters and Sorting */}
        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700 mb-6">
          <div className="flex flex-wrap gap-4 items-center">
            {/* Sort By */}
            <div className="flex items-center gap-2">
              <span className="text-gray-400 text-sm">Sort:</span>
              <div className="flex gap-2">
                {['trending', 'popular', 'most_used', 'recent'].map((sort) => (
                  <button
                    key={sort}
                    onClick={() => setSortBy(sort)}
                    className={`px-4 py-2 rounded-lg text-sm transition-all capitalize ${
                      sortBy === sort
                        ? 'bg-purple-600 text-white'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    {sort.replace('_', ' ')}
                  </button>
                ))}
              </div>
            </div>

            {/* Filter by Genre */}
            <div className="flex items-center gap-2">
              <span className="text-gray-400 text-sm">Genre:</span>
              <select
                value={filterGenre}
                onChange={(e) => setFilterGenre(e.target.value)}
                className="px-4 py-2 bg-gray-700 text-white rounded-lg border border-gray-600 focus:border-purple-500 focus:outline-none"
              >
                <option value="">All Genres</option>
                <option value="techno">Techno</option>
                <option value="house">House</option>
                <option value="trap">Trap</option>
                <option value="lofi">Lo-Fi</option>
                <option value="dnb">Drum & Bass</option>
              </select>
            </div>

            {/* Filter by Type */}
            <div className="flex items-center gap-2">
              <span className="text-gray-400 text-sm">Type:</span>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="px-4 py-2 bg-gray-700 text-white rounded-lg border border-gray-600 focus:border-purple-500 focus:outline-none"
              >
                <option value="">All Types</option>
                <option value="drums">🥁 Drums</option>
                <option value="bass">🎸 Bass</option>
                <option value="melody">🎹 Melody</option>
                <option value="full">🎼 Full</option>
              </select>
            </div>

            <div className="ml-auto text-gray-400 text-sm">
              {presets.length} presets
            </div>
          </div>
        </div>

        {/* Presets Grid */}
        {presets.length === 0 ? (
          <div className="bg-gray-800 p-12 rounded-lg border border-gray-700 text-center">
            <div className="text-6xl mb-4">📭</div>
            <h3 className="text-2xl font-bold text-white mb-2">No presets found</h3>
            <p className="text-gray-400 mb-4">Try different filters or share your own!</p>
            <a
              href="/"
              className="inline-block px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-all"
            >
              Create & Share Preset
            </a>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {presets.map((preset) => (
              <div
                key={preset.id}
                className="bg-gray-800 p-5 rounded-lg border border-gray-700 hover:border-purple-500 transition-all"
              >
                {/* Header */}
                <div className="flex items-start justify-between mb-3">
                  <div className="flex-1">
                    <h3 className="text-xl font-bold text-white mb-1">{preset.name}</h3>
                    {preset.description && (
                      <p className="text-sm text-gray-400 line-clamp-2">{preset.description}</p>
                    )}
                  </div>
                </div>

                {/* Badges */}
                <div className="flex flex-wrap gap-2 mb-3">
                  <span className="px-2 py-1 bg-purple-600 text-white rounded text-xs font-bold">
                    🧬 DNA
                  </span>
                  <span className="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs font-bold capitalize">
                    {preset.type === 'drums' && '🥁'}
                    {preset.type === 'bass' && '🎸'}
                    {preset.type === 'melody' && '🎹'}
                    {preset.type === 'full' && '🎼'}
                    {' '}{preset.type}
                  </span>
                  <span className="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs capitalize">
                    {preset.genre || preset.style}
                  </span>
                  <span className="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs">
                    {preset.bpm} BPM
                  </span>
                  <span className="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs">
                    {preset.key} {preset.scale}
                  </span>
                </div>

                {/* DNA Parameters */}
                <div className="bg-gray-900 p-3 rounded-lg mb-3">
                  <div className="text-xs text-purple-400 font-bold mb-2">DNA Parameters</div>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="flex justify-between">
                      <span className="text-gray-400">Density:</span>
                      <span className="text-white font-bold">{preset.density.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Complexity:</span>
                      <span className="text-white font-bold">{preset.complexity.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Groove:</span>
                      <span className="text-white font-bold">{preset.groove.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Evolution:</span>
                      <span className="text-white font-bold">{preset.evolution.toFixed(2)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-400">Bars:</span>
                      <span className="text-white font-bold">{preset.bars}</span>
                    </div>
                  </div>
                </div>

                {/* Stats */}
                <div className="flex items-center gap-4 text-xs text-gray-400 mb-3">
                  <div className="flex items-center gap-1">
                    <span>👁️</span>
                    <span>{preset.view_count}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <span>✨</span>
                    <span>{preset.use_count} uses</span>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-2 mb-3">
                  <button
                    onClick={() => usePreset(preset)}
                    className="flex-1 py-2 bg-purple-600 hover:bg-purple-700 rounded-lg font-semibold text-sm transition-all"
                  >
                    ✨ Use Preset
                  </button>
                  <button
                    onClick={() => voteOnPreset(preset.share_id, 'upvote')}
                    className={`px-3 py-2 rounded-lg text-sm transition-all ${
                      preset.user_vote === 'upvote'
                        ? 'bg-green-600 text-white'
                        : 'bg-gray-700 text-gray-300 hover:bg-green-600 hover:text-white'
                    }`}
                  >
                    👍 {preset.upvotes}
                  </button>
                  <button
                    onClick={() => voteOnPreset(preset.share_id, 'downvote')}
                    className={`px-3 py-2 rounded-lg text-sm transition-all ${
                      preset.user_vote === 'downvote'
                        ? 'bg-red-600 text-white'
                        : 'bg-gray-700 text-gray-300 hover:bg-red-600 hover:text-white'
                    }`}
                  >
                    👎 {preset.downvotes}
                  </button>
                </div>

                {/* Author & Date */}
                <div className="text-xs text-gray-500 border-t border-gray-700 pt-2">
                  by {preset.user_email.split('@')[0]} • {new Date(preset.created_at).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Call to Action */}
        <div className="mt-12 bg-gradient-to-r from-purple-600 to-blue-600 p-8 rounded-lg text-center">
          <h2 className="text-3xl font-bold text-white mb-2">Share Your Best Presets</h2>
          <p className="text-purple-100 mb-4">Help others create amazing music with your favorite settings</p>
          <a
            href="/"
            className="inline-block px-8 py-3 bg-white text-purple-600 font-bold rounded-lg hover:bg-gray-100 transition-all"
          >
            Create & Share
          </a>
        </div>
      </div>
    </div>
  );
}
