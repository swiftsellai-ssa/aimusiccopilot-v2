# Save this as: backend/examples/test_live12.py

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.als_generator import AbletonLive12Generator

def test_create_live12_project():
    """Create an ALS file for Ableton Live 12"""
    
    print("🎵 Creating Ableton Live 12 Project...")
    print("📌 For Live version 12.2.1")
    
    # Create generator for Live 12
    generator = AbletonLive12Generator(bpm=128, project_name="Live 12 Project")
    
    # Generate ALS data
    als_data = generator.create_live12_project()
    
    # Create output directory
    os.makedirs('output', exist_ok=True)
    
    # Save file
    output_path = 'output/live12_project.als'
    with open(output_path, 'wb') as f:
        f.write(als_data)
    
    # Check file
    file_size = os.path.getsize(output_path)
    
    print(f"✅ Created {output_path}")
    print(f"📁 File size: {file_size:,} bytes")
    print(f"📍 Location: {os.path.abspath(output_path)}")
    print(f"\n🎵 This should open in Ableton Live 12.2.1!")
    print(f"📝 Version string: 12.0_12049")
    
    return output_path

if __name__ == "__main__":
    test_create_live12_project()