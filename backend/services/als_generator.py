import gzip
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional

class AbletonLiveProject:
    """
    A robust 'Project Factory' for Ableton Live 12.
    Uses xml.etree.ElementTree instead of raw strings to ensure
    schema validity and prevent file corruption.
    """
    
    def __init__(self, project_name: str = "AI Generated", bpm: float = 120.0):
        self.bpm = bpm
        self.project_name = project_name
        self.next_id = 10000
        # Live 12.0.2 schema versioning
        self.major_version = "5"
        self.minor_version = "12.0_12049"
        self.schema_change_count = "1"
        self.creator = "Ableton Live 12.0.2"

    def _get_next_id(self) -> str:
        """Generate unique sequential IDs for XML nodes."""
        self.next_id += 1
        return str(self.next_id)

    def create_project(self, midi_data: Dict = None, tracks_config: List[Dict] = None) -> bytes:
        """
        Main entry point. Orchestrates the creation of the Project Factory.
        """
        # 1. Create Root & LiveSet
        root = self._create_root_structure()
        live_set = root.find('LiveSet')
        tracks_node = live_set.find('Tracks')
        
        # 2. Add Tracks (Dynamic Configuration)
        # Default to 4 tracks if no config provided
        config = tracks_config if tracks_config else [
            {'name': 'Drums', 'color': 4},
            {'name': 'Bass', 'color': 8},
            {'name': 'Lead', 'color': 14},
            {'name': 'Synth', 'color': 21}
        ]
        
        for i, track_info in enumerate(config):
            self._add_midi_track(tracks_node, track_info['name'], track_info.get('color', 10), i)

        # 3. Add Master Track (Required by Live)
        self._add_master_track(live_set)

        # 4. Serialize and Compress
        return self._serialize_and_compress(root)

    def _create_root_structure(self) -> ET.Element:
        """Builds the skeleton of a valid Live 12 ALS file."""
        root = ET.Element('Ableton', {
            'MajorVersion': self.major_version,
            'MinorVersion': self.minor_version,
            'SchemaChangeCount': self.schema_change_count,
            'Creator': self.creator,
            'Revision': ""
        })

        live_set = ET.SubElement(root, 'LiveSet')
        
        # Essential Global Settings
        ET.SubElement(live_set, 'NextPointeeId', {'Value': '20000'})
        ET.SubElement(live_set, 'OverwriteProtectionNumber', {'Value': '2817'})
        ET.SubElement(live_set, 'LomId', {'Value': '0'})
        
        # Container for Tracks
        ET.SubElement(live_set, 'Tracks')
        
        # Transport / Tempo
        transport = ET.SubElement(live_set, 'Transport')
        tempo = ET.SubElement(transport, 'Tempo')
        ET.SubElement(tempo, 'Manual', {'Value': str(self.bpm)})
        
        # Scale Information (Live 12 specific)
        scale_info = ET.SubElement(live_set, 'ScaleInformation')
        ET.SubElement(scale_info, 'RootNote', {'Value': '0'})
        ET.SubElement(scale_info, 'Name', {'Value': 'Major'})

        return root

    def _add_midi_track(self, parent_node: ET.Element, name: str, color: int, index: int):
        """Adds a single MIDI track with valid internal routing IDs."""
        track_id = str(100 + index)
        track = ET.SubElement(parent_node, 'MidiTrack', {'Id': track_id})
        
        # Track Header
        ET.SubElement(track, 'LomId', {'Value': '0'})
        name_node = ET.SubElement(track, 'Name')
        ET.SubElement(name_node, 'EffectiveName', {'Value': name})
        ET.SubElement(name_node, 'UserName', {'Value': name})
        ET.SubElement(track, 'Color', {'Value': str(color)})
        ET.SubElement(track, 'TrackGroupId', {'Value': '-1'})

        # Device Chain (The Core Mixer)
        device_chain = ET.SubElement(track, 'DeviceChain')
        mixer = ET.SubElement(device_chain, 'Mixer')
        
        # Setup Mixer Volume/Pan
        self._setup_mixer_component(mixer, 'Volume', 1.0)
        self._setup_mixer_component(mixer, 'Pan', 0.0)
        
        # Adds an empty MainSequencer (where MIDI clips will go later)
        ET.SubElement(device_chain, 'MainSequencer')

    def _add_master_track(self, live_set_node: ET.Element):
        """Adds the Master track. Essential for the file to open."""
        master = ET.SubElement(live_set_node, 'MasterTrack', {'Id': '0'})
        ET.SubElement(master, 'LomId', {'Value': '0'})
        
        name_node = ET.SubElement(master, 'Name')
        ET.SubElement(name_node, 'EffectiveName', {'Value': 'Master'})
        
        device_chain = ET.SubElement(master, 'DeviceChain')
        mixer = ET.SubElement(device_chain, 'Mixer')
        self._setup_mixer_component(mixer, 'Volume', 1.0)
        
    def _setup_mixer_component(self, mixer_node: ET.Element, name: str, default_value: float):
        """Helper to create Mixer controls with required AutomationTargets."""
        component = ET.SubElement(mixer_node, name)
        ET.SubElement(component, 'LomId', {'Value': '0'})
        ET.SubElement(component, 'Manual', {'Value': str(default_value)})
        
        # AutomationTarget is required for every knob in Live's XML
        auto_target = ET.SubElement(component, 'AutomationTarget', {'Id': self._get_next_id()})
        ET.SubElement(auto_target, 'LockEnvelope', {'Value': '0'})

    def _serialize_and_compress(self, root: ET.Element) -> bytes:
        """Converts the ElementTree to XML string and GZIPs it."""
        # Add XML declaration and encoding
        xml_str = ET.tostring(root, encoding='UTF-8', xml_declaration=True)
        
        # Ableton expects standard compression
        return gzip.compress(xml_str, compresslevel=9)