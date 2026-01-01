'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-hot-toast';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

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
  order_index: number;
  created_at: string;
  updated_at: string;
}

export default function ProjectsPage() {
  const router = useRouter();
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');
  const [newProjectDescription, setNewProjectDescription] = useState('');
  const [newProjectBpm, setNewProjectBpm] = useState(120);
  const [newProjectKey, setNewProjectKey] = useState('C');
  const [newProjectScale, setNewProjectScale] = useState('minor');

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        toast.error('Please log in to view projects');
        router.push('/');
        return;
      }

      const response = await axios.get('http://localhost:8000/api/projects', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setProjects(response.data);
    } catch (err: any) {
      console.error('Error loading projects:', err);
      if (err.response?.status === 401) {
        toast.error('Session expired. Please log in again.');
        router.push('/');
      } else {
        toast.error('Failed to load projects');
      }
    } finally {
      setLoading(false);
    }
  };

  const createProject = async () => {
    if (!newProjectName.trim()) {
      toast.error('Please enter a project name');
      return;
    }

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        toast.error('Please log in to create projects');
        return;
      }

      const response = await axios.post(
        'http://localhost:8000/api/projects',
        {
          name: newProjectName.trim(),
          description: newProjectDescription.trim() || null,
          bpm: newProjectBpm,
          key: newProjectKey,
          scale: newProjectScale,
          total_bars: 8
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      toast.success('Project created!');
      setShowCreateModal(false);
      setNewProjectName('');
      setNewProjectDescription('');
      setNewProjectBpm(120);
      setNewProjectKey('C');
      setNewProjectScale('minor');

      // Navigate to project editor
      router.push(`/projects/${response.data.id}`);
    } catch (err: any) {
      console.error('Error creating project:', err);
      toast.error('Failed to create project');
    }
  };

  const deleteProject = async (projectId: number, projectName: string) => {
    if (!confirm(`Are you sure you want to delete "${projectName}"? This cannot be undone.`)) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      await axios.delete(`http://localhost:8000/api/projects/${projectId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      toast.success('Project deleted');
      loadProjects();
    } catch (err: any) {
      console.error('Error deleting project:', err);
      toast.error('Failed to delete project');
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 flex items-center justify-center">
        <div className="text-white text-2xl">Loading projects...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 p-8">
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">Multi-Track Projects</h1>
            <p className="text-purple-200">Combine drums, bass, melody into full arrangements</p>
          </div>
          <Link
            href="/"
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition"
          >
            ← Back to Generator
          </Link>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white font-semibold rounded-lg shadow-lg transition"
        >
          + New Project
        </button>
      </div>

      {/* Projects Grid */}
      <div className="max-w-7xl mx-auto">
        {projects.length === 0 ? (
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-12 text-center">
            <div className="text-6xl mb-4">🎵</div>
            <h2 className="text-2xl font-bold text-white mb-2">No projects yet</h2>
            <p className="text-purple-200 mb-6">
              Create your first multi-track project to combine drums, bass, and melody!
            </p>
            <button
              onClick={() => setShowCreateModal(true)}
              className="px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white font-semibold rounded-lg shadow-lg transition"
            >
              Create Your First Project
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.map((project) => (
              <div
                key={project.id}
                className="bg-white/10 backdrop-blur-md rounded-xl p-6 hover:bg-white/20 transition cursor-pointer"
                onClick={() => router.push(`/projects/${project.id}`)}
              >
                <div className="flex items-start justify-between mb-3">
                  <h3 className="text-xl font-bold text-white">{project.name}</h3>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      deleteProject(project.id, project.name);
                    }}
                    className="text-red-300 hover:text-red-400 transition text-sm"
                  >
                    🗑️
                  </button>
                </div>

                {project.description && (
                  <p className="text-purple-200 text-sm mb-3">{project.description}</p>
                )}

                <div className="space-y-2 mb-4">
                  <div className="flex items-center gap-2 text-sm">
                    <span className="text-purple-300">Tracks:</span>
                    <span className="text-white font-semibold">{project.tracks.length}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <span className="text-purple-300">BPM:</span>
                    <span className="text-white font-semibold">{project.bpm}</span>
                  </div>
                  <div className="flex items-center gap-2 text-sm">
                    <span className="text-purple-300">Key:</span>
                    <span className="text-white font-semibold">
                      {project.key} {project.scale}
                    </span>
                  </div>
                </div>

                <div className="text-xs text-purple-300">
                  Updated {formatDate(project.updated_at)}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Project Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
          <div className="bg-gradient-to-br from-purple-800 to-blue-900 rounded-2xl p-8 max-w-md w-full shadow-2xl">
            <h2 className="text-2xl font-bold text-white mb-6">Create New Project</h2>

            <div className="space-y-4">
              <div>
                <label className="block text-purple-200 text-sm mb-2">Project Name</label>
                <input
                  type="text"
                  value={newProjectName}
                  onChange={(e) => setNewProjectName(e.target.value)}
                  placeholder="My Awesome Track"
                  className="w-full px-4 py-2 bg-white/10 border border-purple-400/30 rounded-lg text-white placeholder-purple-300/50 focus:outline-none focus:border-purple-400"
                />
              </div>

              <div>
                <label className="block text-purple-200 text-sm mb-2">Description (optional)</label>
                <textarea
                  value={newProjectDescription}
                  onChange={(e) => setNewProjectDescription(e.target.value)}
                  placeholder="A brief description of your project..."
                  rows={3}
                  className="w-full px-4 py-2 bg-white/10 border border-purple-400/30 rounded-lg text-white placeholder-purple-300/50 focus:outline-none focus:border-purple-400 resize-none"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-purple-200 text-sm mb-2">BPM</label>
                  <input
                    type="number"
                    value={newProjectBpm}
                    onChange={(e) => setNewProjectBpm(parseInt(e.target.value) || 120)}
                    min={60}
                    max={200}
                    className="w-full px-4 py-2 bg-white/10 border border-purple-400/30 rounded-lg text-white focus:outline-none focus:border-purple-400"
                  />
                </div>

                <div>
                  <label className="block text-purple-200 text-sm mb-2">Key</label>
                  <select
                    value={newProjectKey}
                    onChange={(e) => setNewProjectKey(e.target.value)}
                    className="w-full px-4 py-2 bg-white/10 border border-purple-400/30 rounded-lg text-white focus:outline-none focus:border-purple-400"
                  >
                    <option value="C">C</option>
                    <option value="C#">C#</option>
                    <option value="D">D</option>
                    <option value="D#">D#</option>
                    <option value="E">E</option>
                    <option value="F">F</option>
                    <option value="F#">F#</option>
                    <option value="G">G</option>
                    <option value="G#">G#</option>
                    <option value="A">A</option>
                    <option value="A#">A#</option>
                    <option value="B">B</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-purple-200 text-sm mb-2">Scale</label>
                <select
                  value={newProjectScale}
                  onChange={(e) => setNewProjectScale(e.target.value)}
                  className="w-full px-4 py-2 bg-white/10 border border-purple-400/30 rounded-lg text-white focus:outline-none focus:border-purple-400"
                >
                  <option value="major">Major</option>
                  <option value="minor">Minor</option>
                  <option value="dorian">Dorian</option>
                  <option value="phrygian">Phrygian</option>
                  <option value="lydian">Lydian</option>
                  <option value="mixolydian">Mixolydian</option>
                  <option value="harmonic_minor">Harmonic Minor</option>
                  <option value="blues">Blues</option>
                </select>
              </div>
            </div>

            <div className="flex gap-4 mt-6">
              <button
                onClick={() => setShowCreateModal(false)}
                className="flex-1 px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-lg transition"
              >
                Cancel
              </button>
              <button
                onClick={createProject}
                className="flex-1 px-4 py-2 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white font-semibold rounded-lg transition"
              >
                Create Project
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
