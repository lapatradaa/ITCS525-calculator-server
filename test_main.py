from fastapi.testclient import TestClient
from main import app
import math

client = TestClient(app)

def test_basic_division():
    r = client.post("/calculate", params={"expr": "30/4"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert abs(data["result"] - 7.5) < 1e-9

def test_percent_subtraction():
    r = client.post("/calculate", params={"expr": "100 - 6%"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert abs(data["result"] - 94.0) < 1e-9

def test_standalone_percent():
    r = client.post("/calculate", params={"expr": "6%"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert abs(data["result"] - 0.06) < 1e-9

def test_invalid_expr_returns_ok_false():
    r = client.post("/calculate", params={"expr": "2**(3"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is False
    assert "error" in data and data["error"] != ""

#-------------------------------------------------------------------------------------------------------
# TODO Add more tests
def test_history_after_calculation():
    client.delete("/history")
    client.post("/calculate", params={"expr": "2+2"})
    client.post("/calculate", params={"expr": "5*3"})
    
    r = client.get("/history")
    assert r.status_code == 200
    history = r.json()
    assert len(history) == 2
    assert any(h["expr"] == "2+2" and h["result"] == 4 for h in history)
    assert any(h["expr"] == "5*3" and h["result"] == 15 for h in history)

def test_large_number_calculation():
    r = client.post("/calculate", params={"expr": "666666 * 666666"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["result"] == 666666 * 666666

def test_floating_point_precision():
    r = client.post("/calculate", params={"expr": "0.1 + 0.7 - 0.2"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert abs(data["result"] - 0.6) < 1e-9

def test_chained_operations():
    r = client.post("/calculate", params={"expr": "68 + 36 * 90 - 1"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert data["result"] == 68 + 36 * 90 - 1