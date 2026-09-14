# Feature Documentation — Late_delivery_risk

> **Modeling rule:** we predict `Late_delivery_risk` **before** a delivery
> happens. Every feature must therefore be knowable at order/booking time.
> Anything that is only visible *after* delivery is excluded (see §3).

- Source: `data/raw/APL_Logistics - APL_Logistics.csv` (180,519 rows × 40 cols)
- Pipeline: `backend/ml/preprocessing.py`
- After row filtering: **172,765 rows** (`CANCELED` / `SUSPECTED_FRAUD` orders removed)
- Train / Test: **138,212 / 34,553**, stratified on the target, `random_state=42`
- Final processed features: **136**

---

## 1. Included features

**Numeric (1) — scaled with `StandardScaler`:**
| Column | Notes |
|---|---|
| `Days for shipment (scheduled)` | The number of days the carrier *promises* ahead of time. Only pre-delivery signal with real strength (r ≈ −0.37). |

**Categorical (7) — one-hot encoded (`drop="first"`):**
| Column | Distinct values | Why kept |
|---|---|---|
| `Shipping Mode` | 4 (Standard / Second / First Class, Same Day) | Service level drives promised lead time. |
| `Market` | 5 (LATAM, Europe, Pacific Asia, USCA, Africa) | Geography at a coarse, stable grain. |
| `Order Region` | 23 | Cross-border logistics effort. |
| `Customer Segment` | 3 (Consumer / Corporate / Home Office) | B2B vs B2C expectation differences. |
| `Customer State` | 46 | Domestic regional effects. |
| `Category Name` | 50 | Product family affects handling/lead time. |
| `Department Name` | 11 (Golf, Footwear, Fan Shop, …) | Higher-level product grouping. |

Encoded as `Shipping Mode_First Class`, `Category Name_Fishing`, … (136 total columns).

## 2. Excluded (but harmless / available pre-delivery)

| Column(s) | Reason |
|---|---|
| `Order City` | 3,597 unique values — far too sparse to be a stable predictor. |
| `Order Country` | 164 unique values — too sparse. |
| `Customer City` | 563 unique values — too sparse. |
| `Product Name` | 118 values — fully captured by `Category Name` + `Department Name`. |
| `Customer Country` | Only 2 values, redundant with `Customer State`. |
| `Type` (payment method) | Unrelated to logistics; ~0 correlation with the target. |
| `Latitude`, `Longitude` | ~0 correlation with the target. |

## 3. Excluded — leakage / post-delivery / PII (the important part)

| Column | Category | Why excluded |
|---|---|---|
| `Delivery Status` | **outcome** | Is the target itself: every row with `Delivery Status = "Late delivery"` has `Late_delivery_risk = 1` (98,977 rows, exact match). |
| `Days for shipping (real)` | **outcome** | The real delivery time; `real − scheduled` reproduces the label with ~97.6% agreement. It *is* the delay, measured after the fact. |
| `Order Status` | post | Lifecycle flag finalized later (`CANCELED`, `PROCESSING`, …). Used in this pipeline *only* to filter out non-deliveries. |
| `Order Item Quantity` | post/noise | Realized during fulfillment; ~0 correlation. |
| `Order Item Discount`, `Order Item Discount Rate`, `Order Item Product Price`, `Order Item Total`, `Sales`, `Product Price` | post | Monetary values known at checkout but ~0 correlation with delivery risk. |
| `Order Item Profit Ratio`, `Order Profit Per Order`, `Benefit per order`, `Sales per customer` | post | Profit is measured *after* delivery; also ~0 correlation. |
| `Customer Fname`, `Customer Lname`, `Customer Street` | PII | Free-form personal data, high cardinality, zero predictive value, a compliance burden. |
| `Customer Zipcode` | PII | Postal code, 3 missing, high cardinality. |
| `Customer Id`, `Order Customer Id` | PII | 180k unique identifiers — no standalone signal. |
| `Latitude`, `Longitude` | — | Covered under §2. |

**Rule of thumb used:** if a column's value can only be known *after* the
shipment arrives, it cannot be used to predict whether it arrives late.

## 4. Sanity-check guarantee

`select_features()` raises `ValueError` if any column from §3 is ever added back
into `FEATURE_COLUMNS`, so future edits cannot silently reintroduce leakage.

## 5. Reproducibility

- Seed: `random_state = 42` (split is deterministic).
- Pipeline artifact: `models/preprocessing_pipeline.joblib` — reuse at prediction
  time so new rows get the **same** encoding/scaling learned from the train set.
- Feature order: `models/feature_names.json`.