from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import expand_percent

client = TestClient(app)


def test_add_percent():
    """Test addition where B% means 'B percent of A'."""
    assert expand_percent("5 + 10%") == "5 + ((10/100)*5)"


def test_subtract_percent():
    """Test subtraction where B% means 'B percent of A'."""
    assert expand_percent("20 - 30%") == "20 - ((30/100)*20)"


def test_multiply_percent():
    """Test multiplication where B% means 'B divided by 100'."""
    assert expand_percent("15 * 25%") == "15 * (25/100)"


def test_divide_percent():
    """Test division where B% means 'B divided by 100'."""
    assert expand_percent("40 / 50%") == "40 / (50/100)"


def test_multiple_operations():
    """Test expressions with multiple A op B% operations."""
    assert expand_percent("3 * 4% + 2 / 1%") == "3 * (4/100) + 2 / (1/100)"


def test_standalone_100_percent():
    """Test standalone percentage (100%)."""
    assert expand_percent("100%") == "(100/100)"


def test_two_standalone_percents():
    """Test expression with two standalone percentages."""
    assert expand_percent("10% + 20%") == "(10/100) + (20/100)"


def test_calculate_addition():
    # Updated input to use JSON object with key 'expr'
    response = client.post("/calculate", json={"expr": "1+1"})
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["result"] == 2


def test_calculate_invalid():
    response = client.post("/calculate", json={"expr": "1++1"})
    assert response.status_code == 200
    data = response.json()
    assert not data["ok"]
    assert "error" in data and data["error"] != ""


def test_operator_normalization():
    response = client.post("/calculate", json={"expr": "2×2"})
    assert response.status_code == 200
    data = response.json()
    assert data["ok"] is True
    assert data["result"] == 4


def test_history_and_clear_history():
    # Ensure history is clear before starting the test
    client.delete("/history")

    # perform a calculation to add an entry to the history
    client.post("/calculate", json={"expr": "3+3"})

    # check that history has entries
    response_history = client.get("/history")
    data_history = response_history.json()
    assert len(data_history) > 0

    # clear the history
    response_clear = client.delete("/history")
    data_clear = response_clear.json()
    assert data_clear["ok"] is True

    # after clearing history, history should be empty
    response_history_after = client.get("/history")
    data_history_after = response_history_after.json()
    assert data_history_after == []
