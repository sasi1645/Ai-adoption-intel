from fastapi.testclient import TestClient
from ai_adoption_intel.api import app

client = TestClient(app)

def test_national_ai_adoption():
    response = client.get("/national/ai-adoption")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 23 
    assert data[9] == {"period_start":"2026-03-09","percentage":19.1}

def test_sector_adoption():
    response = client.get("/sectors/ai-adoption?sector=44") 
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 23 
    assert data[0] == {"period_start":"2025-11-03","percentage":12.5}

def test_sector_missing():
    response = client.get("/sectors/ai-adoption") 
    assert response.status_code == 422

    data = response.json()
    assert data["detail"][0]["type"] == "missing"

def test_sector_adoption_99():
    response = client.get("/sectors/ai-adoption?sector=99") 
    assert response.status_code == 404

    data = response.json()
    assert "99" in data["detail"]

def test_sector_ranking():
    response = client.get("/sectors/ranking?limit=3")
    assert response.status_code == 200

    data = response.json()
    assert data[2] == {"sector":"52","percentage":40.1}

def test_sector_ranking_abc():
    response = client.get("/sectors/ranking?limit=abc")
    assert response.status_code == 422

    data = response.json()
    assert data["detail"][0]["type"] == "int_parsing"

def test_sector_ranking_100():
    response = client.get("/sectors/ranking?limit=100")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 20
    assert data[5] == {"sector":"53","percentage":30.8}

def test_ranking_default():
    response = client.get("/sectors/ranking")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 5
    assert data[4] == {"sector":"XX","percentage":33.7}
