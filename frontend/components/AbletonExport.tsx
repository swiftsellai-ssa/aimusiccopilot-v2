// frontend/components/AbletonExport.tsx
import { useState } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';
import { downloadWithProgress } from '../lib/axios-config';

interface AbletonExportProps {
  pattern: {
    genre?: string;
    style?: string;
    instrument?: string;
  };
  bpm: number;
  musical_key?: string;
  musical_scale?: string;
}

// Download icon component
const DownloadIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
          d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
  </svg>
);

export function AbletonExport({ pattern, bpm, musical_key = "C", musical_scale = "minor" }: AbletonExportProps) {
  const [loading, setLoading] = useState(false);
  const [projectType, setProjectType] = useState('full');
  const [downloadProgress, setDownloadProgress] = useState(0);

  const exportProject = async () => {
    setLoading(true);
    setDownloadProgress(0);
    const style = pattern.style || pattern.genre || 'techno';

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        toast.error('Please log in to download');
        setLoading(false);
        return;
      }

      const response = await axios.post(
        'http://localhost:8000/api/download/package',
        {
          project_name: `AI_${style}_${Date.now()}`,
          bpm: bpm,
          style: style,
          type: projectType,
          metadata: {
            key: musical_key,
            scale: musical_scale,
            instrument: pattern.instrument || 'full'
          }
        },
        {
          responseType: 'blob',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          },
          timeout: 30000,
          onDownloadProgress: (progressEvent) => {
            if (progressEvent.total) {
              const percentCompleted = Math.round(
                (progressEvent.loaded * 100) / progressEvent.total
              );
              setDownloadProgress(percentCompleted);
            }
          }
        }
      );

      // Create download link
      const blob = new Blob([response.data], { type: 'application/zip' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;

      // Generate filename with timestamp
      const timestamp = new Date().toISOString().split('T')[0];
      link.setAttribute('download', `${style}_${bpm}bpm_${timestamp}.zip`);

      document.body.appendChild(link);
      link.click();
      link.parentNode?.removeChild(link);

      // Clean up
      window.URL.revokeObjectURL(url);

      toast.success('Project downloaded successfully!');

    } catch (error: any) {
      console.error('Export failed:', error);

      if (error.response?.status === 401) {
        toast.error('Session expired. Please log in again.');
      } else if (error.code === 'ECONNABORTED') {
        toast.error('Download timeout. Please try again.');
      } else {
        toast.error('Export failed. Please try again.');
      }
    } finally {
      setLoading(false);
      setDownloadProgress(0);
    }
  };

  return (
    <div className="bg-gradient-to-b from-neutral-900 to-neutral-950 p-5 rounded-xl border border-neutral-800">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-bold">Export Project</h3>
        <span className="text-xs text-green-400 uppercase font-bold">Ready</span>
      </div>
      
      <div className="space-y-4">
        {/* Project type selector */}
        <div>
          <label className="block text-xs text-neutral-400 mb-2 uppercase tracking-wider">
            Export Type
          </label>
          <select 
            value={projectType}
            onChange={(e) => setProjectType(e.target.value)}
            className="w-full p-3 bg-black/50 border border-neutral-800 rounded-lg text-sm focus:border-blue-500 focus:outline-none transition-colors"
          >
            <option value="full">Full Project Pack</option>
            <option value="midi">MIDI Files Only</option>
            <option value="stems">Separated Stems</option>
            <option value="minimal">Minimal Template</option>
          </select>
        </div>
        
        {/* Info display */}
        <div className="grid grid-cols-2 gap-3 text-xs">
          <div className="bg-black/30 p-3 rounded-lg">
            <span className="text-neutral-500">Style:</span>
            <p className="font-bold text-neutral-300">{pattern.style || pattern.genre || 'Custom'}</p>
          </div>
          <div className="bg-black/30 p-3 rounded-lg">
            <span className="text-neutral-500">Tempo:</span>
            <p className="font-bold text-neutral-300">{bpm} BPM</p>
          </div>
          <div className="bg-black/30 p-3 rounded-lg">
            <span className="text-neutral-500">Key:</span>
            <p className="font-bold text-neutral-300">{musical_key} {musical_scale}</p>
          </div>
          <div className="bg-black/30 p-3 rounded-lg">
            <span className="text-neutral-500">Type:</span>
            <p className="font-bold text-neutral-300">{pattern.instrument || 'Full'}</p>
          </div>
        </div>
        
        {/* Progress bar */}
        {loading && downloadProgress > 0 && (
          <div className="space-y-2">
            <div className="flex justify-between text-xs text-neutral-400">
              <span>Downloading...</span>
              <span>{downloadProgress}%</span>
            </div>
            <div className="w-full bg-neutral-800 rounded-full h-2 overflow-hidden">
              <div
                className="bg-gradient-to-r from-green-500 to-emerald-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${downloadProgress}%` }}
              />
            </div>
          </div>
        )}

        {/* Download button */}
        <button
          onClick={exportProject}
          disabled={loading}
          className={`
            w-full flex items-center justify-center gap-3 py-4 rounded-lg
            font-bold text-sm transition-all duration-200
            ${loading
              ? 'bg-neutral-800 text-neutral-500 cursor-not-allowed'
              : 'bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 text-white shadow-[0_0_20px_rgba(34,197,94,0.3)]'
            }
          `}
        >
          {loading ? (
            <>
              <div className="w-4 h-4 border-2 border-neutral-600 border-t-neutral-400 rounded-full animate-spin" />
              {downloadProgress > 0 ? `Downloading ${downloadProgress}%` : 'Preparing Download...'}
            </>
          ) : (
            <>
              <DownloadIcon />
              Download Project Pack
            </>
          )}
        </button>
        
        {/* Package contents */}
        <div className="text-xs text-neutral-500 space-y-1">
          <p className="font-bold text-neutral-400 mb-2">Package includes:</p>
          <p>✓ MIDI files for all tracks</p>
          <p>✓ Project structure & README</p>
          <p>✓ Production tips for {pattern.style || 'your style'}</p>
          <p>✓ Ready for Ableton Live 11/12</p>
        </div>
      </div>
    </div>
  );
}