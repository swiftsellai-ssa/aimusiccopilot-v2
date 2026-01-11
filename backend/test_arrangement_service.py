import sys
import os
import mido

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.arrangement_service import ArrangementService

def test_arrangement_service():
    print("--- Testing ArrangementService ---")
    
    service = ArrangementService()
    
    structure = [
        {'type': 'intro', 'bars': 4},
        {'type': 'verse', 'bars': 8},
        {'type': 'chorus', 'bars': 8}
    ]
    
    print(f"Generating arrangement with structure: {structure}")
    
    try:
        mid = service.generate_arrangement(
            structure=structure,
            style='techno',
            key='F#',
            scale='minor',
            bpm=128
        )
        
        # Verify Length
        total_ticks = 0
        for track in mid.tracks:
            ticks = sum(msg.time for msg in track)
            if ticks > total_ticks: total_ticks = ticks
            
        print(f"Total Ticks: {total_ticks}")
        
        # Expected: (4 + 8 + 8) bars * 4 beats * 480 ticks
        expected_ticks = (4 + 8 + 8) * 4 * 480
        print(f"Expected:    {expected_ticks}")
        
        if abs(total_ticks - expected_ticks) < 10:
            print("✅ Service Test Passed: Length matches.")
        else:
            print(f"❌ Service Test Failed: Length mismatch ({total_ticks} vs {expected_ticks})")
            
        # Verify Content (Basic)
        print(f"Track count: {len(mid.tracks)}")
        if len(mid.tracks) >= 4:
             print("✅ MIDI has 4+ tracks (Multi-Track Success).")
        else:
             print(f"❌ MIDI Track count too low: {len(mid.tracks)}")

        # Verify Length of ALL tracks
        all_match = True
        for i, tr in enumerate(mid.tracks):
             ticks = sum(msg.time for msg in tr)
             if ticks > 0 and abs(ticks - expected_ticks) > 100: # Allow slight meta difference
                 print(f"Track {i} Length Mismatch: {ticks}")
                 all_match = False
        
        if all_match:
            print("✅ All tracks aligned.")
             
    except Exception as e:
        print(f"❌ Service Test Crashed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_arrangement_service()
