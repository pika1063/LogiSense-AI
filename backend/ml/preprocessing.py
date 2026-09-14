"""
preprocessing.py
================
Leakage-safe preprocessing pipeline for LogiSense-AI.

Goal
----
Predict `Late_delivery_risk` (0 = on time, 1 = late) **before** the delivery
happens. Anything that is only known *after* delivery - or that equals the
outcome itself - is therefore excluded from the model features.

Design rules enforced here
--------------------------
1. NEVER use as features:
   - Delivery Status            -> it IS the outcome ("Late delivery" == risk 1)
   - Days for shipping (real)   -> the real vs scheduled gap ~ IS the delay
   - Order Status               -> lifecycle flag filled in after the fact
   - realized financial fields  -> not available pre-delivery AND ~no signal
   - customer names / street    -> PII, and pure noise
2. Rows that are not real deliveries (`CANCELED`, `SUSPECTED_FRAUD` order
   status) are dropped *before* splitting: their "on-time" label is meaningless.
3. Every randomness draws a fixed `random_state` so the whole run reproduces
   byte-for-byte.
4. The preprocessor is fit on the TRAIN split only - never on the test split
   (prevents test leakage through imputation/encoding/scaling statistics).

Outputs
-------
- data/processed/X_train.csv, X_test.csv, y_train.csv, y_test.csv
- data/processed/preprocessing_summary.json   (shapes, class counts)
- models/preprocessing_pipeline.joblib        (fitted transformers, re-usable
                                                later at prediction time)
- models/feature_names.json                   (names of the final columns)

Usage
-----
    python backend/ml/preprocessing.py
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# ----------------------------------------------------------------------------
# Project paths (resolved relative to this repo so it runs from anywhere)
# ----------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
RAW_PATH = REPO_ROOT / "data" / "raw" / "APL_Logistics - APL_Logistics.csv"
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
MODELS_DIR = REPO_ROOT / "models"

# ----------------------------------------------------------------------------
# Hyper-parameters (kept together so they are easy to change / reproduce)
# ----------------------------------------------------------------------------
TARGET_COLUMN = "Late_delivery_risk"
TEST_SIZE = 0.20
RANDOM_STATE = 42

NON_DELIVERY_ORDER_STATUSES = ["CANCELED", "SUSPECTED_FRAUD"]

# Leakage/unsafe columns and the reason each one is excluded.
#   "outcome"  -> identical to, or a direct transformation of, the target.
#   "post"     -> only known after delivery / after the fact.
#   "pii"      -> personally identifiable information, high cardinality noise.
#   "noise"    -> available but carries no signal for this target.
LEAKAGE_REASONS: dict[str, str] = {
    "Delivery Status":          "outcome - exactly mirrors Late_delivery_risk (Late delivery -> 1).",
    "Days for shipping (real)": "outcome - actual delivery time; (real - scheduled) ~ IS the delay.",
    "Order Status":             "post - lifecycle flag finalized after the fact; also used only as a row filter.",
    "Order Item Quantity":      "noise - no correlation with risk and realized during fulfillment.",
    "Order Item Discount":      "noise - ~0 correlation; financial value realized at checkout.",
    "Order Item Discount Rate": "noise - ~0 correlation; financial value realized at checkout.",
    "Order Item Product Price": "noise - ~0 correlation; financial value realized at checkout.",
    "Order Item Profit Ratio":  "noise - ~0 correlation; financial value realized after delivery.",
    "Order Item Total":         "noise - ~0 correlation; financial value realized after delivery.",
    "Sales":                    "noise - ~0 correlation; revenue realized after delivery.",
    "Order Profit Per Order":   "noise - ~0 correlation; profit realized after delivery.",
    "Benefit per order":        "noise - ~0 correlation; profit realized after delivery.",
    "Sales per customer":       "noise - ~0 correlation; aggregated post-delivery.",
    "Product Price":            "noise - ~0 correlation; financial value realized at checkout.",
    "Order Customer Id":        "pii - 180k unique identifiers, no predictive value raw.",
    "Customer Id":              "pii - individual identifiers.",
    "Customer Fname":           "pii - customer first name.",
    "Customer Lname":           "pii - customer last name.",
    "Customer Street":          "pii - full street address (7k unique).",
    "Customer Zipcode":         "pii - postal code, 3 missing values, near-infinite cardinality.",
    "Customer Country":         "noise - only 2 values (EE. UU., Puerto Rico), redundant with State.",
    "Type":                     "noise - payment method, unrelated to logistics and delay.",
    "Latitude":                 "noise - ~0 correlation; shipment coordinates add no risk signal.",
    "Longitude":                "noise - ~0 correlation; shipment coordinates add no risk signal.",
    "Order City":               "noise - 3,597 unique cities (too sparse, minor signal).",
    "Order Country":            "noise - 164 unique countries (too sparse, minor signal).",
    "Customer City":            "noise - 563 unique cities (too sparse, minor signal).",
    "Product Name":             "noise - 118 products; Category + Department already capture it.",
}

# The final, leakage-safe columns used to build the model.
NUMERIC_FEATURES = ["Days for shipment (scheduled)"]

CATEGORICAL_FEATURES = [
    "Shipping Mode",     # standard / second / first class / same day
    "Market",            # 5 international markets
    "Order Region",      # 23 regions (kept; Order City/Country dropped as too sparse)
    "Customer Segment",  # consumer / corporate / home office
    "Customer State",    # 46 states
    "Category Name",     # 50 product categories
    "Department Name",   # 11 departments
]

FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES


# ----------------------------------------------------------------------------
# 1. Loading
# ----------------------------------------------------------------------------
def load_raw(path: Path = RAW_PATH) -> pd.DataFrame:
    """Load the real APL Logistics dataset."""
    if not path.exists():
        raise FileNotFoundError(f"Raw dataset not found: {path}")
    df = pd.read_csv(path, encoding="utf-8", low_memory=False)
    return df


# ----------------------------------------------------------------------------
# 2. Row filtering (NOT feature engineering)
# ----------------------------------------------------------------------------
def drop_non_deliveries(df: pd.DataFrame) -> pd.DataFrame:
    """
    Keep only actual deliveries.

    CANCELED / SUSPECTED_FRAUD orders are not deliveries - their target is 0
    for the wrong reason ("never shipped" != "on time"). Removing them before
    splitting makes the on-time class meaningful. Order Status is used ONLY for
    filtering here, never as a model feature.
    """
    before = len(df)
    mask = ~df["Order Status"].isin(NON_DELIVERY_ORDER_STATUSES)
    result = df[mask].copy()
    print(f"[filter] dropped {before - len(result):,} non-delivery rows "
          f"({NON_DELIVERY_ORDER_STATUSES}); kept {len(result):,}")
    return result


# ----------------------------------------------------------------------------
# 3. Feature selection (leakage-safe)
# ----------------------------------------------------------------------------
def select_features(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series]:
    """
    Split the raw frame into X (leakage-safe features) and y (target).

    Raises an error if a "forbidden" column would sneak back into the features,
    so future edits cannot accidentally reintroduce leakage.
    """
    X = df[FEATURE_COLUMNS].copy()

    # Cast categoricals to plain `object` strings. pandas 3.0 reads CSVs with
    # the new StringDtype ("str"), and scikit-learn's SimpleImputer/OneHotEncoder
    # handle that dtype differently from classic object strings - which made the
    # categorical branch collapse to one column. Object dtype is the well-tested
    # path for sklearn encoders.
    for col in CATEGORICAL_FEATURES:
        X[col] = X[col].astype("object")

    y = df[TARGET_COLUMN].astype(int).copy()

    leaked_present = [c for c in LEAKAGE_REASONS if c not in X.columns and c != "Delivery Status"]
    # The excluded columns must NOT be among FEATURE_COLUMNS.
    forbidden_in_features = [c for c in LEAKAGE_REASONS if c in FEATURE_COLUMNS]
    if forbidden_in_features:
        raise ValueError(f"Leakage guard failed - forbidden columns in features: {forbidden_in_features}")

    print(f"[select] features = {X.shape[1]} ({len(NUMERIC_FEATURES)} numeric, "
          f"{len(CATEGORICAL_FEATURES)} categorical) | target rows = {len(y):,}")
    return X, y


# ----------------------------------------------------------------------------
# 4. Transformer construction
# ----------------------------------------------------------------------------
def build_preprocessor() -> ColumnTransformer:
    """
    ColumnTransformer used at both train and prediction time.

    numeric   -> median imputation (defensive; no NaNs today) + StandardScaler
    cat       -> most-frequent imputation (defensive) + OneHotEncoder (drops
                 the first category of each column to avoid collinearity)
    """
    numeric_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )

    categorical_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            # sparse_output=False: pandas 3.0 cannot wrap a scipy sparse matrix
            # into a DataFrame (it reads the shape as (n, 1)); dense output keeps
            # the pipeline compatible and feature names 1:1 with columns.
            ("encoder", OneHotEncoder(handle_unknown="ignore", drop="first",
                                      sparse_output=False)),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_pipe, NUMERIC_FEATURES),
            ("cat", categorical_pipe, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
        verbose_feature_names_out=False,  # clean names like "Shipping Mode_First Class"
    )
    return preprocessor


def fitted_feature_names(preprocessor: ColumnTransformer) -> list[str]:
    """Return the exact output column names for the fitted transformer."""
    return list(preprocessor.get_feature_names_out())


# ----------------------------------------------------------------------------
# 5. Orchestrator
# ----------------------------------------------------------------------------
def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    # --- load + filter + select ---
    df = load_raw()
    df = drop_non_deliveries(df)
    X, y = select_features(df)

    # --- stratified split (reproducible) ---
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=TEST_SIZE,
        stratify=y,             # keep the same late/on-time ratio in both folds
        random_state=RANDOM_STATE,
    )
    print(f"[split] train = {len(X_train):,} | test = {len(X_test):,} "
          f"(test_size={TEST_SIZE}, random_state={RANDOM_STATE})")

    # --- fit the preprocessor on the TRAIN split only ---
    preprocessor = build_preprocessor()
    preprocessor.fit(X_train)

    X_train_t = pd.DataFrame(
        preprocessor.transform(X_train),
        columns=fitted_feature_names(preprocessor),
    )
    X_test_t = pd.DataFrame(
        preprocessor.transform(X_test),
        columns=fitted_feature_names(preprocessor),
    )

    # --- save datasets ---
    X_train_t.to_csv(PROCESSED_DIR / "X_train.csv", index=False)
    X_test_t.to_csv(PROCESSED_DIR / "X_test.csv", index=False)
    y_train.to_csv(PROCESSED_DIR / "y_train.csv", index=False)
    y_test.to_csv(PROCESSED_DIR / "y_test.csv", index=False)

    # --- save reusable artifacts ---
    joblib.dump(preprocessor, MODELS_DIR / "preprocessing_pipeline.joblib")
    with open(MODELS_DIR / "feature_names.json", "w", encoding="utf-8") as fh:
        json.dump(fitted_feature_names(preprocessor), fh, indent=2)

    # --- save a short machine-readable summary ---
    summary: dict[str, Any] = {
        "raw_rows": len(df),
        "n_features": X_train_t.shape[1],
        "train_size": len(X_train_t),
        "test_size": len(X_test_t),
        "train_class_counts": y_train.value_counts().to_dict(),
        "test_class_counts": y_test.value_counts().to_dict(),
        "late_rate_train": round(float(y_train.mean()), 4),
        "late_rate_test": round(float(y_test.mean()), 4),
        "random_state": RANDOM_STATE,
        "excluded_leakage_columns": sorted(LEAKAGE_REASONS.keys()),
    }
    with open(PROCESSED_DIR / "preprocessing_summary.json", "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)

    # --- console report ---
    print("\n================ PREPROCESSING REPORT ================")
    print(f"Feature count (one-hot expanded): {X_train_t.shape[1]}")
    print(f"Train size: {len(X_train_t):,} | Test size: {len(X_test_t):,}")
    print(f"Target splits:\n  train -> {y_train.value_counts().to_dict()}")
    print(f"  test  -> {y_test.value_counts().to_dict()}")
    print(f"Late rate: train {y_train.mean():.4f} | test {y_test.mean():.4f}")
    print(f"Excluded leakage-prone columns: {len(LEAKAGE_REASONS)}")
    print("Saved: X_train/X_test/y_train/y_test CSV, preprocessor.joblib,")
    print("       feature_names.json, preprocessing_summary.json")
    print("======================================================")


if __name__ == "__main__":
    main()