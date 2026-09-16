# LogiSense-AI API Documentation

Base URL: `http://localhost:8000` (or `$VITE_API_URL environment variable)

## Endpoints

**GET /health**
- Returns backend, model, preprocessor, and database health status.

**POST /predict**
- Predicts delay risk given pre-delivery shipment attributes.

- Payload: `days_for_shipment_scheduled`,  shipping_mode`, `market`, `order_region`, `customer_segment`, `customer_state`, `category_name`, `department_name`.

- Response: `prediction` (0 or 1), `prediction_label`, `delay_probability`, `risk_level` (Low/Medium/High), `model`.

**GET /analytics**
- Returns global alogistics distributions across modes, regions, markets, and categories.

**GET /insights**
- Returns feature importance and explainability data.

**GET /shipments**
- Paginated shipment records from SQLite (supports `limit` and `offset`).

**GET /shipments/search**
- Search and filter shipments by `q` free-text or specific fields.

**GET /shipments/summary**
- Total, late, on-time counts, and observed delay rates.
