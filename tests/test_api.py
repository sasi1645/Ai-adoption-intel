from fastapi.testclient import TestClient
import ai_adoption_intel.api
from ai_adoption_intel.api import app

client = TestClient(app)


def test_national_ai_adoption():
    response = client.get("/national/ai-adoption")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 23
    assert data[9] == {"period_start": "2026-03-09", "percentage": 19.1}


def test_sector_adoption():
    response = client.get("/sectors/ai-adoption?sector=44")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 23
    assert data[0] == {"period_start": "2025-11-03", "percentage": 12.5}


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
    assert data[2] == {
        "sector": "52",
        "name": "Finance and Insurance",
        "percentage": 40.1,
    }


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
    assert data[5] == {
        "sector": "53",
        "name": "Real Estate and Rental and Leasing",
        "percentage": 30.8,
    }


def test_ranking_default():
    response = client.get("/sectors/ranking")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 5
    assert data[4] == {
        "sector": "XX",
        "name": "Multi-sector or multi-state companies",
        "percentage": 33.7,
    }


def test_ask_success(monkeypatch):
    fake_result = {
        "question": "q",
        "sql": "SELECT question From national;",
        "rows": [],
        "answer": "is using ai is good.",
    }

    def func(question):
        return fake_result

    monkeypatch.setattr(ai_adoption_intel.api, "ask", func)
    response = client.post("/ask", json={"question": "How much do banks use AI?"})
    assert response.status_code == 200
    data = response.json()
    assert data == fake_result


def test_ask_unsafe_sql(monkeypatch):
    def func(question):
        raise ValueError("not safe")

    monkeypatch.setattr(ai_adoption_intel.api, "ask", func)
    response = client.post(
        "/ask",
        json={"question": "How has AI use changed in the space-travel industry?"},
    )
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "not safe"


def test_ask_missing_question():
    response = client.post("/ask", json={})
    assert response.status_code == 422
