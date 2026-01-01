import gzip
import os

# Numele fișierului generat (verifică să fie cel corect din folderul output sau root)
# Dacă fișierul e în output, schimbă calea: 'output/dark_techno_starter.als'
filename = 'live12_project.als' 

try:
    with gzip.open(filename, 'rb') as f:
        xml_content = f.read().decode('utf-8')
        
    lines = xml_content.split('\n')
    
    print(f"--- XML INSPECTOR: {filename} ---")
    print(f"Total lines: {len(lines)}")
    
    # Afișăm liniile din jurul erorii (75)
    start = max(0, 70)
    end = min(len(lines), 85)
    
    for i in range(start, end):
        prefix = ">>" if (i + 1) == 75 else "  "
        print(f"{prefix} {i+1}: {lines[i]}")
        
except Exception as e:
    print(f"Error: {e}")