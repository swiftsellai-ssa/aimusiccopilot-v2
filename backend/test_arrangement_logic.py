import sys
import os
import requests
from pydantic import BaseModel

# Mock the path to run standalone if needed, but since we are testing endpoints, we might need running server OR just import logic.
# Importing logic is safer / faster than checking running server.

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.routers.arrangement import ArrangementRequest, ArrangementBlock
from backend.services.integrated_midi_generator import IntegratedMidiGenerator
import mido

def test_stitching_logic():
    print("--- Testing Arrangement Stitching Logic ---")
    
    # Mock Request
    req = ArrangementRequest(
        blocks=[
            ArrangementBlock(type='intro', bars=4),
            ArrangementBlock(type='verse', bars=8),
            ArrangementBlock(type='chorus', bars=8)
        ],
        style='techno',
        bpm=120
    )
    
    print(f"Plan: {len(req.blocks)} blocks.")
    
    # Initialize Generator
    generator = IntegratedMidiGenerator()
    final_mid = mido.MidiFile(ticks_per_beat=480)
    final_track = mido.MidiTrack()
    final_mid.tracks.append(final_track)
    final_track.append(mido.MetaMessage('set_tempo', tempo=mido.bpm2tempo(req.bpm)))
    
    ticks_per_bar = 480 * 4
    total_expected_ticks = 0
    
    for block in req.blocks:
        print(f"Generating block: {block.type} ({block.bars} bars)...")
        block_mid, _ = generator.generate(
            description=f"{req.style} {block.type}",
            style=req.style,
            instrument='full_kit',
            sub_option=block.type,
            bpm=req.bpm,
            bars=block.bars,
            humanize=False # simplify
        )
        
        source_track = block_mid.tracks[0]
        current_block_ticks = 0
        
        for msg in source_track:
            if msg.type == 'set_tempo': continue
            if msg.type == 'end_of_track': continue
            
            final_track.append(msg.copy())
            current_block_ticks += msg.time
            
        print(f"  > Generated Ticks: {current_block_ticks}")
        expected_local = block.bars * ticks_per_bar
        print(f"  > Expected Ticks:  {expected_local}")
        
        if current_block_ticks < expected_local:
            gap = expected_local - current_block_ticks
            final_track.append(mido.MetaMessage('marker', text=f"End {block.type}", time=int(gap)))
            print(f"  > Added GAP: {gap}")
        elif current_block_ticks > expected_local:
             print("  > ⚠️ OVERFLOW")
             
        total_expected_ticks += expected_local

    print(f"\nTotal Expected Length: {total_expected_ticks}")
    
    # Calculate actual length
    actual_len = sum(msg.time for msg in final_track)
    print(f"Actual Length: {actual_len}")
    
    if abs(actual_len - total_expected_ticks) < 10: # Allow tiny float error
        print("✅ Stitching Successful. Length matches.")
    else:
        print("❌ Stitching Error. Length mismatch.")
        
if __name__ == "__main__":
    test_stitching_logic()
