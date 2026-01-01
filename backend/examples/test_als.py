# Save this as: backend/examples/test_als.py

import sys
import os

# Add parent directory to path so we can import from services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.als_generator_fixed import AbletonLiveProject
from services.midi_to_als import MIDIToAbletonConverter

def test_create_project():
    """
    Example: Create a complete Ableton project
    """
    
    print("🎵 Creating Ableton Live Project...")
    
    # Initialize project
    project = AbletonLiveProject(
        project_name="Dark Techno Starter",
        bpm=130,
        live_version="11.0"  # Use 11.0 for compatibility
    )
    
    # Define patterns
    techno_pattern = {
        'drums': {
            'kick': [0, 4, 8, 12],
            'hihat_closed': [2, 6, 10, 14],
            'clap': [4, 12],
            'rim': [7, 15]
        },
        'bass': {
            '33': [0, 1, 2, 3, 4, 5, 6, 7]  # A0 note, 8th notes
        }
    }
    
    # Convert patterns to notes
    converter = MIDIToAbletonConverter()
    
    # Configure tracks
    tracks_config = [
        {
            'type': 'midi',
            'name': 'Drums',
            'color': 14,  # Red
            'clips': [{
                'name': 'Main Beat',
                'length': 4,
                'notes': converter.pattern_to_notes(techno_pattern['drums'])
            }]
        },
        {
            'type': 'midi',
            'name': 'Bass',
            'color': 8,  # Blue
            'clips': [{
                'name': 'Bassline',
                'length': 4,
                'notes': converter.pattern_to_notes(techno_pattern['bass'])
            }]
        }
    ]
    
    # Generate ALS file
    als_bytes = project.create_project(
        midi_data=techno_pattern,
        tracks_config=tracks_config
    )
    
    # Create output directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    # Save to file
    output_path = 'output/dark_techno_starter.als'
    with open(output_path, 'wb') as f:
        f.write(als_bytes)
    
    # Get file size
    file_size = os.path.getsize(output_path)
    
    print("✅ Created dark_techno_starter.als")
    print(f"   - BPM: 130")
    print(f"   - Tracks: Drums, Bass")
    print(f"   - File size: {file_size} bytes")
    print(f"   - Location: {os.path.abspath(output_path)}")
    print(f"   - Ready to open in Ableton Live!")
    print("\n📝 Try opening this file in Ableton Live")
    
    return output_path

if __name__ == "__main__":
    test_create_project()