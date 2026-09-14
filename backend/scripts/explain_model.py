"""
LogiSense-AI - Fast Model Explainability

Uses Random Forest feature_importances_ instead of SHAP.
This is much faster and gives global feature importance
for the dashboard.
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
EVAL_DIR = MODELS_DIR / "evaluation"

BEST_MODEL_PATH = MODELS_DIR / "best_model.joblib"
FEATURE_NAMES_PATH = MODELS_DIR / "feature_names.json"

EVAL_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():
    print("\n" + "=" * 70)
    print("LOGISENSE-AI FAST MODEL EXPLAINABILITY")
    print("=" * 70)

    # Load model
    print("\nLoading best model...")

    model = joblib.load(BEST_MODEL_PATH)

    print(f"Model: {type(model).__name__}")

    # Load feature names
    with open(FEATURE_NAMES_PATH, "r", encoding="utf-8") as file:
        feature_names = json.load(file)

    print(f"Features: {len(feature_names)}")

    # -----------------------------------------------------
    # Feature importance
    # -----------------------------------------------------

    if not hasattr(model, "feature_importances_"):
        raise ValueError(
            "The saved best model does not support "
            "feature_importances_."
        )

    importances = model.feature_importances_

    if len(importances) != len(feature_names):
        raise ValueError(
            f"Feature mismatch: model has {len(importances)} "
            f"importances but feature_names.json has "
            f"{len(feature_names)} names."
        )

    importance_df = pd.DataFrame(
        {
            "feature": feature_names,
            "importance": importances,
        }
    )

    importance_df = importance_df.sort_values(
        by="importance",
        ascending=False,
    ).reset_index(drop=True)

    # Save all feature importance
    importance_df.to_csv(
        EVAL_DIR / "feature_importance.csv",
        index=False,
    )

    # -----------------------------------------------------
    # Top 20 features
    # -----------------------------------------------------

    top_20 = importance_df.head(20)

    print("\n" + "=" * 70)
    print("TOP 20 IMPORTANT FEATURES")
    print("=" * 70)

    print(
        top_20.to_string(
            index=False,
            float_format=lambda x: f"{x:.6f}",
        )
    )

    # Save top features
    top_20.to_csv(
        EVAL_DIR / "top_20_features.csv",
        index=False,
    )

    # Save JSON
    with open(
        EVAL_DIR / "top_features.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            top_20.to_dict(orient="records"),
            file,
            indent=2,
        )

    # -----------------------------------------------------
    # Plot
    # -----------------------------------------------------

    plot_df = importance_df.head(15).sort_values(
        by="importance",
        ascending=True,
    )

    plt.figure(figsize=(10, 7))

    plt.barh(
        plot_df["feature"],
        plot_df["importance"],
    )

    plt.xlabel("Feature Importance")
    plt.ylabel("Feature")
    plt.title(
        "LogiSense-AI - Top 15 Feature Importance"
    )

    plt.tight_layout()

    plt.savefig(
        EVAL_DIR / "feature_importance.png",
        dpi=150,
        bbox_inches="tight",
    )

    plt.close()

    # -----------------------------------------------------
    # Metadata
    # -----------------------------------------------------

    metadata = {
        "model": type(model).__name__,
        "method": "Random Forest feature_importances_",
        "total_features": len(feature_names),
        "top_features_saved": 20,
    }

    with open(
        EVAL_DIR / "explainability_metadata.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metadata,
            file,
            indent=2,
        )

    # -----------------------------------------------------
    # Final report
    # -----------------------------------------------------

    print("\n" + "=" * 70)
    print("EXPLAINABILITY COMPLETED")
    print("=" * 70)

    print("\nCreated files:")
    print("  feature_importance.csv")
    print("  top_20_features.csv")
    print("  top_features.json")
    print("  feature_importance.png")
    print("  explainability_metadata.json")

    print("\nLocation:")
    print(EVAL_DIR)

    print("\nDone.")


if __name__ == "__main__":
    main()