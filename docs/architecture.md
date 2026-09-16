# LogiSense-AI System Architecture

## Overview
LogiSense-AI is an end-to-end, enterprise-grade delay risk intelligence platform that forecasts late shipments before delivery fulfillment. It combines real-world supply chain datasets (APL Logistics), leakage-safe machine learning pipelines, FastAPI microservices, and a React + Vite interactive intelligence dashboard.

`
+-------------------------------------------------------------------------+
|                              REACT FRONTEND                             |
|  +--------------------+  +--------------------+  +-------------------+  |
|  |  Interactive Earth |  | Real-Time Predictor|  | Shipment Explorer |  |
|  |   3D Visual Scene  |  |  Dynamic Risk Dial |  | SQLite Table & BI |  |
|  +--------------------+  +--------------------+  +-------------------+  |
+------------------------------------+------------------------------------+
                                     |
                         HTTP / REST API (JSON)
                                     |
+------------------------------------v------------------------------------+
|                             FASTAPI BACKEND                             |
|  +--------------------+  +--------------------+  +-------------------+  |
|  | CORS & Validation  |  | Prediction Engine  |  | Query Optimization|  |
|  | Pydantic Schemas   |  | Preprocessor & RF  |  | SQLite Index Scan |  |
|  +--------------------+  +--------------------+  +-------------------+  |
+-------------------+--------------------------------+--------------------+
                    |                                |
        +-----------v-----------+        +-----------v-----------+
        |   ML Model Artifacts  |        |    SQLite Database    |
        | - best_model.joblib   |        | - logisense.db        |
        | - preprocessor.joblib |        | - 172,765 records     |
        | - feature_names.json  |        | - 5 query indexes     |
        +-----------------------+        +-----------------------+
`

## Component Breakdown

### 1. Data Ingestion & Storage
- **Source**: data/raw/APL_Logistics - APL_Logistics.csv (180,519 raw records).
- **Filtering**: Rows with non-delivery statuses (CANCELED, SUSPECTED_FRAUD) are dropped, yielding 172,765 valid fulfillment observations.
- **Database**: SQLite (data/logisense.db), table shipments, indexed on Late_delivery_risk, Shipping Mode, Market, Order Region, and Customer Segment.

### 2. Machine Learning Pipeline
- **Target**: Late_delivery_risk ( = \text{on time}, 1 = \text{late}$).
- **Feature Selection**: Strictly pre-delivery attributes.
- **Transformer**: ColumnTransformer with StandardScaler for scheduled days and OneHotEncoder(drop='first', handle_unknown='ignore') for categoricals (136 total expanded features).
- **Model**: Tuned Random Forest Classifier ($ estimators, balanced class weights).

### 3. Backend REST Service
- Built with **FastAPI** and **Uvicorn**.
- Provides real-time inference via POST /predict.
- Provides dataset exploration and aggregation via GET /shipments, GET /shipments/search, GET /analytics, GET /insights.

### 4. Frontend Intelligence Dashboard
- Built with **React 19** and **Vite**.
- Three distinct themes: **Midnight**, **Aurora**, and **Light**.
- Custom 3D CSS interactive Earth globe tracking scroll progression.
- Live prediction engine with interactive risk dial and probability calculations.
