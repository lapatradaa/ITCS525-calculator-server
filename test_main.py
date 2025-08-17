from fastapi.testclient import TestClient
from main import app  # or whatever your app module is
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
def test_math_constants():
    r = client.post("/calculate", params={"expr": "pi + e"})
    assert r.status_code == 200
    data = r.json()
    assert data["ok"] is True
    assert abs(data["result"] - (math.pi + math.e)) < 1e-9

def test_history_after_calculation():
    client.delete("/history")
    client.post("/calculate", params={"expr": "2+2"})
    client.post("/calculate", params={"expr": "5*3"})
    
    r = client.get("/history")
    assert r.status_code == 200
    history = r.json()
    assert len(history) == 2
    assert "2+2 = 4" in history
    assert "5*3 = 15" in history

def test_history_parameter_lmit():
    client.delete("/history")
    for i in range(1, 6):
        client.post("/calculate", params={"expr": f"{i}*10"})
    
    r = client.get("/history?n=3")
    assert len(r.json()) == 3
    assert "5*10 = 50" in r.json()

def test_history_clear():
    client.post("/calculate", params={"expr": "1+1"})
    r = client.delete("/history")
    assert r.status_code == 200
    assert r.json()["message"] == "history cleared"
    
    assert len(client.get("/history").json()) == 0