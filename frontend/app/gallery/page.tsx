// frontend/app/gallery/page.tsx
'use client';

import { useEffect, useState } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';
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
  midi_url: string;
  view_count: number;
  play_count: number;
  download_count: number;
  upvotes: number;
  downvotes: number;
  score: number;
  created_at: string;
}

export default function PublicGalleryPage() {
  const router = useRouter();
  const [generations, setGenerations] = useState<SharedGeneration[]>([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState('recent');
  const [filterType, setFilterType] = useState('');
  const [filterStyle, setFilterStyle] = useState('');

  useEffect(() => {
    loadGallery();
  }, [sortBy, filterType, filterStyle]);

  const loadGallery = async () => {
    try {
      setLoading(true);
      const params: any = { sort_by: sortBy };
      if (filterType) params.type = filterType;
      if (filterStyle) params.style = filterStyle;

      const response = await axios.get('http://localhost:8000/social/generations', { params });
      setGenerations(response.data);
    } catch (err) {
      console.error('Failed to load gallery:', err);
      toast.error('Failed to load gallery');
    } finally {
      setLoading(false);
    }
  };

  const viewGeneration = (shareId: string) => {
    router.push(`/share/${shareId}`);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin text-6xl mb-4">🎵</div>
          <p className="text-white text-xl">Loading gallery...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-gray-900 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-5xl font-bold text-white mb-2">🎵 Public Gallery</h1>
          <p className="text-xl text-gray-400">Explore amazing AI-generated music patterns from the community</p>
        </div>

        {/* Filters and Sorting */}
        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700 mb-6">
          <div className="flex flex-wrap gap-4 items-center">
            {/* Sort By */}
            <div className="flex items-center gap-2">
              <span className="text-gray-400 text-sm">Sort:</span>
              <div className="flex gap-2">
                {['recent', 'popular', 'trending'].map((sort) => (
                  <button
                    key={sort}
                    onClick={() => setSortBy(sort)}
                    className={`px-4 py-2 rounded-lg text-sm transition-all capitalize ${
                      sortBy === sort
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    {sort}
                  </button>
                ))}
              </div>
            </div>

            {/* Filter by Type */}
            <div className="flex items-center gap-2">
              <span className="text-gray-400 text-sm">Type:</span>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="px-4 py-2 bg-gray-700 text-white rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
              >
                <option value="">All Types</option>
                <option value="drums">🥁 Drums</option>
                <option value="bass">🎸 Bass</option>
                <option value="melody">🎹 Melody</option>
                <option value="full">🎼 Full</option>
              </select>
            </div>

            {/* Filter by Style */}
            <div className="flex items-center gap-2">
              <span className="text-gray-400 text-sm">Style:</span>
              <select
                value={filterStyle}
                onChange={(e) => setFilterStyle(e.target.value)}
                className="px-4 py-2 bg-gray-700 text-white rounded-lg border border-gray-600 focus:border-blue-500 focus:outline-none"
              >
                <option value="">All Styles</option>
                <option value="techno">Techno</option>
                <option value="house">House</option>
                <option value="trap">Trap</option>
                <option value="lofi">Lo-Fi</option>
                <option value="dnb">Drum & Bass</option>
              </select>
            </div>

            <div className="ml-auto text-gray-400 text-sm">
              {generations.length} patterns
            </div>
          </div>
        </div>

        {/* Gallery Grid */}
        {generations.length === 0 ? (
          <div className="bg-gray-800 p-12 rounded-lg border border-gray-700 text-center">
            <div className="text-6xl mb-4">📭</div>
            <h3 className="text-2xl font-bold text-white mb-2">No patterns found</h3>
            <p className="text-gray-400 mb-4">Try different filters or be the first to share!</p>
            <a
              href="/"
              className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-all"
            >
              Create & Share
            </a>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {generations.map((gen) => (
              <div
                key={gen.id}
                onClick={() => viewGeneration(gen.share_id)}
                className="bg-gray-800 p-5 rounded-lg border border-gray-700 hover:border-purple-500 transition-all cursor-pointer group"
              >
                {/* Title */}
                <h3 className="text-xl font-bold text-white mb-2 group-hover:text-purple-400 transition-colors">
                  {gen.title}
                </h3>

                {/* Description */}
                {gen.description && (
                  <p className="text-sm text-gray-400 mb-3 line-clamp-2">{gen.description}</p>
                )}

                {/* Badges */}
                <div className="flex flex-wrap gap-2 mb-3">
                  <span className={`px-2 py-1 rounded text-xs font-bold ${
                    gen.mode === 'simple' ? 'bg-blue-600 text-white' : 'bg-purple-600 text-white'
                  }`}>
                    {gen.mode === 'simple' ? '🎹' : '🧬'}
                  </span>
                  <span className="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs font-bold capitalize">
                    {gen.type === 'drums' && '🥁'}
                    {gen.type === 'bass' && '🎸'}
                    {gen.type === 'melody' && '🎹'}
                    {gen.type === 'full' && '🎼'}
                    {' '}{gen.type}
                  </span>
                  <span className="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs capitalize">
                    {gen.style}
                  </span>
                  <span className="px-2 py-1 bg-gray-700 text-gray-300 rounded text-xs">
                    {gen.bpm} BPM
                  </span>
                </div>

                {/* Stats */}
                <div className="flex items-center gap-4 text-xs text-gray-400 mb-3">
                  <div className="flex items-center gap-1">
                    <span>👁️</span>
                    <span>{gen.view_count}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <span>▶️</span>
                    <span>{gen.play_count}</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <span>⬇️</span>
                    <span>{gen.download_count}</span>
                  </div>
                </div>

                {/* Score */}
                <div className="flex items-center justify-between border-t border-gray-700 pt-3">
                  <div className="flex items-center gap-3">
                    <div className="flex items-center gap-1 text-green-400">
                      <span>👍</span>
                      <span className="font-bold">{gen.upvotes}</span>
                    </div>
                    <div className="flex items-center gap-1 text-red-400">
                      <span>👎</span>
                      <span className="font-bold">{gen.downvotes}</span>
                    </div>
                  </div>
                  <div className={`px-3 py-1 rounded-lg font-bold ${
                    gen.score > 0 ? 'bg-green-900 text-green-400' :
                    gen.score < 0 ? 'bg-red-900 text-red-400' :
                    'bg-gray-700 text-gray-400'
                  }`}>
                    {gen.score > 0 ? '+' : ''}{gen.score}
                  </div>
                </div>

                {/* Author & Date */}
                <div className="text-xs text-gray-500 mt-3">
                  by {gen.user_email.split('@')[0]} • {new Date(gen.created_at).toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Call to Action */}
        <div className="mt-12 bg-gradient-to-r from-purple-600 to-blue-600 p-8 rounded-lg text-center">
          <h2 className="text-3xl font-bold text-white mb-2">Share Your Creations</h2>
          <p className="text-purple-100 mb-4">Create amazing patterns and share them with the community</p>
          <a
            href="/"
            className="inline-block px-8 py-3 bg-white text-purple-600 font-bold rounded-lg hover:bg-gray-100 transition-all"
          >
            Start Creating
          </a>
        </div>
      </div>
    </div>
  );
}
