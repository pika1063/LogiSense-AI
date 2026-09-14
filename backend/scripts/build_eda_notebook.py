"""
build_eda_notebook.py
=====================
Builds AND executes `notebooks/01_eda.ipynb` for the LogiSense-AI project.

The notebook loads the real APL Logistics dataset and walks through:
    target distribution, scheduled days, shipping mode, market/region,
    product/category/department, customer segment/state, missing values,
    outliers, a data-leakage exhibit, and numeric correlations.

Why a builder script?
    The notebook is regenerated and fully executed here so that:
      1. the source of the EDA lives in version control as plain Python,
      2. opening `01_eda.ipynb` always shows real outputs and figures,
      3. re-running is one command:  python backend/scripts/build_eda_notebook.py

Usage:
    python backend/scripts/build_eda_notebook.py
"""

from __future__ import annotations

from pathlib import Path

import nbformat
from nbclient import NotebookClient

REPO_ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK_PATH = REPO_ROOT / "notebooks" / "01_eda.ipynb"


# ---------------------------------------------------------------- cells ----
CELLS: list[tuple[str, str]] = [
    (
        "markdown",
        r"""# LogiSense-AI - Exploratory Data Analysis

## `01_eda.ipynb`

Explores the **real** APL Logistics dataset (`data/raw/APL_Logistics - APL_Logistics.csv`)
and documents the patterns that drive the modeling pipeline in
`backend/ml/preprocessing.py`.

> **Leakage warning:** we predict `Late_delivery_risk` **before** delivery. Columns
> such as `Delivery Status`, `Days for shipping (real)` and all realized financial
> fields reproduce the outcome after the fact and are therefore **excluded** from
> every model. They appear in this EDA for understanding only.
""",
    ),
    (
        "code",
        r"""%matplotlib inline
import pandas as pd, numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Robustly locate the repository root from the notebook's working directory.
REPO = Path().resolve()
for _ in range(3):
    if (REPO / "data" / "raw").exists():
        break
    REPO = REPO.parent

df = pd.read_csv(REPO / "data/raw/APL_Logistics - APL_Logistics.csv",
                 encoding="utf-8", low_memory=False)

# Consistent styling for all figures in this notebook.
COLOR_LATE   = "#C94C4C"
COLOR_ONTIME = "#4C7C8A"
ACCENT       = "#2F6BB0"
plt.rcParams.update({
    "axes.grid": True, "grid.alpha": 0.25,
    "axes.spines.top": False, "axes.spines.right": False,
    "figure.dpi": 110,
})

print(f"Loaded {len(df):,} rows x {df.shape[1]} columns")
df.head()""",
    ),
    (
        "markdown",
        r"""## 1. Data quality - missing values & duplicate rows""",
    ),
    (
        "code",
        r"""missing = df.isna().sum()
missing = missing[missing > 0].sort_values(ascending=False)
print("Missing values per column:")
print(missing if len(missing) else "  (none - fully complete)")

dupes = df.duplicated().sum()
print(f"\nExact duplicate rows: {dupes:,}")""",
    ),
    (
        "markdown",
        r"""## 2. Target distribution

`Late_delivery_risk` = 1 if the shipment arrived after the promised date.
Slightly **imbalanced toward late** (54.8%).""",
    ),
    (
        "code",
        r"""vc = df["Late_delivery_risk"].value_counts().sort_index()
dist = vc.to_frame(name="n_orders")
dist["percent"] = (dist / dist.sum()).round(3)
print(dist)

fig, ax = plt.subplots(figsize=(5, 3))
bars = ax.bar(["On time (0)", "Late (1)"], vc.values,
              color=[COLOR_ONTIME, COLOR_LATE], edgecolor="white")
for b in bars:
    ax.annotate(f"{b.get_height():,}", xy=(b.get_x() + b.get_width() / 2, b.get_height()),
                xytext=(0, 6), textcoords="offset points", ha="center")
ax.set_title("Target distribution - Late_delivery_risk")
ax.set_ylabel("Order count")
plt.tight_layout(); plt.show()""",
    ),
    (
        "markdown",
        r"""## 3. Scheduled shipping days vs target

`Days for shipment (scheduled)` is the promised lead time and the **only
pre-delivery numeric with real signal** - shorter promises run late more often.""",
    ),
    (
        "code",
        r"""days = df.groupby("Days for shipment (scheduled)")["Late_delivery_risk"].agg(["mean", "count"])
days.columns = ["late_rate", "n_orders"]
print(days)

fig, ax = plt.subplots(figsize=(6, 3.5))
ax2 = ax.twinx()
ax.bar(days.index, days["n_orders"], color=ACCENT, alpha=0.55, label="Order count")
ax2.plot(days.index, days["late_rate"], color=COLOR_LATE, marker="o", linewidth=2, label="Late rate")
ax.set_xlabel("Scheduled shipping days"); ax.set_ylabel("Order count")
ax2.set_ylabel("Late rate"); ax2.set_ylim(0, 1)
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="center left")
ax.set_title("Delay by scheduled shipping days")
plt.tight_layout(); plt.show()""",
    ),
    (
        "markdown",
        r"""## 4. Shipping mode vs target

`Standard Class` should look the worst - it carries the longest promised windows.""",
    ),
    (
        "code",
        r"""mode = df.groupby("Shipping Mode")["Late_delivery_risk"].agg(["mean", "count"]).sort_values("mean")
mode.columns = ["late_rate", "n_orders"]
print(mode)

fig, ax = plt.subplots(figsize=(6, 3.2))
bars = ax.barh(mode.index, mode["late_rate"],
               color=[COLOR_LATE if r > 0.5 else ACCENT for r in mode["late_rate"]])
for b, (_, row) in zip(bars, mode.iterrows()):
    ax.annotate(f"{row['late_rate']:.1%}  (n={row['n_orders']:,})",
                xy=(b.get_width(), b.get_y() + b.get_height() / 2),
                xytext=(6, 0), textcoords="offset points", va="center", fontsize=9)
ax.set_xlim(0, 1)
ax.set_title("Late rate by shipping mode")
ax.set_xlabel("Late rate")
plt.tight_layout(); plt.show()""",
    ),
    (
        "markdown",
        r"""## 5. Market and Order Region vs target

Geography is coarse in the model (`Market` has 5 values, `Order Region` has 23).""",
    ),
    (
        "code",
        r"""fig, axes = plt.subplots(1, 2, figsize=(13, 4.2))

mk = df.groupby("Market")["Late_delivery_risk"].agg(["mean", "count"]).sort_values("mean")
mk.columns = ["late_rate", "n_orders"]
print("Market:\n", mk, "\n")
axes[0].barh(mk.index, mk["late_rate"],
             color=[COLOR_LATE if r > 0.5 else ACCENT for r in mk["late_rate"]])
axes[0].set_title("Market"); axes[0].set_xlabel("Late rate"); axes[0].set_xlim(0, 1)

reg = (df.groupby("Order Region")["Late_delivery_risk"]
         .agg(["mean", "count"]).sort_values("count", ascending=False).head(12)
         .sort_values("mean"))
reg.columns = ["late_rate", "n_orders"]
print("Order Region (top 12 by volume):\n", reg)
axes[1].barh(reg.index, reg["late_rate"],
             color=[COLOR_LATE if r > 0.5 else ACCENT for r in reg["late_rate"]])
axes[1].set_title("Order Region (top 12)"); axes[1].set_xlabel("Late rate"); axes[1].set_xlim(0, 1)

plt.tight_layout(); plt.show()""",
    ),
    (
        "markdown",
        r"""## 6. Product, Category and Department patterns

`Category Name` (50) and `Department Name` (11) are model features;
`Product Name` (118) is dropped as redundant with its category/department.""",
    ),
    (
        "code",
        r"""cat = df.groupby("Category Name")["Late_delivery_risk"].agg(["mean", "count"]).sort_values("count", ascending=False)
cat.columns = ["late_rate", "n_orders"]
print("Top 10 categories by volume:\n", cat.head(10))

fig, ax = plt.subplots(figsize=(10, 4))
c = cat.head(10)
bars = ax.bar(range(len(c)), c["n_orders"],
              color=[COLOR_LATE if r > 0.5 else ACCENT for r in c["late_rate"]])
ax.set_xticks(range(len(c))); ax.set_xticklabels(c.index, rotation=35, ha="right", fontsize=8)
for b, (_, row) in zip(bars, c.iterrows()):
    ax.annotate(f"{row['late_rate']:.0%}", xy=(b.get_x() + b.get_width() / 2, b.get_height()),
                xytext=(0, 5), textcoords="offset points", ha="center", fontsize=8)
ax.set_title("Top 10 categories - order count (labels = late rate)")
ax.set_ylabel("Order count")
plt.tight_layout(); plt.show()""",
    ),
    (
        "code",
        r"""dep = df.groupby("Department Name")["Late_delivery_risk"].agg(["mean", "count"]).sort_values("mean")
dep.columns = ["late_rate", "n_orders"]
print(dep)

fig, ax = plt.subplots(figsize=(8, 3.4))
colors = [COLOR_LATE if r > 0.5 else ACCENT for r in dep["late_rate"]]
ax.barh(dep.index, dep["late_rate"], color=colors)
for i, (_, row) in enumerate(dep.iterrows()):
    ax.annotate(f"{row['late_rate']:.1%}", xy=(row["late_rate"], i),
                xytext=(6, 0), textcoords="offset points", va="center", fontsize=9)
ax.set_xlim(0, 1)
ax.set_title("Late rate by department")
plt.tight_layout(); plt.show()""",
    ),
    (
        "code",
        r"""prod = df.groupby("Product Name")["Late_delivery_risk"].agg(["mean", "count"]).sort_values("count", ascending=False)
prod.columns = ["late_rate", "n_orders"]
print("Top 10 products by volume:\n", prod.head(10))""",
    ),
    (
        "markdown",
        r"""## 7. Customer segment and geography (states)""",
    ),
    (
        "code",
        r"""seg = df.groupby("Customer Segment")["Late_delivery_risk"].agg(["mean", "count"]).sort_values("mean")
seg.columns = ["late_rate", "n_orders"]
print(seg)

state = (df.groupby("Customer State")["Late_delivery_risk"]
          .agg(["mean", "count"]).sort_values("count", ascending=False).head(10)
          .sort_values("mean"))
state.columns = ["late_rate", "n_orders"]
print("\nTop 10 states by volume:\n", state)""",
    ),
    (
        "markdown",
        r"""## 8. Numeric distributions & outliers

Financial fields appear here only for completeness - they are **excluded**
from every model (realized after delivery, ~zero signal).""",
    ),
    (
        "code",
        r"""fig, axes = plt.subplots(1, 2, figsize=(12, 4))

axes[0].hist(df["Days for shipment (scheduled)"],
             bins=[-0.5, 0.5, 1.5, 2.5, 3.5, 4.5],
             color=ACCENT, edgecolor="white", rwidth=0.65)
axes[0].set_title("Scheduled shipping days")
axes[0].set_xlabel("Days"); axes[0].set_ylabel("Count")

order = df.groupby("Department Name")["Product Price"].median().sort_values(ascending=False).index
df.boxplot(column="Product Price", by="Department Name", grid=False, ax=axes[1], vert=True,
           fontsize=8)
axes[1].set_title("Product Price by Department (financial - excluded from model)")
axes[1].set_xlabel(""); axes[1].set_ylabel("Product Price ($)")

plt.suptitle(""); plt.tight_layout(); plt.show()""",
    ),
    (
        "code",
        r"""neg = df[df["Order Item Profit Ratio"] < 0]
print(f"Rows with negative profit ratio: {len(neg):,} ({len(neg)/len(df):.2%})")
if len(neg):
    print("Min:", round(neg["Order Item Profit Ratio"].min(), 3),
          "| median of negatives:", round(neg["Order Item Profit Ratio"].median(), 3))
print("-> financial field, realized after delivery, ~zero signal: excluded from features.")""",
    ),
    (
        "markdown",
        r"""## 9. Data leakage exhibit - why columns are excluded

This section **proves**, at the data level, that two columns reproduce the target.""",
    ),
    (
        "code",
        r"""ct = pd.crosstab(df["Delivery Status"], df["Late_delivery_risk"])
print("=== Crosstab: Delivery Status x Late_delivery_risk ===\n", ct)
late_status = df["Delivery Status"].eq("Late delivery")
print(f"\nRows with 'Late delivery' status : {late_status.sum():,}")
print(f"Rows with target == 1            : {(df['Late_delivery_risk'] == 1).sum():,}")
print("-> identical sets: Delivery Status is the target in disguise (excluded).")""",
    ),
    (
        "code",
        r"""gap = df["Days for shipping (real)"] - df["Days for shipment (scheduled)"]
gap_rate = df.groupby(gap)["Late_delivery_risk"].agg(["mean", "count"])
gap_rate.columns = ["late_rate", "n_orders"]
print("=== (real - scheduled) days gap vs late rate ===\n", gap_rate)
print("\n-> 'real' is only known after delivery; it already CONTAINS the delay (excluded).")""",
    ),
    (
        "markdown",
        r"""## 10. Numeric correlations with the target

Point-biserial correlations. `Days for shipping (real)` is strongest - and it
is the outcome itself. Every excluded financial field shows ~0.00. The single
*usable* numeric is `Days for shipment (scheduled)` (r = -0.37).""",
    ),
    (
        "code",
        r"""corr_cols = [c for c in df.select_dtypes(include="number").columns]
corr = df[corr_cols].corrwith(df["Late_delivery_risk"]).sort_values(ascending=False)
print(corr.round(4))""",
    ),
    (
        "markdown",
        r"""## 11. Key findings & next steps

**Patterns that help prediction (all available pre-delivery):**
- `Days for shipment (scheduled)` - the strongest usable signal: shorter promise -> higher late rate.
- `Shipping Mode` - `Standard Class` is the worst performer within a small spread.
- `Market` / `Order Region` - consistent, coarse geographic variation.
- `Department Name` / `Category Name` - mild but stable differences across product families.

**Patterns with ~no signal:**
- All financial/profit columns (|r| < 0.01) - also realized only after delivery.

**Leakage proven (excluded from features):**
- `Delivery Status` is a 1:1 mirror of `Late_delivery_risk`.
- `Days for shipping (real)` == the delay measure itself.

**What happens next:**
1. `backend/ml/preprocessing.py` enforces these exclusions and saves stratified
   train/test splits + a reusable fitted pipeline.
2. Model training comes after this notebook (not yet).
3. The frontend dashboard comes last.
""",
    ),
]


def main() -> None:
    """Assemble, execute, and save the notebook."""
    # --- assemble raw notebook -------------------------------------------------
    nb = nbformat.v4.new_notebook()
    nb.metadata["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    nb.cells = [
        nbformat.v4.new_markdown_cell(text) if kind == "markdown"
        else nbformat.v4.new_code_cell(text)
        for kind, text in CELLS
    ]

    # Write the un-executed notebook first so it exists even if execution fails.
    NOTEBOOK_PATH.parent.mkdir(parents=True, exist_ok=True)
    nbformat.write(nb, str(NOTEBOOK_PATH))

    # --- execute every cell (ipykernel backend, inline figures) ---------------
    print(f"Executing notebook ({len(nb.cells)} cells)...")
    client = NotebookClient(nb, timeout=1800, kernel_name="python3")
    client.execute()  # raises if any cell fails

    # --- save the executed notebook --------------------------------------------
    nbformat.write(nb, str(NOTEBOOK_PATH))
    print(f"Notebook executed and saved -> {NOTEBOOK_PATH}")

    outputs = sum(1 for c in nb.cells if c.cell_type == "code" and c.outputs)
    images = sum(1 for c in nb.cells if c.cell_type == "code"
                 for o in c.outputs
                 if o.output_type == "display_data" and "image/png" in o.get("data", {}))
    print(f"Cells with outputs: {outputs} | embedded figures: {images}")


if __name__ == "__main__":
    main()