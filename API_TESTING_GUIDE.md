# API Testing Guide - AI Music Copilot

Complete guide for testing all API endpoints in your application.

---

## Prerequisites

### 1. Get Your Authentication Token

First, login to get a JWT token:

```bash
# Login (replace with your credentials)
curl -X POST http://localhost:8000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=your@email.com&password=yourpassword"
```

Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Save this token** - you'll use it in all subsequent requests as:
```bash
-H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

---

## Testing the Existing API (v2)

### 1. Complete Generation

Generate a full track with all layers:

```bash
curl -X POST http://localhost:8000/api/v2/generate/complete \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "dark techno beat at 130 BPM",
    "style": "techno",
    "bpm": 130,
    "bars": 8
  }'
```

Expected Response:
```json
{
  "generation_id": 123,
  "description": "dark techno beat at 130 BPM",
  "file_path": "storage/generations/generation_123_1234567890.mid",
  "download_url": "/api/v2/download/123",
  "metadata": {
    "bpm": 130,
    "bars": 8,
    "style": "techno",
    "layers": ["kick", "snare", "hat", "bass"]
  }
}
```

### 2. Layer Generation

Generate a single instrument layer:

```bash
curl -X POST http://localhost:8000/api/v2/generate/layer \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "instrument": "bass",
    "context": {
      "style": "techno",
      "bpm": 130,
      "key": "C",
      "scale": "minor"
    }
  }'
```

### 3. Download Generated Files

Download as MIDI:
```bash
curl http://localhost:8000/api/v2/download/123 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o output.mid
```

Download as ZIP (with project files):
```bash
curl http://localhost:8000/api/v2/download/123?format=zip \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o project.zip
```

### 4. Get Generation History

```bash
curl http://localhost:8000/api/history \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Testing the New Integrated MIDI Generator

### 1. Get Available Styles

```bash
curl http://localhost:8000/api/integrated-midi/styles
```

Expected Response:
```json
{
  "styles": ["techno", "trap", "house", "dnb", "lofi"],
  "description": "Supported music styles for integrated MIDI generation"
}
```

### 2. Get Available Instruments

```bash
curl http://localhost:8000/api/integrated-midi/instruments
```

Expected Response:
```json
{
  "drum_instruments": ["kick", "snare", "hat", "clap", "rim", "tom", "crash", "ride", "perc", "drums"],
  "melodic_instruments": ["bass", "melody", "lead", "pad", "synth"],
  "description": "Supported instruments for integrated MIDI generation"
}
```

### 3. Get DNA Presets

```bash
curl http://localhost:8000/api/integrated-midi/presets
```

Expected Response:
```json
{
  "presets": {
    "minimal": {
      "density": 0.3,
      "complexity": 0.2,
      "evolution": 0.1,
      "description": "Sparse, simple patterns"
    },
    "balanced": {
      "density": 0.6,
      "complexity": 0.5,
      "evolution": 0.3,
      "description": "Standard complexity patterns"
    },
    "complex": {
      "density": 0.9,
      "complexity": 0.8,
      "evolution": 0.5,
      "description": "Dense, evolving patterns"
    },
    "groovy": {
      "density": 0.7,
      "complexity": 0.5,
      "groove": 0.4,
      "velocity_curve": "accent",
      "description": "Swung, groovy patterns"
    }
  }
}
```

### 4. Quick Generate (Simple)

One-click generation with smart defaults:

```bash
curl -X POST "http://localhost:8000/api/integrated-midi/quick-generate?description=dark%20techno%20kick&style=techno" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Expected Response:
```json
{
  "success": true,
  "generation_id": 456,
  "file_path": "storage/integrated_midi/dark_techno_kick_kick_1_1234567890.mid",
  "download_url": "/api/integrated-midi/download/456",
  "message": "MIDI pattern generated successfully",
  "metadata": {
    "description": "dark techno kick",
    "style": "techno",
    "instrument": "kick",
    "bpm": 130,
    "bars": 4,
    "key": "C",
    "scale": "minor",
    "tracks": 2,
    "used_dna": null,
    "humanized": null
  }
}
```

### 5. Full Generation (Advanced)

Complete control over all DNA parameters:

```bash
curl -X POST http://localhost:8000/api/integrated-midi/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "rolling trap hi-hats",
    "style": "trap",
    "instrument": "hat",
    "bpm": 140,
    "bars": 8,
    "use_dna": true,
    "humanize": true,
    "density": 0.9,
    "complexity": 0.8,
    "groove": 0.3,
    "evolution": 0.4,
    "velocity_curve": "exponential",
    "musical_key": "A",
    "musical_scale": "minor"
  }'
```

### 6. Download Pattern

```bash
curl http://localhost:8000/api/integrated-midi/download/456 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o pattern.mid
```

---

## Testing Scenarios

### Scenario 1: Complete Track Workflow

```bash
# Step 1: Generate complete track
TRACK_ID=$(curl -X POST http://localhost:8000/api/v2/generate/complete \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"description": "aggressive techno track", "bpm": 135}' \
  | jq -r '.generation_id')

# Step 2: Download as ZIP
curl http://localhost:8000/api/v2/download/$TRACK_ID?format=zip \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o track_$TRACK_ID.zip

echo "Downloaded track_$TRACK_ID.zip"
```

### Scenario 2: Pattern Collection Workflow

```bash
# Generate multiple patterns for a track
TOKEN="YOUR_TOKEN"

# Kick pattern
curl -X POST "http://localhost:8000/api/integrated-midi/quick-generate?description=powerful%20kick&style=techno" \
  -H "Authorization: Bearer $TOKEN" | jq

# Hat pattern
curl -X POST "http://localhost:8000/api/integrated-midi/quick-generate?description=fast%20hats&style=techno" \
  -H "Authorization: Bearer $TOKEN" | jq

# Bass pattern
curl -X POST http://localhost:8000/api/integrated-midi/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "deep rolling bass",
    "style": "techno",
    "instrument": "bass",
    "bpm": 130,
    "bars": 8,
    "density": 0.6,
    "complexity": 0.7,
    "musical_key": "A",
    "musical_scale": "minor"
  }' | jq
```

### Scenario 3: Variation Generation

Generate variations of the same pattern:

```bash
TOKEN="YOUR_TOKEN"

# Minimal version
curl -X POST http://localhost:8000/api/integrated-midi/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "techno kick",
    "style": "techno",
    "instrument": "kick",
    "bpm": 130,
    "bars": 4,
    "density": 0.3,
    "complexity": 0.2
  }' | jq > minimal.json

# Complex version
curl -X POST http://localhost:8000/api/integrated-midi/generate \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "techno kick",
    "style": "techno",
    "instrument": "kick",
    "bpm": 130,
    "bars": 4,
    "density": 0.9,
    "complexity": 0.8,
    "evolution": 0.6
  }' | jq > complex.json
```

---

## Testing with Postman

### Import Collection

Create a Postman collection with these settings:

**Collection Variables:**
- `baseUrl`: `http://localhost:8000`
- `token`: `<your-jwt-token>`

**Authorization (Collection Level):**
- Type: Bearer Token
- Token: `{{token}}`

### Example Requests

1. **Login**
   - Method: POST
   - URL: `{{baseUrl}}/token`
   - Body (x-www-form-urlencoded):
     - `username`: your@email.com
     - `password`: yourpassword

2. **Quick Generate Pattern**
   - Method: POST
   - URL: `{{baseUrl}}/api/integrated-midi/quick-generate?description=techno kick&style=techno`
   - Headers: Authorization: Bearer {{token}}

3. **Advanced Generate**
   - Method: POST
   - URL: `{{baseUrl}}/api/integrated-midi/generate`
   - Headers:
     - Authorization: Bearer {{token}}
     - Content-Type: application/json
   - Body (JSON):
     ```json
     {
       "description": "dark techno kick",
       "style": "techno",
       "instrument": "kick",
       "bpm": 130,
       "bars": 4,
       "use_dna": true,
       "humanize": true,
       "density": 0.7,
       "complexity": 0.6
     }
     ```

---

## Testing with Browser (Swagger UI)

The easiest way to test is using the built-in Swagger UI:

1. **Start Backend**:
   ```bash
   cd backend
   venv\Scripts\activate
   uvicorn main:app --reload
   ```

2. **Open Swagger UI**:
   - Navigate to: http://localhost:8000/docs

3. **Authenticate**:
   - Click "Authorize" button (top right)
   - Login via `/token` endpoint
   - Copy the access_token
   - Paste into "Value" field
   - Click "Authorize"

4. **Test Endpoints**:
   - Expand any endpoint
   - Click "Try it out"
   - Fill in parameters
   - Click "Execute"
   - See response below

---

## Testing Error Handling

### Test Invalid Token

```bash
curl -X POST http://localhost:8000/api/integrated-midi/quick-generate?description=test&style=techno \
  -H "Authorization: Bearer invalid_token"
```

Expected: 401 Unauthorized

### Test Invalid Style

```bash
curl -X POST http://localhost:8000/api/integrated-midi/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "test",
    "style": "invalid_style",
    "instrument": "kick",
    "bpm": 130,
    "bars": 4
  }'
```

Expected: 400 Bad Request or validation error

### Test Missing Required Fields

```bash
curl -X POST http://localhost:8000/api/integrated-midi/generate \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "test"
  }'
```

Expected: 422 Unprocessable Entity (validation error)

---

## Performance Testing

### Test Response Times

```bash
# Time a quick generate
time curl -X POST "http://localhost:8000/api/integrated-midi/quick-generate?description=kick&style=techno" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

Expected: < 2 seconds for pattern generation

### Concurrent Requests

```bash
# Generate 5 patterns concurrently
for i in {1..5}; do
  curl -X POST "http://localhost:8000/api/integrated-midi/quick-generate?description=pattern$i&style=techno" \
    -H "Authorization: Bearer YOUR_TOKEN" &
done
wait
```

---

## Automated Test Script

Save as `test_api.sh`:

```bash
#!/bin/bash

# Configuration
BASE_URL="http://localhost:8000"
EMAIL="your@email.com"
PASSWORD="yourpassword"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Login and get token
echo "Logging in..."
TOKEN=$(curl -s -X POST "$BASE_URL/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$EMAIL&password=$PASSWORD" \
  | jq -r '.access_token')

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
  echo -e "${RED}[FAIL]${NC} Login failed"
  exit 1
fi
echo -e "${GREEN}[PASS]${NC} Login successful"

# Test 1: Get styles
echo "Testing get styles..."
STYLES=$(curl -s "$BASE_URL/api/integrated-midi/styles" | jq -r '.styles | length')
if [ "$STYLES" -gt 0 ]; then
  echo -e "${GREEN}[PASS]${NC} Get styles ($STYLES styles found)"
else
  echo -e "${RED}[FAIL]${NC} Get styles"
fi

# Test 2: Get instruments
echo "Testing get instruments..."
DRUMS=$(curl -s "$BASE_URL/api/integrated-midi/instruments" | jq -r '.drum_instruments | length')
if [ "$DRUMS" -gt 0 ]; then
  echo -e "${GREEN}[PASS]${NC} Get instruments ($DRUMS drum instruments found)"
else
  echo -e "${RED}[FAIL]${NC} Get instruments"
fi

# Test 3: Quick generate
echo "Testing quick generate..."
GEN_ID=$(curl -s -X POST "$BASE_URL/api/integrated-midi/quick-generate?description=test&style=techno" \
  -H "Authorization: Bearer $TOKEN" \
  | jq -r '.generation_id')

if [ "$GEN_ID" != "null" ] && [ -n "$GEN_ID" ]; then
  echo -e "${GREEN}[PASS]${NC} Quick generate (ID: $GEN_ID)"
else
  echo -e "${RED}[FAIL]${NC} Quick generate"
  exit 1
fi

# Test 4: Download
echo "Testing download..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  "$BASE_URL/api/integrated-midi/download/$GEN_ID" \
  -H "Authorization: Bearer $TOKEN")

if [ "$HTTP_CODE" == "200" ]; then
  echo -e "${GREEN}[PASS]${NC} Download (HTTP $HTTP_CODE)"
else
  echo -e "${RED}[FAIL]${NC} Download (HTTP $HTTP_CODE)"
fi

# Test 5: Advanced generate
echo "Testing advanced generate..."
ADV_ID=$(curl -s -X POST "$BASE_URL/api/integrated-midi/generate" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "test advanced",
    "style": "techno",
    "instrument": "kick",
    "bpm": 130,
    "bars": 4,
    "density": 0.7,
    "complexity": 0.6
  }' | jq -r '.generation_id')

if [ "$ADV_ID" != "null" ] && [ -n "$ADV_ID" ]; then
  echo -e "${GREEN}[PASS]${NC} Advanced generate (ID: $ADV_ID)"
else
  echo -e "${RED}[FAIL]${NC} Advanced generate"
fi

echo ""
echo "All tests completed!"
```

Make executable and run:
```bash
chmod +x test_api.sh
./test_api.sh
```

---

## Summary

You now have comprehensive testing coverage for:

- ✅ Existing v2 API (complete generation, layers, downloads)
- ✅ New Integrated MIDI API (patterns, DNA parameters, presets)
- ✅ Authentication
- ✅ Error handling
- ✅ Performance testing
- ✅ Automated test scripts

Choose your preferred testing method:
- **Quick testing**: Use Swagger UI at http://localhost:8000/docs
- **Command line**: Use curl commands above
- **API client**: Import into Postman
- **Automated**: Run the test script

All endpoints are documented and ready to test!
