from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_prediction():
    payload = {
        "days_for_shipment_scheduled": 3,
        "shipping_mode": "Standard Class",
        "market": "USCA",
        "order_region": "Western US",
        "customer_segment": "Consumer",
        "customer_state": "CA",
        "category_name": "Cleats",
        "department_name": "Outdoors"
    }

    response = client.post("/predict", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert "prediction" in data
    assert "prediction_label" in data
    assert "delay_probability" in data
    assert "risk_level" in data

    assert data["prediction"] in [0, 1]
    assert 0 <= data["delay_probability"] <= 100
    assert data["risk_level"] in ["Low", "Medium", "High"]
