import joblib
import json
import pandas as pd
import pytest
from pathlib import Path
from backend.ml.preprocessing import (
    FEATURE_COLUMNS,
    LEAKAGE_REASONS,
    NUMERIC_FEATURES,
    CATEGORICAL_FEATURES,
)

ROOT = Path(__file__).resolve().parents[1]



def test_leakage_reasons_guard():
    for col in FEATURE_COLUMNS:
        assert col not in LEAKAGE_REASONS, f"Leakage column {col} in FEATURE_COLUMNS!"



def test_preprocessor_transformation():
    prep_path = ROOT / "models" / "preprocessing_pipeline.joblib"
    assert prep_path.exists(), "preprocessing_pipeline.joblib must exist"
    prep = joblib.load(prep_path)
    df = pd.DataFrame([{
        "Days for shipment (scheduled)": 3,
        "Shipping Mode": "Standard Class",
        "Market": "USCA",
        "Order Region": "West of USA",
        "Customer Segment": "Consumer",
        "Customer State": "CA",
        "Category Name": "Cleats",
        "Department Name": "Outdoors",
    }])
    transformed = prep.transform(df)
    assert transformed.shape[1] == 136



def test_feature_names_file():
    feat_path = ROOT / "models" / "feature_names.json"
    assert feat_path.exists()
    with open(feat_path, "r", encoding="utf-8") as f:
        names = json.load(f)
    assert len(names) == 136
    assert names[0] == "Days for shipment (scheduled)"
