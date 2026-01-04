
import sys
import os
import logging

# Setup path
sys.path.append(os.path.join(os.path.dirname(__file__)))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("TestWiringV2")

def test_v2_generation_args():
    logger.info("--- Testing V2 Generation Wiring ---")
    from services.integrated_midi_generator import IntegratedMidiGenerator
    
    generator = IntegratedMidiGenerator()
    
    # Simulate "Advanced" Complexity request from Frontend
    logger.info("Attempting generation with Structure='AABA', PassingTones=True, GhostNotes=True")
    try:
        midi, seed = generator.generate(
            description="Test V2",
            style="techno", 
            instrument="drums", 
            sub_option="full_kit",
            complexity=0.9,
            key="C",
            scale_type="minor",
            use_dna=True,
            # New Kwargs
            structure="AABA",
            passing_tones=True, 
            ghost_notes=True
        )
        logger.info("✅ Generation Successful with new kwargs!")
    except Exception as e:
        logger.error(f"❌ Generation Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_v2_generation_args()
