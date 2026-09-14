"""
LogiSense-AI - Model Training

Trains:
1. Logistic Regression
2. Random Forest
3. XGBoost

Uses the already-preprocessed real dataset from:
data/processed/

No synthetic data is used.
"""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    ConfusionMatrixDisplay,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
    RocCurveDisplay,
)
from xgboost import XGBClassifier


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
EVAL_DIR = MODELS_DIR / "evaluation"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
EVAL_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------
# Settings
# ---------------------------------------------------------

RANDOM_STATE = 42


# ---------------------------------------------------------
# Load data
# ---------------------------------------------------------

def load_data():
    print("\nLoading processed data...")

    X_train = pd.read_csv(PROCESSED_DIR / "X_train.csv")
    X_test = pd.read_csv(PROCESSED_DIR / "X_test.csv")

    y_train = pd.read_csv(PROCESSED_DIR / "y_train.csv").squeeze("columns")
    y_test = pd.read_csv(PROCESSED_DIR / "y_test.csv").squeeze("columns")

    print(f"X_train shape: {X_train.shape}")
    print(f"X_test shape : {X_test.shape}")
    print(f"y_train size : {len(y_train):,}")
    print(f"y_test size  : {len(y_test):,}")

    return X_train, X_test, y_train, y_test


# ---------------------------------------------------------
# Evaluate model
# ---------------------------------------------------------

def evaluate_model(name, model, X_test, y_test):
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roc_auc = roc_auc_score(y_test, y_prob)

    print("\n" + "=" * 70)
    print(name)
    print("=" * 70)

    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1-score : {f1:.4f}")
    print(f"ROC-AUC  : {roc_auc:.4f}")

    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, digits=4))

    results = {
        "model": name,
        "accuracy": round(float(accuracy), 6),
        "precision": round(float(precision), 6),
        "recall": round(float(recall), 6),
        "f1": round(float(f1), 6),
        "roc_auc": round(float(roc_auc), 6),
    }

    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)

    fig, ax = plt.subplots(figsize=(6, 5))
    ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=["On Time", "Late"],
    ).plot(ax=ax)

    ax.set_title(f"{name} - Confusion Matrix")
    fig.tight_layout()

    safe_name = name.lower().replace(" ", "_").replace("-", "")
    fig.savefig(
        EVAL_DIR / f"{safe_name}_confusion_matrix.png",
        dpi=150,
        bbox_inches="tight",
    )
    plt.close(fig)

    # ROC curve
    fig, ax = plt.subplots(figsize=(7, 5))
    RocCurveDisplay.from_predictions(
        y_test,
        y_prob,
        name=name,
        ax=ax,
    )

    ax.set_title(f"{name} - ROC Curve")
    fig.tight_layout()

    fig.savefig(
        EVAL_DIR / f"{safe_name}_roc_curve.png",
        dpi=150,
        bbox_inches="tight",
    )
    plt.close(fig)

    return results


# ---------------------------------------------------------
# Main training function
# ---------------------------------------------------------

def main():
    print("\n")
    print("=" * 70)
    print("LOGISENSE-AI MODEL TRAINING")
    print("=" * 70)

    # Load existing processed data
    X_train, X_test, y_train, y_test = load_data()

    print("\nTraining models using random_state=42...")
    print("Test data will only be used for final evaluation.")

    results = []

    # -----------------------------------------------------
    # 1. Logistic Regression
    # -----------------------------------------------------

    print("\n[1/3] Training Logistic Regression...")

    logistic_model = LogisticRegression(
        max_iter=1000,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    logistic_model.fit(X_train, y_train)

    joblib.dump(
        logistic_model,
        MODELS_DIR / "logistic_regression.joblib",
    )

    logistic_results = evaluate_model(
        "Logistic Regression",
        logistic_model,
        X_test,
        y_test,
    )

    results.append(logistic_results)

    # -----------------------------------------------------
    # 2. Random Forest
    # -----------------------------------------------------

    print("\n[2/3] Training Random Forest...")

    random_forest_model = RandomForestClassifier(
        n_estimators=250,
        max_depth=None,
        min_samples_split=2,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        class_weight="balanced",
    )

    random_forest_model.fit(X_train, y_train)

    joblib.dump(
        random_forest_model,
        MODELS_DIR / "random_forest.joblib",
    )

    random_forest_results = evaluate_model(
        "Random Forest",
        random_forest_model,
        X_test,
        y_test,
    )

    results.append(random_forest_results)

    # -----------------------------------------------------
    # 3. XGBoost
    # -----------------------------------------------------

    print("\n[3/3] Training XGBoost...")

    xgb_model = XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.8,
        objective="binary:logistic",
        eval_metric="logloss",
        random_state=RANDOM_STATE,
        n_jobs=-1,
        tree_method="hist",
    )

    xgb_model.fit(X_train, y_train)

    joblib.dump(
        xgb_model,
        MODELS_DIR / "xgboost.joblib",
    )

    xgb_results = evaluate_model(
        "XGBoost",
        xgb_model,
        X_test,
        y_test,
    )

    results.append(xgb_results)

    # -----------------------------------------------------
    # Compare models
    # -----------------------------------------------------

    results_df = pd.DataFrame(results)

    results_df = results_df.sort_values(
        by=["f1", "roc_auc"],
        ascending=False,
    ).reset_index(drop=True)

    print("\n")
    print("=" * 70)
    print("MODEL COMPARISON")
    print("=" * 70)

    print(
        results_df.to_string(
            index=False,
            float_format=lambda x: f"{x:.4f}",
        )
    )

    # Save comparison
    results_df.to_csv(
        EVAL_DIR / "model_comparison.csv",
        index=False,
    )

    # Save JSON
    with open(
        EVAL_DIR / "model_metrics.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            results,
            file,
            indent=2,
        )

    # -----------------------------------------------------
    # Select best model
    # -----------------------------------------------------

    best_model_name = results_df.iloc[0]["model"]

    model_objects = {
        "Logistic Regression": logistic_model,
        "Random Forest": random_forest_model,
        "XGBoost": xgb_model,
    }

    best_model = model_objects[best_model_name]

    joblib.dump(
        best_model,
        MODELS_DIR / "best_model.joblib",
    )

    with open(
        MODELS_DIR / "best_model_info.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            {
                "best_model": best_model_name,
                "selection_rule": "Highest F1-score, then ROC-AUC",
                "random_state": RANDOM_STATE,
            },
            file,
            indent=2,
        )

    # -----------------------------------------------------
    # Final report
    # -----------------------------------------------------

    print("\n")
    print("=" * 70)
    print("BEST MODEL")
    print("=" * 70)

    print(f"Model : {best_model_name}")
    print(
        f"F1    : {results_df.iloc[0]['f1']:.4f}"
    )
    print(
        f"ROC-AUC: {results_df.iloc[0]['roc_auc']:.4f}"
    )

    print("\nSaved model:")
    print(MODELS_DIR / "best_model.joblib")

    print("\nSaved evaluation files:")
    print(EVAL_DIR)

    print("\nTraining completed successfully.")
    print("=" * 70)


if __name__ == "__main__":
    main()