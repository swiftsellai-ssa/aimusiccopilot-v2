export interface MusicStyle {
    id: string;
    label: string;
    category: 'Electronic' | 'Pop/Rock' | 'Urban' | 'Jazz/Soul' | 'World' | 'Hard' | 'Score';
    bpm: number; // Default BPM for smart-setting
}

export const MUSIC_STYLES: MusicStyle[] = [
    // ELECTRONIC
    { id: 'techno', label: 'Techno', category: 'Electronic', bpm: 130 },
    { id: 'house', label: 'House', category: 'Electronic', bpm: 124 },
    { id: 'deep_house', label: 'Deep House', category: 'Electronic', bpm: 120 },
    { id: 'trap', label: 'Trap', category: 'Electronic', bpm: 140 },
    { id: 'dnb', label: 'DnB', category: 'Electronic', bpm: 174 },
    { id: 'dubstep', label: 'Dubstep', category: 'Electronic', bpm: 140 },
    { id: 'ambient', label: 'Ambient', category: 'Electronic', bpm: 80 },

    // POP/ROCK
    { id: 'pop', label: 'Pop', category: 'Pop/Rock', bpm: 110 },
    { id: 'rock', label: 'Rock', category: 'Pop/Rock', bpm: 120 },
    { id: 'indie', label: 'Indie', category: 'Pop/Rock', bpm: 105 },
    { id: 'funk', label: 'Funk', category: 'Pop/Rock', bpm: 115 },
    { id: 'disco', label: 'Disco', category: 'Pop/Rock', bpm: 120 },

    // URBAN
    { id: 'hip_hop', label: 'Hip Hop', category: 'Urban', bpm: 90 },
    { id: 'boom_bap', label: 'Boom Bap', category: 'Urban', bpm: 88 },
    { id: 'lofi', label: 'Lofi', category: 'Urban', bpm: 85 },
    { id: 'rnb', label: 'RnB', category: 'Urban', bpm: 95 },

    // JAZZ/SOUL
    { id: 'jazz', label: 'Jazz', category: 'Jazz/Soul', bpm: 120 },
    { id: 'soul', label: 'Soul', category: 'Jazz/Soul', bpm: 100 },
    { id: 'gospel', label: 'Gospel', category: 'Jazz/Soul', bpm: 110 },

    // WORLD
    { id: 'reggaeton', label: 'Reggaeton', category: 'World', bpm: 96 },
    { id: 'latin', label: 'Latin', category: 'World', bpm: 100 },
    { id: 'afrobeat', label: 'Afrobeat', category: 'World', bpm: 115 },

    // HARD
    { id: 'metal', label: 'Metal', category: 'Hard', bpm: 140 },
    { id: 'punk', label: 'Punk', category: 'Hard', bpm: 160 },

    // SCORE
    { id: 'cinematic', label: 'Cinematic', category: 'Score', bpm: 70 },
];

// Helper to get styles by category for the UI grid
export const getStylesByCategory = () => {
    const groups: Record<string, MusicStyle[]> = {};
    MUSIC_STYLES.forEach(style => {
        if (!groups[style.category]) groups[style.category] = [];
        groups[style.category].push(style);
    });
    return groups;
};