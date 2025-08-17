from fastapi.testclient import TestClient
from main import app
import math
from datetime import datetime, timezone

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
def test_history_empty():
    client.delete("/history")
    r = client.get("/history")
    assert r.status_code == 200
    assert r.json() == []


def test_history_delete_and_empty():
    client.post("/calculate", params={"expr": "1+2"})
    client.post("/calculate", params={"expr": "3+4"})
    r = client.delete("/history")
    assert r.status_code == 200 and r.json() == {"ok": True, "cleared": True}
    r = client.get("/history")
    assert r.status_code == 200 and r.json() == []

def test_history_after_calculation():
    client.delete("/history")
    client.post("/calculate", params={"expr": "9+9"})
    client.post("/calculate", params={"expr": "9*9"})
    
    r = client.get("/history")
    assert r.status_code == 200
    history = r.json()
    assert len(history) == 2
    assert any(h["expr"] == "9+9" and h["result"] == 18 for h in history)
    assert any(h["expr"] == "9*9" and h["result"] == 81 for h in history)

def test_history_error_entry_shape():
    client.delete("/history")
    client.post("/calculate", params={"expr": "2*("})  # force error
    it = client.get("/history").json()[0]
    assert it["expr"] == "2*(" and it["result"] == "" and it["error"]

def test_history_entry_timestamp():
    client.delete("/history")
    r = client.post("/calculate", params={"expr": "5+5"})
    assert r.status_code == 200
    history = client.get("/history").json()
    assert len(history) == 1
    assert "timestamp" in history[0]
    assert isinstance(history[0]["timestamp"], str)
    try:
        datetime.fromisoformat(history[0]["timestamp"])
    except ValueError:
        assert False, "Timestamp is not a valid ISO format"