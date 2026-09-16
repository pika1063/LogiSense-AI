from pathlib import Path
import json
import os
import logging

import pandas as pd
import joblib

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.app.database import get_connection
from backend.scripts.import_database import main as import_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("logisense")


# ==========================================================
# PROJECT PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODELS_DIR = PROJECT_ROOT / "models"
EVALUATION_DIR = MODELS_DIR / "evaluation"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


# ==========================================================
# MODEL FILES
# ==========================================================

BEST_MODEL_PATH = MODELS_DIR / "xgboost.joblib"

PREPROCESSOR_PATH = MODELS_DIR / "preprocessing_pipeline.joblib"

BEST_MODEL_INFO_PATH = MODELS_DIR / "best_model_info.json"

FEATURE_NAMES_PATH = MODELS_DIR / "feature_names.json"

ANALYTICS_PATH = PROCESSED_DIR / "analytics.json"

METRICS_PATH = EVALUATION_DIR / "model_metrics.json"

TOP_FEATURES_PATH = EVALUATION_DIR / "top_features.json"


# ==========================================================
# LOAD MODEL + FILES
# ==========================================================

model = None
preprocessor = None

model_info = {}
feature_names = []
analytics_data = {}
metrics_data = {}
top_features_data = []


def load_json(path: Path, default):
    try:
        if path.exists():
            with open(
                path,
                "r",
                encoding="utf-8"
            ) as file:
                return json.load(file)

    except Exception as err:
        logger.warning(
            f"Could not load JSON from {path}: {err}"
        )

    return default


try:
    if BEST_MODEL_PATH.exists():
        model = joblib.load(
            BEST_MODEL_PATH
        )
        logger.info(
            f"Loaded model: {type(model).__name__}"
        )

except Exception as error:
    logger.warning(
        f"Warning: Could not load model: {error}"
    )


try:
    if PREPROCESSOR_PATH.exists():
        preprocessor = joblib.load(
            PREPROCESSOR_PATH
        )
        logger.info(
            "Loaded preprocessing pipeline successfully"
        )

except Exception as error:
    logger.warning(
        f"Warning: Could not load preprocessor: {error}"
    )


model_info = load_json(
    BEST_MODEL_INFO_PATH,
    {}
)

feature_names = load_json(
    FEATURE_NAMES_PATH,
    []
)

analytics_data = load_json(
    ANALYTICS_PATH,
    {}
)

metrics_data = load_json(
    METRICS_PATH,
    {}
)

top_features_data = load_json(
    TOP_FEATURES_PATH,
    []
)


# ==========================================================
# FASTAPI APP
# ==========================================================

app = FastAPI(
    title="LogiSense AI API",
    description=(
        "Delivery performance, delay risk "
        "and logistics efficiency intelligence API."
    ),
    version="1.0.0"
)


# ==========================================================
# CORS CONFIGURATION
# ==========================================================

raw_cors = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173,"
    "http://127.0.0.1:5173,"
    "http://localhost:3000,"
    "http://127.0.0.1:3000,"
    "http://localhost:80,"
    "http://127.0.0.1:80"
)

allowed_origins = [
    origin.strip()
    for origin in raw_cors.split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=(
        allowed_origins
        if allowed_origins
        else ["*"]
    ),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ==========================================================
# DATABASE INITIALIZATION
# ==========================================================

@app.on_event("startup")
def initialize_database():
    try:
        connection = get_connection()

        table_exists = connection.execute(
            "SELECT name FROM sqlite_master "
            "WHERE type='table' AND name='shipments'"
        ).fetchone()

        connection.close()

        if table_exists is None:
            logger.info(
                "Shipments table missing. Importing database..."
            )
            import_database()

            logger.info(
                "Database initialization completed."
            )

        else:
            logger.info(
                "Shipments table already exists."
            )

    except Exception as error:
        logger.warning(
            f"Database initialization warning: {error}"
        )


# ==========================================================
# PYDANTIC SCHEMA
# ==========================================================

class ShipmentInput(BaseModel):

    days_for_shipment_scheduled: int = Field(
        ...,
        ge=0,
        le=60,
        description=(
            "Promised/scheduled days for shipment fulfillment"
        ),
        json_schema_extra={
            "example": 3
        }
    )

    shipping_mode: str = Field(
        ...,
        description=(
            "Logistics service tier: Standard Class, "
            "Second Class, First Class, Same Day"
        ),
        json_schema_extra={
            "example": "Standard Class"
        }
    )

    market: str = Field(
        ...,
        description=(
            "Destination market region: USCA, LATAM, "
            "Europe, Pacific Asia, Africa"
        ),
        json_schema_extra={
            "example": "USCA"
        }
    )

    order_region: str = Field(
        ...,
        description=(
            "Operating region (e.g. Western US, "
            "Central America, Western Europe)"
        ),
        json_schema_extra={
            "example": "Western US"
        }
    )

    customer_segment: str = Field(
        ...,
        description=(
            "Customer tier: Consumer, Corporate, Home Office"
        ),
        json_schema_extra={
            "example": "Consumer"
        }
    )

    customer_state: str = Field(
        ...,
        description=(
            "US state or regional identifier "
            "(e.g. CA, NY, TX, PR)"
        ),
        json_schema_extra={
            "example": "CA"
        }
    )

    category_name: str = Field(
        ...,
        description="Merchandise product category",
        json_schema_extra={
            "example": "Cleats"
        }
    )

    department_name: str = Field(
        ...,
        description="Department classification",
        json_schema_extra={
            "example": "Outdoors"
        }
    )


# ==========================================================
# HELPER
# ==========================================================

MODEL_COLUMNS = [
    "Days for shipment (scheduled)",
    "Shipping Mode",
    "Market",
    "Order Region",
    "Customer Segment",
    "Customer State",
    "Category Name",
    "Department Name",
]


def make_model_dataframe(
    shipment: ShipmentInput
) -> pd.DataFrame:

    return pd.DataFrame(
        [
            {
                "Days for shipment (scheduled)":
                    shipment.days_for_shipment_scheduled,

                "Shipping Mode":
                    shipment.shipping_mode,

                "Market":
                    shipment.market,

                "Order Region":
                    shipment.order_region,

                "Customer Segment":
                    shipment.customer_segment,

                "Customer State":
                    shipment.customer_state,

                "Category Name":
                    shipment.category_name,

                "Department Name":
                    shipment.department_name,
            }
        ],
        columns=MODEL_COLUMNS
    )


def calculate_risk(probability: float):

    if probability < 35:
        return "Low"

    if probability < 65:
        return "Medium"

    return "High"


# ==========================================================
# STATIC FILES / FRONTEND MOUNTING
# ==========================================================

from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

DIST_DIR = PROJECT_ROOT / "frontend" / "dist"
ASSETS_DIR = DIST_DIR / "assets"

if ASSETS_DIR.exists():
    app.mount(
        "/assets",
        StaticFiles(
            directory=str(ASSETS_DIR)
        ),
        name="assets"
    )


# ==========================================================
# BASIC / ROOT ENDPOINT
# ==========================================================

@app.get("/")
def root():

    index_file = DIST_DIR / "index.html"

    if index_file.exists():
        return FileResponse(
            str(index_file)
        )

    return {
        "message": "LogiSense AI API is running",
        "status": "healthy"
    }


@app.get("/api/status")
def api_status():

    return {
        "message": "LogiSense AI API is running",
        "status": "healthy"
    }


# ==========================================================
# HEALTH
# ==========================================================

@app.get("/health")
def health():

    database_connected = False

    try:

        connection = get_connection()

        connection.execute(
            "SELECT 1"
        ).fetchone()

        connection.close()

        database_connected = True

    except Exception:

        database_connected = False

    return {
        "status": "healthy",

        "model_loaded":
            model is not None,

        "preprocessor_loaded":
            preprocessor is not None,

        "database_connected":
            database_connected,

        "model":
            (
                model.__class__.__name__
                if model is not None
                else None
            ),

        "feature_count":
            len(MODEL_COLUMNS)
    }


# ==========================================================
# PREDICTION
# ==========================================================

@app.post("/predict")
def predict(
    shipment: ShipmentInput
):

    if model is None:
        raise HTTPException(
            status_code=500,
            detail="Model is not loaded."
        )

    if preprocessor is None:
        raise HTTPException(
            status_code=500,
            detail=(
                "Preprocessing pipeline is not loaded."
            )
        )

    try:

        dataframe = make_model_dataframe(
            shipment
        )

        transformed = preprocessor.transform(
            dataframe
        )

        if (
            feature_names
            and hasattr(transformed, "shape")
            and transformed.shape[1]
                == len(feature_names)
        ):

            transformed_df = pd.DataFrame(
                transformed,
                columns=feature_names
            )

            prediction = int(
                model.predict(
                    transformed_df
                )[0]
            )

            probabilities = (
                model.predict_proba(
                    transformed_df
                )[0]
            )

        else:

            prediction = int(
                model.predict(
                    transformed
                )[0]
            )

            probabilities = (
                model.predict_proba(
                    transformed
                )[0]
            )

        delay_probability = float(
            probabilities[1] * 100
        )

        delay_probability = round(
            delay_probability,
            2
        )

        prediction_label = (
            "Late"
            if prediction == 1
            else "On Time"
        )

        risk_level = calculate_risk(
            delay_probability
        )

        return {
            "prediction":
                prediction,

            "prediction_label":
                prediction_label,

            "delay_probability":
                delay_probability,

            "risk_level":
                risk_level,

            "model":
                model.__class__.__name__
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Prediction failed: {error}"
            )
        )


# ==========================================================
# ANALYTICS
# ==========================================================

@app.get("/analytics")
def analytics():

    return analytics_data


# ==========================================================
# MODEL INSIGHTS
# ==========================================================

@app.get("/insights")
def insights():

    return {
        "top_features":
            top_features_data,

        "model_info":
            model_info,

        "metrics":
            metrics_data
    }


# ==========================================================
# MODEL INFO
# ==========================================================

@app.get("/model-info")
def get_model_info():

    return model_info


# ==========================================================
# DATABASE — COUNT
# ==========================================================

@app.get("/shipments/count")
def shipment_count():

    try:

        connection = get_connection()

        result = connection.execute(
            "SELECT COUNT(*) AS total "
            "FROM shipments"
        ).fetchone()

        connection.close()

        return {
            "total_shipments":
                result["total"]
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Database error: {error}"
            )
        )


# ==========================================================
# DATABASE — RECENT SHIPMENTS
# ==========================================================

@app.get("/shipments")
def get_shipments(

    limit: int = Query(
        20,
        ge=1,
        le=100
    ),

    offset: int = Query(
        0,
        ge=0
    )
):

    try:

        connection = get_connection()

        rows = connection.execute(
            """
            SELECT *
            FROM shipments
            LIMIT ?
            OFFSET ?
            """,
            (
                limit,
                offset
            )
        ).fetchall()

        connection.close()

        shipments = [
            dict(row)
            for row in rows
        ]

        return {
            "count":
                len(shipments),

            "limit":
                limit,

            "offset":
                offset,

            "shipments":
                shipments
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Database error: {error}"
            )
        )


# ==========================================================
# DATABASE — SEARCH
# ==========================================================

@app.get("/shipments/search")
def search_shipments(

    q: str | None = None,

    shipping_mode: str | None = None,

    market: str | None = None,

    customer_segment: str | None = None,

    order_region: str | None = None,

    late_delivery_risk: int | None = Query(
        None,
        ge=0,
        le=1
    ),

    limit: int = Query(
        20,
        ge=1,
        le=100
    ),

    offset: int = Query(
        0,
        ge=0
    )
):

    try:

        connection = get_connection()

        query = """
            SELECT *
            FROM shipments
            WHERE 1 = 1
        """

        parameters = []

        if q and q.strip():

            term = f"%{q.strip()}%"

            query += """
                AND (
                    CAST("Order Id" AS TEXT) LIKE ?
                    OR "Shipping Mode" LIKE ?
                    OR "Market" LIKE ?
                    OR "Order Region" LIKE ?
                    OR "Customer Segment" LIKE ?
                    OR "Customer State" LIKE ?
                    OR "Category Name" LIKE ?
                    OR "Department Name" LIKE ?
                )
            """

            parameters.extend(
                [term] * 8
            )

        if shipping_mode:

            query += """
                AND "Shipping Mode" = ?
            """

            parameters.append(
                shipping_mode
            )

        if market:

            query += """
                AND "Market" = ?
            """

            parameters.append(
                market
            )

        if customer_segment:

            query += """
                AND "Customer Segment" = ?
            """

            parameters.append(
                customer_segment
            )

        if order_region:

            query += """
                AND "Order Region" = ?
            """

            parameters.append(
                order_region
            )

        if late_delivery_risk is not None:

            query += """
                AND "Late_delivery_risk" = ?
            """

            parameters.append(
                late_delivery_risk
            )

        query += """
            LIMIT ?
            OFFSET ?
        """

        parameters.append(limit)
        parameters.append(offset)

        rows = connection.execute(
            query,
            parameters
        ).fetchall()

        connection.close()

        shipments = [
            dict(row)
            for row in rows
        ]

        return {
            "count":
                len(shipments),

            "limit":
                limit,

            "offset":
                offset,

            "shipments":
                shipments
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Database error: {error}"
            )
        )


# ==========================================================
# DATABASE — SUMMARY
# ==========================================================

@app.get("/shipments/summary")
def shipment_summary():

    try:

        connection = get_connection()

        total = connection.execute(
            """
            SELECT COUNT(*) AS value
            FROM shipments
            """
        ).fetchone()["value"]

        late = connection.execute(
            """
            SELECT COUNT(*) AS value
            FROM shipments
            WHERE "Late_delivery_risk" = 1
            """
        ).fetchone()["value"]

        on_time = connection.execute(
            """
            SELECT COUNT(*) AS value
            FROM shipments
            WHERE "Late_delivery_risk" = 0
            """
        ).fetchone()["value"]

        connection.close()

        late_rate = (
            (late / total) * 100
            if total > 0
            else 0
        )

        return {
            "total_shipments":
                total,

            "late_shipments":
                late,

            "on_time_shipments":
                on_time,

            "late_rate":
                round(
                    late_rate,
                    2
                )
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Database error: {error}"
            )
        )


# ==========================================================
# DATABASE — SHIPPING MODE SUMMARY
# ==========================================================

@app.get("/shipments/by-shipping-mode")
def shipments_by_shipping_mode():

    try:

        connection = get_connection()

        rows = connection.execute(
            """
            SELECT
                "Shipping Mode" AS shipping_mode,
                COUNT(*) AS shipments,
                SUM(
                    CASE
                        WHEN "Late_delivery_risk" = 1
                        THEN 1
                        ELSE 0
                    END
                ) AS late_shipments
            FROM shipments
            GROUP BY "Shipping Mode"
            ORDER BY shipments DESC
            """
        ).fetchall()

        connection.close()

        result = []

        for row in rows:

            shipments = row["shipments"]

            late_shipments = (
                row["late_shipments"]
                or 0
            )

            result.append(
                {
                    "shipping_mode":
                        row["shipping_mode"],

                    "shipments":
                        shipments,

                    "late_shipments":
                        late_shipments,

                    "late_rate":
                        round(
                            (
                                late_shipments
                                / shipments
                            ) * 100,
                            2
                        )
                        if shipments > 0
                        else 0
                }
            )

        return result

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Database error: {error}"
            )
        )


# ==========================================================
# DATABASE — MARKET SUMMARY
# ==========================================================

@app.get("/shipments/by-market")
def shipments_by_market():

    try:

        connection = get_connection()

        rows = connection.execute(
            """
            SELECT
                "Market" AS market,
                COUNT(*) AS shipments,
                SUM(
                    CASE
                        WHEN "Late_delivery_risk" = 1
                        THEN 1
                        ELSE 0
                    END
                ) AS late_shipments
            FROM shipments
            GROUP BY "Market"
            ORDER BY shipments DESC
            """
        ).fetchall()

        connection.close()

        result = []

        for row in rows:

            shipments = row["shipments"]

            late_shipments = (
                row["late_shipments"]
                or 0
            )

            result.append(
                {
                    "market":
                        row["market"],

                    "shipments":
                        shipments,

                    "late_shipments":
                        late_shipments,

                    "late_rate":
                        round(
                            (
                                late_shipments
                                / shipments
                            ) * 100,
                            2
                        )
                        if shipments > 0
                        else 0
                }
            )

        return result

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Database error: {error}"
            )
        )


# ==========================================================
# DATABASE — SHIPPING MODE PERFORMANCE
# ==========================================================

@app.get("/shipments/by-carrier")
def shipments_by_carrier():

    """
    Returns delivery performance aggregated by Shipping Mode.

    Note: The dataset categorizes logistics tiers
    by Shipping Mode (Standard, Second, First, Same Day).
    """

    try:

        connection = get_connection()

        rows = connection.execute(
            """
            SELECT
                "Shipping Mode" AS shipping_mode,
                COUNT(*) AS shipments,
                SUM(
                    CASE
                        WHEN "Late_delivery_risk" = 1
                        THEN 1
                        ELSE 0
                    END
                ) AS late_shipments
            FROM shipments
            GROUP BY "Shipping Mode"
            ORDER BY shipments DESC
            """
        ).fetchall()

        connection.close()

        result = []

        for row in rows:

            shipments = row["shipments"]

            late_shipments = (
                row["late_shipments"]
                or 0
            )

            late_rate = (
                (late_shipments / shipments) * 100
                if shipments > 0
                else 0
            )

            result.append(
                {
                    "shipping_mode":
                        row["shipping_mode"],

                    "carrier":
                        row["shipping_mode"],

                    "shipments":
                        shipments,

                    "late_shipments":
                        late_shipments,

                    "late_rate":
                        round(
                            late_rate,
                            2
                        )
                }
            )

        return result

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Database error: {error}"
            )
        )