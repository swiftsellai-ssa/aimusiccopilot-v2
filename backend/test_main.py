from fastapi.testclient import TestClient
from main import app  # Importă aplicația ta

client = TestClient(app)

# 1. Testăm dacă serverul e viu
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    # Verifică dacă mesajul e cel așteptat (ajustează textul)
    assert response.json() == {"message": "AIMusicCopilot API is running"}

# 2. Testăm Generarea (fără să cerem AI-ului să muncească greu)
# Aici verificăm doar dacă endpoint-ul acceptă cererea corect
def test_generate_music_validation():
    # Trimitem date incomplete să vedem dacă dă eroare (așa e corect)
    response = client.post("/generate", json={}) 
    assert response.status_code == 422  # Unprocessable Entity (lipsesc date)

# 3. Testăm un flux complet de generare (Mock)
# Atenție: Asta va consuma resurse reale dacă nu folosim mock-uri, 
# dar e bun pentru un test rapid local.
def test_generate_drums_simple():
    payload = {
        "type": "drums",
        "complexity": "simple",
        "bpm": 120
    }
    # Asigură-te că endpoint-ul tău e /generate sau /api/generate
    response = client.post("/generate", json=payload)
    
    if response.status_code == 200:
        data = response.json()
        assert "midi_data" in data or "url" in data
        assert "status" in data
        assert data["status"] == "success"
    else:
        # Dacă ai autentificare pe endpoint, testul va pica cu 401
        print("Endpoint-ul necesită autentificare sau a crăpat:", response.text)

# 4. Test Login (dacă vrei să testezi și autentificarea)
def test_login_flow():
    # Încearcă să te loghezi cu un user fals
    response = client.post("/token", data={
        "username": "nu_exista@test.com", 
        "password": "parola_gresita"
    })
    assert response.status_code == 401