// frontend/components/AnalyticsDashboard.tsx
'use client';

import { useState, useEffect } from 'react';
import { analytics } from '@/lib/analytics';

interface AnalyticsSummary {
  total_generations: number;
  successful_generations: number;
  failed_generations: number;
  success_rate: number;

  simple_mode_percentage: number;
  advanced_mode_percentage: number;

  most_popular_type: string;
  most_popular_style: string;
  most_popular_key: string | null;
  most_popular_scale: string | null;

  avg_bpm: number;
  avg_generation_time_ms: number;

  avg_density: number | null;
  avg_complexity: number | null;
  avg_groove: number | null;
  avg_evolution: number | null;
  avg_bars: number | null;

  download_rate: number;
  play_rate: number;
  avg_play_duration: number | null;

  period_days: number;
}

interface Insights {
  insights: string[];
  recommendations: string[];
  period_days: number;
}

export default function AnalyticsDashboard() {
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [insights, setInsights] = useState<Insights | null>(null);
  const [loading, setLoading] = useState(true);
  const [period, setPeriod] = useState(30);

  useEffect(() => {
    loadAnalytics();
  }, [period]);

  const loadAnalytics = async () => {
    setLoading(true);
    try {
      console.log('📊 Loading analytics for period:', period);
      const [summaryData, insightsData] = await Promise.all([
        analytics.getSummary(period),
        analytics.getInsights(period)
      ]);

      console.log('📊 Analytics loaded:', { summaryData, insightsData });
      setSummary(summaryData);
      setInsights(insightsData);
    } catch (error) {
      console.error('❌ Failed to load analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-gray-900 p-6 rounded-lg border border-gray-800">
        <div className="animate-pulse text-center py-8">
          <div className="text-4xl mb-2">📊</div>
          <p className="text-gray-400">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (!summary) {
    return (
      <div className="bg-gray-900 p-6 rounded-lg border border-gray-800">
        <p className="text-gray-400 text-center">No analytics data available yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gray-900 p-6 rounded-lg border border-gray-800">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold">📊 Your Analytics</h2>

          {/* Period Selector */}
          <div className="flex gap-2">
            {[7, 30, 90].map((days) => (
              <button
                key={days}
                onClick={() => setPeriod(days)}
                className={`px-4 py-2 rounded-lg text-sm transition-all ${
                  period === days
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}
              >
                {days}d
              </button>
            ))}
          </div>
        </div>

        {/* Overview Stats */}
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-gray-800 p-4 rounded-lg">
            <div className="text-3xl font-bold text-blue-400">{summary.total_generations}</div>
            <div className="text-sm text-gray-400">Total Generations</div>
          </div>

          <div className="bg-gray-800 p-4 rounded-lg">
            <div className="text-3xl font-bold text-green-400">
              {summary.success_rate.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-400">Success Rate</div>
          </div>

          <div className="bg-gray-800 p-4 rounded-lg">
            <div className="text-3xl font-bold text-purple-400">
              {summary.download_rate.toFixed(1)}%
            </div>
            <div className="text-sm text-gray-400">Download Rate</div>
          </div>

          <div className="bg-gray-800 p-4 rounded-lg">
            <div className="text-3xl font-bold text-yellow-400">
              {summary.avg_bpm.toFixed(0)}
            </div>
            <div className="text-sm text-gray-400">Avg BPM</div>
          </div>
        </div>
      </div>

      {/* Mode Breakdown */}
      <div className="bg-gray-900 p-6 rounded-lg border border-gray-800">
        <h3 className="text-xl font-bold mb-4">Mode Usage</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gray-800 p-4 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-400">🎹 Simple Mode</span>
              <span className="font-bold text-blue-400">
                {summary.simple_mode_percentage.toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className="bg-blue-500 h-2 rounded-full"
                style={{ width: `${summary.simple_mode_percentage}%` }}
              />
            </div>
          </div>

          <div className="bg-gray-800 p-4 rounded-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="text-gray-400">🧬 DNA Mode</span>
              <span className="font-bold text-purple-400">
                {summary.advanced_mode_percentage.toFixed(1)}%
              </span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className="bg-purple-500 h-2 rounded-full"
                style={{ width: `${summary.advanced_mode_percentage}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Favorites */}
      <div className="bg-gray-900 p-6 rounded-lg border border-gray-800">
        <h3 className="text-xl font-bold mb-4">Your Favorites</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gray-800 p-4 rounded-lg">
            <div className="text-sm text-gray-400 mb-1">Most Popular Type</div>
            <div className="text-2xl font-bold capitalize">
              {summary.most_popular_type === 'drums' && '🥁'}
              {summary.most_popular_type === 'bass' && '🎸'}
              {summary.most_popular_type === 'melody' && '🎹'}
              {summary.most_popular_type === 'full' && '🎼'}
              {' '}
              {summary.most_popular_type}
            </div>
          </div>

          <div className="bg-gray-800 p-4 rounded-lg">
            <div className="text-sm text-gray-400 mb-1">Favorite Style</div>
            <div className="text-2xl font-bold capitalize">{summary.most_popular_style}</div>
          </div>

          {summary.most_popular_key && (
            <div className="bg-gray-800 p-4 rounded-lg">
              <div className="text-sm text-gray-400 mb-1">Favorite Key</div>
              <div className="text-2xl font-bold">{summary.most_popular_key}</div>
            </div>
          )}

          {summary.most_popular_scale && (
            <div className="bg-gray-800 p-4 rounded-lg">
              <div className="text-sm text-gray-400 mb-1">Favorite Scale</div>
              <div className="text-2xl font-bold capitalize">{summary.most_popular_scale}</div>
            </div>
          )}
        </div>
      </div>

      {/* DNA Parameters (if using advanced mode) */}
      {summary.avg_density !== null && (
        <div className="bg-gray-900 p-6 rounded-lg border border-gray-800">
          <h3 className="text-xl font-bold mb-4">Average DNA Parameters</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-gray-800 p-4 rounded-lg">
              <div className="flex justify-between mb-2">
                <span className="text-gray-400">Density</span>
                <span className="font-bold text-purple-400">
                  {summary.avg_density?.toFixed(2)}
                </span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div
                  className="bg-purple-500 h-2 rounded-full"
                  style={{ width: `${(summary.avg_density || 0) * 100}%` }}
                />
              </div>
            </div>

            <div className="bg-gray-800 p-4 rounded-lg">
              <div className="flex justify-between mb-2">
                <span className="text-gray-400">Complexity</span>
                <span className="font-bold text-purple-400">
                  {summary.avg_complexity?.toFixed(2)}
                </span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div
                  className="bg-purple-500 h-2 rounded-full"
                  style={{ width: `${(summary.avg_complexity || 0) * 100}%` }}
                />
              </div>
            </div>

            <div className="bg-gray-800 p-4 rounded-lg">
              <div className="flex justify-between mb-2">
                <span className="text-gray-400">Groove</span>
                <span className="font-bold text-purple-400">
                  {summary.avg_groove?.toFixed(2)}
                </span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div
                  className="bg-purple-500 h-2 rounded-full"
                  style={{ width: `${(summary.avg_groove || 0) * 100}%` }}
                />
              </div>
            </div>

            <div className="bg-gray-800 p-4 rounded-lg">
              <div className="flex justify-between mb-2">
                <span className="text-gray-400">Evolution</span>
                <span className="font-bold text-purple-400">
                  {summary.avg_evolution?.toFixed(2)}
                </span>
              </div>
              <div className="w-full bg-gray-700 rounded-full h-2">
                <div
                  className="bg-purple-500 h-2 rounded-full"
                  style={{ width: `${(summary.avg_evolution || 0) * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Insights & Recommendations */}
      {insights && (insights.insights.length > 0 || insights.recommendations.length > 0) && (
        <div className="bg-gray-900 p-6 rounded-lg border border-gray-800">
          <h3 className="text-xl font-bold mb-4">💡 Insights & Recommendations</h3>

          {insights.insights.length > 0 && (
            <div className="mb-4">
              <h4 className="text-sm font-bold text-blue-400 mb-2">Insights:</h4>
              <ul className="space-y-2">
                {insights.insights.map((insight, i) => (
                  <li key={i} className="text-gray-300 flex items-start gap-2">
                    <span className="text-blue-400">•</span>
                    {insight}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {insights.recommendations.length > 0 && (
            <div>
              <h4 className="text-sm font-bold text-green-400 mb-2">Try This:</h4>
              <ul className="space-y-2">
                {insights.recommendations.map((rec, i) => (
                  <li key={i} className="text-gray-300 flex items-start gap-2">
                    <span className="text-green-400">→</span>
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
