"""
Test runner for integrated MIDI generator
Run from backend directory: python test_runner.py
"""
import sys
import os
import unittest

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the test module
from services import test_integrated_midi_generator

if __name__ == '__main__':
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromModule(test_integrated_midi_generator)

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
