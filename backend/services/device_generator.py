# backend/services/device_generator.py
import json
import xml.etree.ElementTree as ET
from typing import Dict, Optional

class AbletonDeviceGenerator:
    """
    Generates Ableton device presets and racks
    """
    
    def create_drum_rack(self, samples: Dict = None) -> ET.Element:
        """
        Create a drum rack device
        """
        drum_rack = ET.Element('GroupDevicePreset')
        
        # Device metadata
        ET.SubElement(drum_rack, 'Name', {'Value': 'AI Drum Kit'})
        
        # Device chain
        device = ET.SubElement(drum_rack, 'Device')
        drum_group = ET.SubElement(device, 'DrumGroupDevice', {'Id': '0'})
        
        # Add drum pads
        branches = ET.SubElement(drum_group, 'Branches')
        
        # Standard drum mapping
        drum_pads = [
            {'note': 36, 'name': 'Kick'},
            {'note': 38, 'name': 'Snare'},
            {'note': 42, 'name': 'Hat Closed'},
            {'note': 46, 'name': 'Hat Open'},
            {'note': 39, 'name': 'Clap'},
            {'note': 43, 'name': 'Tom Low'},
            {'note': 45, 'name': 'Tom Mid'},
            {'note': 47, 'name': 'Tom Hi'}
        ]
        
        for pad in drum_pads:
            self._add_drum_pad(branches, pad['note'], pad['name'])
        
        return drum_rack
    
    def _add_drum_pad(self, parent, note: int, name: str):
        """Add individual drum pad to rack"""
        branch = ET.SubElement(parent, 'DrumBranch', {'Id': str(note)})
        
        ET.SubElement(branch, 'LomId', {'Value': '0'})
        ET.SubElement(branch, 'Name', {'Value': name})
        ET.SubElement(branch, 'MidiNoteNumber', {'Value': str(note)})
        
        # Receive note
        receive_note = ET.SubElement(branch, 'ReceivingNote')
        ET.SubElement(receive_note, 'NoteNumber', {'Value': str(note)})
        ET.SubElement(receive_note, 'Name', {'Value': name})
        ET.SubElement(receive_note, 'Pitch', {'Value': str(note)})
        
        # Device chain for the pad
        device_chain = ET.SubElement(branch, 'DeviceChain')
        
        # Can add Simpler/Sampler here with samples if provided
        if name == 'Kick':
            self._add_operator_to_chain(device_chain, self._create_kick_preset())
    
    def _create_kick_preset(self) -> Dict:
        """Create Operator preset for kick drum"""
        return {
            'osc_a': {
                'wave': 'Sine',
                'coarse': 0,
                'fine': 0,
                'volume': -6
            },
            'pitch_env': {
                'amount': 48,
                'attack': 0.001,
                'decay': 0.1,
                'sustain': 0
            },
            'filter': {
                'type': 'Low Pass',
                'frequency': 200,
                'resonance': 0.5
            },
            'amp_env': {
                'attack': 0.001,
                'decay': 0.5,
                'sustain': 0,
                'release': 0.5
            }
        }
    
    def _add_operator_to_chain(self, chain, preset: Dict):
        """Add Operator synth with preset to device chain"""
        devices = ET.SubElement(chain, 'Devices')
        operator = ET.SubElement(devices, 'Operator', {'Id': '1'})
        
        # Apply preset parameters
        # This is simplified - real Operator has hundreds of parameters
        for param_name, value in preset.items():
            if isinstance(value, dict):
                group = ET.SubElement(operator, param_name)
                for sub_param, sub_value in value.items():
                    ET.SubElement(group, sub_param, {'Value': str(sub_value)})
            else:
                ET.SubElement(operator, param_name, {'Value': str(value)})