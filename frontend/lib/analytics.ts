// frontend/lib/analytics.ts
/**
 * Analytics tracking utilities for AI Music Copilot
 * Automatically tracks user behavior and preferences
 */

import axios from 'axios';

const API_BASE = 'http://localhost:8000';

export interface GenerationTrackingData {
  mode: 'simple' | 'advanced';
  generation_type: 'drums' | 'bass' | 'melody' | 'full';
  style: string;
  bpm: number;
  musical_key?: string;
  musical_scale?: string;

  // DNA parameters (optional)
  density?: number;
  complexity?: number;
  groove?: number;
  evolution?: number;
  bars?: number;

  // Outcome
  success: boolean;
  error_message?: string;
  generation_time_ms?: number;
}

export interface InteractionTrackingData {
  event_id: number;
  action: 'download' | 'play' | 'stop';
  play_duration_seconds?: number;
}

class Analytics {
  private sessionId: number | null = null;
  private currentEventId: number | null = null;
  private playStartTime: number | null = null;

  /**
   * Initialize analytics session
   */
  async startSession(): Promise<void> {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      const response = await axios.post(
        `${API_BASE}/api/analytics/track/session/start`,
        {},
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      this.sessionId = response.data.session_id;
      console.log('📊 Analytics session started:', this.sessionId);
    } catch (error) {
      console.error('Failed to start analytics session:', error);
    }
  }

  /**
   * End analytics session
   */
  async endSession(): Promise<void> {
    if (!this.sessionId) return;

    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      await axios.post(
        `${API_BASE}/api/analytics/track/session/end/${this.sessionId}`,
        {},
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      console.log('📊 Analytics session ended');
      this.sessionId = null;
    } catch (error) {
      console.error('Failed to end analytics session:', error);
    }
  }

  /**
   * Track a MIDI generation event
   */
  async trackGeneration(data: GenerationTrackingData): Promise<number | null> {
    try {
      const token = localStorage.getItem('token');
      if (!token) return null;

      const response = await axios.post(
        `${API_BASE}/api/analytics/track/generation`,
        data,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      this.currentEventId = response.data.event_id;
      console.log('📊 Generation tracked:', this.currentEventId);

      return this.currentEventId;
    } catch (error) {
      console.error('Failed to track generation:', error);
      return null;
    }
  }

  /**
   * Track user interaction (download, play, stop)
   */
  async trackInteraction(data: InteractionTrackingData): Promise<void> {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;

      await axios.post(
        `${API_BASE}/api/analytics/track/interaction`,
        data,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      console.log(`📊 Interaction tracked: ${data.action}`);
    } catch (error) {
      console.error('Failed to track interaction:', error);
    }
  }

  /**
   * Track download action
   */
  async trackDownload(eventId?: number): Promise<void> {
    const id = eventId || this.currentEventId;
    if (!id) return;

    await this.trackInteraction({
      event_id: id,
      action: 'download'
    });
  }

  /**
   * Track play start
   */
  async trackPlayStart(eventId?: number): Promise<void> {
    const id = eventId || this.currentEventId;
    if (!id) return;

    this.playStartTime = Date.now();

    await this.trackInteraction({
      event_id: id,
      action: 'play'
    });
  }

  /**
   * Track play stop (with duration)
   */
  async trackPlayStop(eventId?: number): Promise<void> {
    const id = eventId || this.currentEventId;
    if (!id || !this.playStartTime) return;

    const duration = (Date.now() - this.playStartTime) / 1000; // Convert to seconds

    await this.trackInteraction({
      event_id: id,
      action: 'stop',
      play_duration_seconds: duration
    });

    this.playStartTime = null;
  }

  /**
   * Get analytics summary
   */
  async getSummary(days: number = 30): Promise<any> {
    try {
      const token = localStorage.getItem('token');
      if (!token) return null;

      const response = await axios.get(
        `${API_BASE}/api/analytics/summary?days=${days}`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      return response.data;
    } catch (error) {
      console.error('Failed to get analytics summary:', error);
      return null;
    }
  }

  /**
   * Get personalized insights
   */
  async getInsights(days: number = 30): Promise<any> {
    try {
      const token = localStorage.getItem('token');
      if (!token) return null;

      const response = await axios.get(
        `${API_BASE}/api/analytics/insights?days=${days}`,
        {
          headers: { 'Authorization': `Bearer ${token}` }
        }
      );

      return response.data;
    } catch (error) {
      console.error('Failed to get insights:', error);
      return null;
    }
  }

  /**
   * Set current event ID (used after generation)
   */
  setCurrentEventId(eventId: number): void {
    this.currentEventId = eventId;
  }

  /**
   * Get current event ID
   */
  getCurrentEventId(): number | null {
    return this.currentEventId;
  }
}

// Singleton instance
export const analytics = new Analytics();
