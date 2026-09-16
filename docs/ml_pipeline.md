# LogiSense-AI ML Pipeline Documentation

## Overview
LogiSense-AI predicts `Late_delivery_risk` (binary classification) using only attributes known at booking/dispatch time.

## Leakage Prevention
All post-delivery and outcome fields are strictly excluded:
1. `Delivery Status` (exact mirror of target)
2. `Days for shipping (real)` (actual delivery time)
3. `Order Status` (finalized lifecycle)
4. Realized financial metrics (sales, profit, discounts)
5. Customer PII (full names, street addresses)


## Model Comparison

- Random Forest (Chosen): Fa = 69.08%, ROC-AUC = 75.47%, Accuracy = 69.21%
- XGBoost: F1 = 68.90%, ROC-AUC = 76.24%, Accuracy = 70.27%
- Logistic Regression: Fa = 67.25%, ROC-AUC = 74.47%, Accuracy = 69.64%

## Explainability
-@ Days for shipment (scheduled) carries the largest influence reducing uncertainty, followed by Shipping Mode Second Class and regional attributes.
