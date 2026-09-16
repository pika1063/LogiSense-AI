from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200


def test_api_status():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"



def test_health():
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True
    assert data["preprocessor_loaded"] is True
    assert data["database_connected"] is True
    assert data["model"] is not None


def test_analytics():
    response = client.get("/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "total_shipments" in data
    assert "late_rate" in data
    assert "shipping_mode" in data


def test_insights():
    response = client.get("/insights")
    assert response.status_code == 200
    data = response.json()
    assert "top_features" in data
    assert "model_info" in data


def test_model_info():
    response = client.get("/model-info")
    assert response.status_code == 200
    data = response.json()
    assert "best_model" in data


def test_shipments_summary():
    response = client.get("/shipments/summary")
    assert response.status_code == 200
    data = response.json()
    assert "total_shipments" in data
    assert "late_shipments" in data
    assert "on_time_shipments" in data
    assert "late_rate" in data


def test_shipments_by_shipping_mode():
    response = client.get("/shipments/by-shipping-mode")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "shipping_mode" in data[0]
    assert "late_rate" in data[0]


def test_shipments_by_market():
    response = client.get("/shipments/by-market")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "market" in data[0]


def test_shipments_by_carrier():
    response = client.get("/shipments/by-carrier")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "carrier" in data[0] or "shipping_mode" in data[0]

