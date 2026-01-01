"""
Quick integration test for IntegratedMidiGenerator
Run this to verify everything works end-to-end
"""
import requests
import json
import sys
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
EMAIL = "test@example.com"  # Change to your test account
PASSWORD = "testpassword"    # Change to your test password

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}[PASS]{Colors.END} {msg}")

def print_fail(msg):
    print(f"{Colors.RED}[FAIL]{Colors.END} {msg}")

def print_info(msg):
    print(f"{Colors.BLUE}[INFO]{Colors.END} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}[WARN]{Colors.END} {msg}")

class APITester:
    def __init__(self, base_url, email, password):
        self.base_url = base_url
        self.email = email
        self.password = password
        self.token = None
        self.test_results = []

    def login(self):
        """Login and get JWT token"""
        print_info("Attempting login...")
        try:
            response = requests.post(
                f"{self.base_url}/token",
                data={"username": self.email, "password": self.password}
            )
            if response.status_code == 200:
                self.token = response.json()["access_token"]
                print_success(f"Login successful")
                return True
            else:
                print_fail(f"Login failed: {response.status_code}")
                return False
        except Exception as e:
            print_fail(f"Login error: {e}")
            return False

    def get_headers(self):
        """Get headers with auth token"""
        return {"Authorization": f"Bearer {self.token}"}

    def test_server_running(self):
        """Test if server is running"""
        print_info("Testing server connection...")
        try:
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                print_success("Server is running")
                return True
            else:
                print_fail(f"Server returned {response.status_code}")
                return False
        except Exception as e:
            print_fail(f"Cannot connect to server: {e}")
            return False

    def test_get_styles(self):
        """Test getting available styles"""
        print_info("Testing get styles endpoint...")
        try:
            response = requests.get(f"{self.base_url}/api/integrated-midi/styles")
            if response.status_code == 200:
                data = response.json()
                styles = data.get('styles', [])
                print_success(f"Got {len(styles)} styles: {', '.join(styles)}")
                return True
            else:
                print_fail(f"Get styles failed: {response.status_code}")
                return False
        except Exception as e:
            print_fail(f"Get styles error: {e}")
            return False

    def test_get_instruments(self):
        """Test getting available instruments"""
        print_info("Testing get instruments endpoint...")
        try:
            response = requests.get(f"{self.base_url}/api/integrated-midi/instruments")
            if response.status_code == 200:
                data = response.json()
                drums = len(data.get('drum_instruments', []))
                melodic = len(data.get('melodic_instruments', []))
                print_success(f"Got {drums} drum instruments, {melodic} melodic instruments")
                return True
            else:
                print_fail(f"Get instruments failed: {response.status_code}")
                return False
        except Exception as e:
            print_fail(f"Get instruments error: {e}")
            return False

    def test_get_presets(self):
        """Test getting DNA presets"""
        print_info("Testing get presets endpoint...")
        try:
            response = requests.get(f"{self.base_url}/api/integrated-midi/presets")
            if response.status_code == 200:
                data = response.json()
                presets = data.get('presets', {})
                print_success(f"Got {len(presets)} presets: {', '.join(presets.keys())}")
                return True
            else:
                print_fail(f"Get presets failed: {response.status_code}")
                return False
        except Exception as e:
            print_fail(f"Get presets error: {e}")
            return False

    def test_quick_generate(self):
        """Test quick generation"""
        print_info("Testing quick generate...")
        try:
            response = requests.post(
                f"{self.base_url}/api/integrated-midi/quick-generate",
                params={"description": "test pattern", "style": "techno"},
                headers=self.get_headers()
            )
            if response.status_code == 200:
                data = response.json()
                gen_id = data.get('generation_id')
                print_success(f"Quick generate successful (ID: {gen_id})")
                return gen_id
            else:
                print_fail(f"Quick generate failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print_fail(f"Quick generate error: {e}")
            return None

    def test_advanced_generate(self):
        """Test advanced generation with DNA parameters"""
        print_info("Testing advanced generate...")
        try:
            payload = {
                "description": "dark techno kick pattern",
                "style": "techno",
                "instrument": "kick",
                "bpm": 130,
                "bars": 4,
                "use_dna": True,
                "humanize": True,
                "density": 0.7,
                "complexity": 0.6,
                "groove": 0.2,
                "evolution": 0.3,
                "velocity_curve": "natural",
                "musical_key": "C",
                "musical_scale": "minor"
            }
            response = requests.post(
                f"{self.base_url}/api/integrated-midi/generate",
                json=payload,
                headers=self.get_headers()
            )
            if response.status_code == 200:
                data = response.json()
                gen_id = data.get('generation_id')
                metadata = data.get('metadata', {})
                print_success(f"Advanced generate successful (ID: {gen_id})")
                print_info(f"  BPM: {metadata.get('bpm')}, Bars: {metadata.get('bars')}, Tracks: {metadata.get('tracks')}")
                return gen_id
            else:
                print_fail(f"Advanced generate failed: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print_fail(f"Advanced generate error: {e}")
            return None

    def test_download(self, generation_id):
        """Test downloading a generated file"""
        print_info(f"Testing download for generation {generation_id}...")
        try:
            response = requests.get(
                f"{self.base_url}/api/integrated-midi/download/{generation_id}",
                headers=self.get_headers()
            )
            if response.status_code == 200:
                # Save to test file
                output_path = Path(f"test_output_{generation_id}.mid")
                output_path.write_bytes(response.content)
                file_size = len(response.content)
                print_success(f"Download successful ({file_size} bytes) -> {output_path}")
                return True
            else:
                print_fail(f"Download failed: {response.status_code}")
                return False
        except Exception as e:
            print_fail(f"Download error: {e}")
            return False

    def test_multiple_patterns(self):
        """Test generating multiple patterns"""
        print_info("Testing multiple pattern generation...")
        patterns = [
            ("techno kick", "techno", "kick"),
            ("trap hats", "trap", "hat"),
            ("house bass", "house", "bass"),
        ]

        success_count = 0
        for desc, style, instrument in patterns:
            try:
                payload = {
                    "description": desc,
                    "style": style,
                    "instrument": instrument,
                    "bpm": 130,
                    "bars": 4
                }
                response = requests.post(
                    f"{self.base_url}/api/integrated-midi/generate",
                    json=payload,
                    headers=self.get_headers()
                )
                if response.status_code == 200:
                    gen_id = response.json().get('generation_id')
                    print_success(f"  {desc}: ID {gen_id}")
                    success_count += 1
                else:
                    print_fail(f"  {desc}: Failed")
            except Exception as e:
                print_fail(f"  {desc}: Error - {e}")

        print_info(f"Generated {success_count}/{len(patterns)} patterns successfully")
        return success_count == len(patterns)

    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "="*60)
        print("INTEGRATED MIDI GENERATOR - INTEGRATION TESTS")
        print("="*60 + "\n")

        # Test 1: Server running
        if not self.test_server_running():
            print_fail("Server not running. Start with: uvicorn main:app --reload")
            return False

        # Test 2: Login
        if not self.login():
            print_fail("Login failed. Check credentials or create test account")
            return False

        print("\n" + "-"*60)
        print("TESTING METADATA ENDPOINTS")
        print("-"*60 + "\n")

        # Test 3-5: Metadata endpoints
        self.test_get_styles()
        self.test_get_instruments()
        self.test_get_presets()

        print("\n" + "-"*60)
        print("TESTING GENERATION ENDPOINTS")
        print("-"*60 + "\n")

        # Test 6: Quick generate
        quick_gen_id = self.test_quick_generate()

        # Test 7: Advanced generate
        adv_gen_id = self.test_advanced_generate()

        print("\n" + "-"*60)
        print("TESTING DOWNLOAD")
        print("-"*60 + "\n")

        # Test 8-9: Download
        if quick_gen_id:
            self.test_download(quick_gen_id)
        if adv_gen_id:
            self.test_download(adv_gen_id)

        print("\n" + "-"*60)
        print("TESTING MULTIPLE PATTERNS")
        print("-"*60 + "\n")

        # Test 10: Multiple patterns
        self.test_multiple_patterns()

        print("\n" + "="*60)
        print("ALL TESTS COMPLETED")
        print("="*60 + "\n")

        print_success("Integration tests passed!")
        print_info("Check the test_output_*.mid files in the current directory")
        return True


def main():
    """Main test runner"""
    print("\nIntegrated MIDI Generator - Integration Test Suite\n")

    # Check if server is likely running
    print_info(f"Testing connection to {BASE_URL}...")
    print_warning(f"Make sure backend is running: cd backend && uvicorn main:app --reload\n")

    tester = APITester(BASE_URL, EMAIL, PASSWORD)

    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_warning("\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_fail(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
