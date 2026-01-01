# backend/tests/test_als_generator.py
import pytest
import gzip
import xml.etree.ElementTree as ET
from services.als_generator import AbletonLiveProject

def test_als_file_structure():
    """Test that generated ALS has valid structure"""
    
    project = AbletonLiveProject("Test Project", 120)
    als_data = project.create_project()
    
    # Decompress to check XML
    xml_data = gzip.decompress(als_data)
    
    # Parse XML
    root = ET.fromstring(xml_data)
    
    # Check root element
    assert root.tag == 'Ableton'
    assert root.attrib['MajorVersion'] == '5'
    
    # Check for required elements
    live_set = root.find('LiveSet')
    assert live_set is not None
    
    # Check for tracks
    tracks = live_set.find('Tracks')
    assert tracks is not None
    
    # Check for transport (tempo)
    transport = live_set.find('Transport')
    assert transport is not None
    
    print("✅ ALS structure is valid!")

def test_open_in_ableton():
    """
    Manual test: Generate file and try opening in Ableton
    """
    project = AbletonLiveProject("Test Project", 128)
    als_data = project.create_project()
    
    with open('test_output.als', 'wb') as f:
        f.write(als_data)
    
    print("📁 Created test_output.als")
    print("👉 Now open this file in Ableton Live to verify it works!")