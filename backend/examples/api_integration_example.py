"""
Example of integrating IntegratedMidiGenerator with FastAPI endpoints

This shows how to use the integrated generator in your API routes.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import os
import logging

from services.integrated_midi_generator import IntegratedMidiGenerator

# Create router
router = APIRouter(prefix="/api/midi", tags=["MIDI Generation"])

# Initialize generator (singleton pattern)
_generator = None

def get_generator() -> IntegratedMidiGenerator:
    """Get or create the MIDI generator instance"""
    global _generator
    if _generator is None:
        _generator = IntegratedMidiGenerator(enable_humanization=True)
        logging.info("Initialized IntegratedMidiGenerator")
    return _generator


# Request/Response models
class MidiGenerationRequest(BaseModel):
    """Request model for MIDI generation"""
    description: str = Field(..., description="Text description of pattern", example="dark techno kick")
    style: Optional[str] = Field(None, description="Music style", example="techno")
    instrument: Optional[str] = Field(None, description="Instrument type", example="kick")
    use_dna: Optional[bool] = Field(None, description="Use DNA-based generation")
    humanize: Optional[bool] = Field(None, description="Apply humanization")

    # DNA parameters
    density: Optional[float] = Field(0.7, ge=0.0, le=1.0, description="Note density")
    complexity: Optional[float] = Field(0.5, ge=0.0, le=1.0, description="Pattern complexity")
    groove: Optional[float] = Field(0.2, ge=0.0, le=1.0, description="Swing/groove amount")
    velocity_curve: Optional[str] = Field("natural", description="Velocity pattern")
    evolution: Optional[float] = Field(0.3, ge=0.0, le=1.0, description="Pattern evolution")

    # Musical parameters
    bpm: Optional[int] = Field(120, ge=40, le=300, description="Tempo in BPM")
    bars: Optional[int] = Field(4, ge=1, le=32, description="Number of bars")
    musical_key: Optional[str] = Field("C", description="Musical key")
    musical_scale: Optional[str] = Field("minor", description="Musical scale")


class MidiGenerationResponse(BaseModel):
    """Response model for MIDI generation"""
    success: bool
    file_path: str
    message: str
    metadata: dict


# Endpoints
@router.post("/generate", response_model=MidiGenerationResponse)
async def generate_midi(request: MidiGenerationRequest):
    """
    Generate a MIDI file based on text description and parameters.

    Returns the file path to the generated MIDI file.
    """
    try:
        generator = get_generator()

        # Prepare kwargs
        kwargs = {
            "style": request.style,
            "instrument": request.instrument,
            "density": request.density,
            "complexity": request.complexity,
            "groove": request.groove,
            "velocity_curve": request.velocity_curve,
            "evolution": request.evolution,
            "bpm": request.bpm,
            "bars": request.bars,
            "musical_key": request.musical_key,
            "musical_scale": request.musical_scale,
        }

        # Remove None values
        kwargs = {k: v for k, v in kwargs.items() if v is not None}

        # Generate MIDI
        logging.info(f"Generating MIDI: {request.description}")
        midi_file = generator.generate(
            description=request.description,
            use_dna=request.use_dna,
            humanize=request.humanize,
            **kwargs
        )

        # Save file
        output_dir = "output/api_generated"
        os.makedirs(output_dir, exist_ok=True)

        # Create filename from description
        safe_name = "".join(c for c in request.description if c.isalnum() or c in (' ', '-', '_'))
        safe_name = safe_name.replace(' ', '_')[:50]
        file_path = f"{output_dir}/{safe_name}.mid"

        # Save
        midi_file.save(file_path)

        # Prepare response
        return MidiGenerationResponse(
            success=True,
            file_path=file_path,
            message=f"Successfully generated MIDI pattern",
            metadata={
                "description": request.description,
                "style": kwargs.get("style"),
                "instrument": kwargs.get("instrument"),
                "bpm": kwargs.get("bpm"),
                "bars": kwargs.get("bars"),
                "used_dna": request.use_dna,
                "humanized": request.humanize,
            }
        )

    except ValueError as e:
        logging.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logging.error(f"Generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate MIDI: {str(e)}")


@router.get("/styles")
async def get_supported_styles():
    """Get list of supported music styles"""
    generator = get_generator()
    return {
        "styles": list(generator.SUPPORTED_STYLES),
        "description": "Supported music styles for generation"
    }


@router.get("/instruments")
async def get_supported_instruments():
    """Get list of supported instruments"""
    generator = get_generator()
    return {
        "drum_instruments": list(generator.DRUM_INSTRUMENTS),
        "melodic_instruments": list(generator.MELODIC_INSTRUMENTS),
        "description": "Supported instruments for generation"
    }


# Example usage in main FastAPI app:
"""
from fastapi import FastAPI
from examples.api_integration_example import router as midi_router

app = FastAPI(title="AI Music Copilot")
app.include_router(midi_router)

# Then test with:
# POST http://localhost:8000/api/midi/generate
# {
#     "description": "dark techno kick",
#     "style": "techno",
#     "instrument": "kick",
#     "bpm": 130,
#     "bars": 4,
#     "use_dna": true,
#     "humanize": true,
#     "complexity": 0.6
# }
"""


# Standalone test (if run directly)
if __name__ == "__main__":
    import asyncio

    async def test():
        """Test the endpoint logic"""
        print("Testing MIDI generation...")

        request = MidiGenerationRequest(
            description="dark techno kick",
            style="techno",
            instrument="kick",
            bpm=130,
            bars=4,
            use_dna=True,
            complexity=0.6
        )

        response = await generate_midi(request)
        print(f"✓ Generated: {response.file_path}")
        print(f"  Metadata: {response.metadata}")

    asyncio.run(test())
