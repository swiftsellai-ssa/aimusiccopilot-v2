# Next.js Integration Guide for IntegratedMidiGenerator

## Overview

This guide shows you how to integrate the IntegratedMidiGenerator component into your existing Next.js application structure.

---

## Files Created

### 1. TypeScript Version (Recommended for Next.js)
- **Location**: `frontend/src/components/IntegratedMidiGenerator.tsx`
- **Type**: Next.js compatible React component with 'use client' directive
- **Styling**: Uses existing `IntegratedMidiGenerator.css`

### 2. Original JavaScript Version
- **Location**: `frontend/src/components/IntegratedMidiGenerator.jsx`
- **Type**: Standard React component (also works with Next.js)

---

## Integration Options

### Option 1: Add to Existing page.tsx (Recommended)

Add the IntegratedMidiGenerator alongside your existing components:

```tsx
// frontend/app/page.tsx
'use client';

import { useState } from 'react';
import MusicPlayer from '@/components/MusicPlayer';
import MidiVisualizer from '@/components/MidiVisualizer';
import RecommendationPanel from '@/components/RecommendationPanel';
import AbletonExport from '@/components/AbletonExport';
import PatternDNA from '@/components/PatternDNA';
import IntegratedMidiGenerator from '@/components/IntegratedMidiGenerator';
import axios from 'axios';

export default function Home() {
  const [generatedMidi, setGeneratedMidi] = useState(null);
  const [showIntegratedGenerator, setShowIntegratedGenerator] = useState(false);

  // Your existing generate function
  const handleGenerate = async (prompt: string) => {
    const token = localStorage.getItem('token');
    const response = await axios.post('/api/v2/generate/complete',
      { prompt },
      { headers: { Authorization: `Bearer ${token}` } }
    );
    setGeneratedMidi(response.data);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black text-white">
      <main className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-center mb-8">
          AI Music Copilot
        </h1>

        {/* Toggle between generators */}
        <div className="flex justify-center gap-4 mb-8">
          <button
            onClick={() => setShowIntegratedGenerator(false)}
            className={`px-6 py-3 rounded-lg ${!showIntegratedGenerator ? 'bg-blue-600' : 'bg-gray-700'}`}
          >
            Complete Generator
          </button>
          <button
            onClick={() => setShowIntegratedGenerator(true)}
            className={`px-6 py-3 rounded-lg ${showIntegratedGenerator ? 'bg-blue-600' : 'bg-gray-700'}`}
          >
            Pattern Generator (DNA)
          </button>
        </div>

        {/* Conditional rendering */}
        {showIntegratedGenerator ? (
          // New IntegratedMidiGenerator
          <IntegratedMidiGenerator />
        ) : (
          // Your existing components
          <div className="space-y-8">
            <MusicPlayer onGenerate={handleGenerate} />
            {generatedMidi && (
              <>
                <MidiVisualizer midiData={generatedMidi} />
                <PatternDNA dnaData={generatedMidi.dna} />
                <AbletonExport midiData={generatedMidi} />
                <RecommendationPanel />
              </>
            )}
          </div>
        )}
      </main>
    </div>
  );
}
```

---

### Option 2: Create Separate Route

Create a dedicated page for the pattern generator:

```bash
# Create new route
mkdir -p frontend/app/pattern-generator
```

```tsx
// frontend/app/pattern-generator/page.tsx
'use client';

import IntegratedMidiGenerator from '@/components/IntegratedMidiGenerator';

export default function PatternGeneratorPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black text-white">
      <main className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-center mb-8">
          DNA Pattern Generator
        </h1>
        <IntegratedMidiGenerator />
      </main>
    </div>
  );
}
```

Then add navigation:

```tsx
// Add to your navigation component
<Link href="/pattern-generator">Pattern Generator</Link>
```

---

### Option 3: Tabs/Accordion Layout

Integrate as a tab in your existing layout:

```tsx
// frontend/app/page.tsx
'use client';

import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import IntegratedMidiGenerator from '@/components/IntegratedMidiGenerator';
// ... your other imports

export default function Home() {
  return (
    <div className="container mx-auto px-4 py-8">
      <Tabs defaultValue="complete">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="complete">Complete Generation</TabsTrigger>
          <TabsTrigger value="pattern">Pattern Generator</TabsTrigger>
        </TabsList>

        <TabsContent value="complete">
          {/* Your existing MusicPlayer, MidiVisualizer, etc. */}
        </TabsContent>

        <TabsContent value="pattern">
          <IntegratedMidiGenerator />
        </TabsContent>
      </Tabs>
    </div>
  );
}
```

---

## API Configuration

The component expects these backend endpoints to be available:

### Backend Endpoints (Already Integrated)
```
GET  /api/integrated-midi/styles
GET  /api/integrated-midi/instruments
GET  /api/integrated-midi/presets
POST /api/integrated-midi/generate
POST /api/integrated-midi/quick-generate
GET  /api/integrated-midi/download/{generation_id}
```

### Authentication
The component uses JWT tokens from localStorage:
```typescript
const token = localStorage.getItem('token');
axios.post(url, data, {
  headers: { Authorization: `Bearer ${token}` }
});
```

This matches your existing authentication pattern.

---

## Styling Integration

### Option A: Use Existing CSS (Already Set Up)
The component already uses `IntegratedMidiGenerator.css` which has professional styling.

### Option B: Tailwind Integration (Convert to Your Style)
If you prefer Tailwind (matching your existing components), you can convert:

```tsx
// Example conversion
<div className="integrated-midi-generator">
  // becomes
<div className="max-w-4xl mx-auto p-6">

<button className="btn btn-generate">
  // becomes
<button className="w-full bg-gradient-to-r from-green-500 to-green-600 text-white font-semibold py-4 px-6 rounded-lg hover:shadow-lg transition">
```

---

## Environment Setup

### 1. Move CSS to Next.js Structure

```bash
# If using src/ directory
cp frontend/src/components/IntegratedMidiGenerator.css frontend/src/app/globals.css
# Or import directly in component

# If not using src/ directory
cp frontend/src/components/IntegratedMidiGenerator.css frontend/app/globals.css
```

### 2. Update Import Paths

If your Next.js uses `@/components` aliasing:

```tsx
// IntegratedMidiGenerator.tsx
import './IntegratedMidiGenerator.css';
// No changes needed - relative imports work fine
```

---

## Testing the Integration

### 1. Start Backend
```bash
cd backend
venv\Scripts\activate
uvicorn main:app --reload
```

### 2. Start Frontend
```bash
cd frontend
npm run dev
```

### 3. Test Authentication
Make sure you're logged in:
- Go to your login page
- Login to get JWT token
- Token should be in localStorage
- Navigate to IntegratedMidiGenerator

### 4. Test Generation
- Try "Quick Generate" first
- Verify download works
- Test advanced parameters
- Check browser console for errors

---

## Common Issues & Solutions

### Issue 1: CORS Errors
If you see CORS errors, ensure backend allows frontend origin:

```python
# backend/main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your Next.js dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue 2: 401 Unauthorized
- Check token exists: `localStorage.getItem('token')`
- Verify token is valid (not expired)
- Check Authorization header format: `Bearer <token>`

### Issue 3: Download Not Working
The download function needs proper token handling:

```typescript
const handleDownload = async () => {
  const token = localStorage.getItem('token');
  if (result?.generation_id) {
    // Create a temporary link with auth
    const response = await axios.get(
      `/api/integrated-midi/download/${result.generation_id}`,
      {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob'
      }
    );

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.download = 'pattern.mid';
    link.click();
  }
};
```

### Issue 4: CSS Not Loading
Ensure CSS is imported:

```tsx
// At top of IntegratedMidiGenerator.tsx
import './IntegratedMidiGenerator.css';
```

Or add to global CSS:

```tsx
// app/layout.tsx
import '@/components/IntegratedMidiGenerator.css';
```

---

## Feature Comparison

### Your Existing Complete Generator
- Full song generation
- Multi-track output
- Recommendations
- Ableton export
- Pattern DNA display

### New Integrated Pattern Generator
- Single pattern focus (kicks, hats, bass, etc.)
- Advanced DNA parameters (density, complexity, groove, evolution)
- Humanization engine
- Multiple style support (techno, trap, house, dnb, lofi)
- Quick generation mode
- Preset system

### Best Use Together
1. Use **Complete Generator** for full tracks
2. Use **Pattern Generator** for individual elements
3. Combine patterns from Pattern Generator in your DAW
4. Use Pattern Generator to fill gaps in Complete Generator output

---

## Next Steps

1. Choose your preferred integration option (tabs recommended)
2. Add the component to your page
3. Test all functionality
4. Customize styling to match your design system
5. Add analytics/tracking if needed

---

## Example: Full Integration with Your Existing Code

```tsx
// frontend/app/page.tsx - Complete example
'use client';

import { useState } from 'react';
import axios from 'axios';
import { toast } from 'react-hot-toast';
import MusicPlayer from '@/components/MusicPlayer';
import MidiVisualizer from '@/components/MidiVisualizer';
import IntegratedMidiGenerator from '@/components/IntegratedMidiGenerator';

export default function Home() {
  const [activeTab, setActiveTab] = useState<'complete' | 'pattern'>('complete');
  const [generatedMidi, setGeneratedMidi] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleCompleteGeneration = async (prompt: string) => {
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.post(
        '/api/v2/generate/complete',
        { prompt },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setGeneratedMidi(response.data);
      toast.success('Track generated successfully!');
    } catch (error) {
      toast.error('Generation failed');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-900 to-black text-white">
      <main className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold text-center mb-8">
          AI Music Copilot
        </h1>

        {/* Tab Navigation */}
        <div className="flex justify-center gap-4 mb-8">
          <button
            onClick={() => setActiveTab('complete')}
            className={`px-6 py-3 rounded-lg font-semibold transition ${
              activeTab === 'complete'
                ? 'bg-blue-600 text-white shadow-lg'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            🎼 Complete Track
          </button>
          <button
            onClick={() => setActiveTab('pattern')}
            className={`px-6 py-3 rounded-lg font-semibold transition ${
              activeTab === 'pattern'
                ? 'bg-blue-600 text-white shadow-lg'
                : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            🧬 Pattern Generator
          </button>
        </div>

        {/* Content */}
        {activeTab === 'complete' ? (
          <div className="space-y-8">
            <MusicPlayer onGenerate={handleCompleteGeneration} loading={loading} />
            {generatedMidi && <MidiVisualizer midiData={generatedMidi} />}
          </div>
        ) : (
          <IntegratedMidiGenerator />
        )}
      </main>
    </div>
  );
}
```

---

## Summary

Your IntegratedMidiGenerator is now fully integrated and ready to use! Choose the integration option that best fits your application structure and start generating DNA-based MIDI patterns.

For questions or issues, check:
- [INTEGRATION_COMPLETE.md](backend/INTEGRATION_COMPLETE.md)
- [QUICKSTART_INTEGRATED.md](backend/QUICKSTART_INTEGRATED.md)
- [QUICK_REFERENCE.md](backend/services/QUICK_REFERENCE.md)
