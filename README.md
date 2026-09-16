# LogiSense-AI — Delivery Performance, Delay Risk & Logistics Intelligence Platform

[![CI Pipeline](https://github.com/pika1063/LogiSense-AI/actions/workflows/ci.yml/badge.svg)](https://github.com/pika1063/LogiSense-AI/actions)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.2+-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.4+-F7931E.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![Docker](https://img.shields.io/badge/Docker-Enabled-2496ED.svg?logo=docker&logoColor=white)](https://www.docker.com/)

**LogiSense-AI** is a full-stack, enterprise-grade machine learning platform designed to forecast delivery delays and evaluate supply chain risk **before** fulfillment occurs.

---

## Key Features

- **Leakage-Safe Predictive Engine**: Predicts Late_delivery_risk ( = \text{on time}, 1 = \text{late}$) strictly using features knowable pre-delivery.
- **Tuned Random Forest Architecture**: Delivers .08\%$ F1-Score, .47\%$ ROC-AUC, and .21\%$ Accuracy over 172,765 real delivery records.
- **Interactive 3D Earth Experience**: Custom CSS 3D Earth globe visualization with scroll progression, orbital particles, and route animations.
- **Dynamic Multi-Theme System**: Instant switching between **Midnight** (navy/violet), **Aurora** (teal/emerald), and **Light** themes.
- **Real-Time Database Explorer**: SQLite shipment browser with multi-filter searches, pagination, and indexing for low-latency queries.
- **Enterprise-Ready REST API**: High-performance FastAPI endpoints with OpenAPI docs, dynamic CORS, and Pydantic validation.
- **Docker & CI/CD**: Complete containerization with docker-compose and automated GitHub Actions pipelines.

---

## System Architecture

`
                                  +---------------------------------------+
                                  |         REACT 19 + VITE FRONTEND      |
                                  | - Multi-Theme & Interactive 3D Earth  |
                                  | - Real-time Risk Prediction Dial      |
                                  | - Shipment Explorer & BI Charts       |
                                  +-------------------+-------------------+
                                                      |
                                          HTTP / REST (JSON)
                                                      |
                                  +-------------------v-------------------+
                                  |            FASTAPI BACKEND            |
                                  | - Pydantic Input Validation           |
                                  | - Preprocessing Pipeline Transform    |
                                  | - Indexed SQLite Query Service        |
                                  +---------+-------------------+---------+
                                            |                   |
                        +-------------------v---+   +-----------v-------------------+
                        |   RANDOM FOREST ML    |   |     SQLITE DATABASE (172K)    |
                        | - 136 Encoded Features|   | - Table: shipments            |
                        | - best_model.joblib   |   | - 5 Performance Indexes       |
                        +-----------------------+   +-------------------------------+
`

---

## Machine Learning Benchmark

| Model | Accuracy | Precision | Recall | F1-Score | ROC-AUC | Status |
|---|---|---|---|---|---|---|
| **Random Forest** | **69.21%** | **69.83%** | **68.35%** | **69.08%** | **75.47%** | **Production Selected** |
| XGBoost | 70.27% | 72.10% | 66.00% | 68.90% | 76.24% | Benchmark |
| Logistic Regression | 69.64% | 70.80% | 64.00% | 67.25% | 74.47% | Baseline |

### Target Leakage Prevention
To guarantee real-world integrity, post-delivery and outcome attributes are strictly excluded from model inputs:
- Delivery Status (exact mirror of target)
- Days for shipping (real) (realized outcome)
- Order Status (post-fulfillment lifecycle flag)
- Financial fields (Sales, Order Profit Per Order, Benefit per order)
- Customer PII (Customer Street, Customer Zipcode)

---

## Quick Start (How to Run Locally)

> **Note:** The links below (localhost) are accessed in your browser **after** you start the backend and frontend servers using either Docker or Python/Node.

### Option 1: Run with Docker Compose (Single Command)
`ash
docker-compose up --build
`
Once started, open in your browser:
* **Web Dashboard**: http://localhost:3000
* **Interactive API Swagger Docs**: http://localhost:8000/docs

---

### Option 2: Run with Python & Vite

#### Step 1: Start the Backend (Terminal 1)
`ash
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
`
* Interactive API Documentation will be live at: **http://127.0.0.1:8000/docs**

#### Step 2: Start the Frontend (Terminal 2)
`ash
cd frontend
npm install
npm run dev
`
* The Web Dashboard will be live at: **http://localhost:5173**

---

## Running Tests

`ash
# Run pytest suite
python -m pytest -v

# Run frontend build check
cd frontend && npm run build
`

---

## API Reference Summary

| Method | Endpoint | Description |
|---|---|---|
| GET | /health | Diagnostic healthcheck (model, DB, preprocessor status) |
| POST | /predict | Predict delay probability and risk category |
| GET | /analytics | Global analytics summary |
| GET | /insights | Top feature importance weights |
| GET | /shipments | Paginated live shipment records |
| GET | /shipments/search | Search shipments by keyword or attribute filters |
| GET | /shipments/summary | Aggregate on-time vs late shipment summary |
| GET | /shipments/by-shipping-mode | Shipping mode volume and delay rates |
| GET | /shipments/by-market | International market performance |

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| ENVIRONMENT | development | Runtime environment (development / production) |
| CORS_ORIGINS | http://localhost:5173,... | Allowed CORS origins (comma-separated) |
| VITE_API_URL | http://127.0.0.1:8000 | Backend API URL for React frontend |

---

## License & Attribution
Developed as part of the **LogiSense-AI** platform engineering project.
