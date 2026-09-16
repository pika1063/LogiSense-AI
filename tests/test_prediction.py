from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)


def test_prediction_standard():
    payload = {
        "days_for_shipment_scheduled": 4,
        "shipping_mode": "Standard Class",
        "market": "USCA",
        "order_region": "West of USA",
        "customer_segment": "Consumer",
        "customer_state": "CA",
        "category_name": "Cleats",
        "department_name": "Outdoors",
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


def test_prediction_same_day():
    payload = {
        "days_for_shipment_scheduled": 0,
        "shipping_mode": "Same Day",
        "market": "Europe",
        "order_region": "Western Europe",
        "customer_segment": "Corporate",
        "customer_state": "NY",
        "category_name": "Women's Apparel",
        "department_name": "Apparel",
    }

    response = client.post("/predict", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["prediction"] in [0, 1]
    assert 0 <= data["delay_probability"] <= 100


def test_prediction_invalid_negative_days():
    payload = {
        "days_for_shipment_scheduled": -5,
        "shipping_mode": "Standard Class",
        "market": "USCA",
        "order_region": "West of USA",
        "customer_segment": "Consumer",
        "customer_state": "CA",
        "category_name": "Cleats",
        "department_name": "Outdoors",
    }

    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_prediction_missing_field():
    payload = {
        "days_for_shipment_scheduled": 3,
        "shipping_mode": "Standard Class",
        # Missing market and other required fields
    }

    response = client.post("/predict", json=payload)
    assert response.status_code == 422


def test_prediction_unseen_category():
    payload = {
        "days_for_shipment_scheduled": 2,
        "shipping_mode": "Second Class",
        "market": "Unknown Market",
        "order_region": "Unknown Region",
        "customer_segment": "Consumer",
        "customer_state": "Unknown State",
        "category_name": "Unknown Category",
        "department_name": "Unknown Dept",
    }

    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["prediction"] in [0, 1]
    assert 0 <= data["delay_probability"] <= 100

