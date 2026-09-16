import sqlite3
from pathlib import Path

import pandas as pd


# ==========================================================
# PATHS
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

CSV_PATH = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "APL_Logistics - APL_Logistics.csv"
)

DB_PATH = (
    PROJECT_ROOT
    / "data"
    / "logisense.db"
)


# ==========================================================
# SETTINGS
# ==========================================================

TABLE_NAME = "shipments"

CHUNK_SIZE = 10_000


# ==========================================================
# MAIN
# ==========================================================

def main():
    print("=" * 60)
    print("LogiSense-AI SQLite Importer")
    print("=" * 60)

    if not CSV_PATH.exists():
        print(f"\nERROR: CSV file not found:")
        print(CSV_PATH)
        return

    DB_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    print("\nCSV:")
    print(CSV_PATH)

    print("\nDatabase:")
    print(DB_PATH)

    print("\nReading CSV in chunks...")

    connection = sqlite3.connect(DB_PATH)

    total_rows = 0

    try:
        first_chunk = True

        for chunk_number, chunk in enumerate(
            pd.read_csv(
                CSV_PATH,
                chunksize=CHUNK_SIZE,
                low_memory=False
            ),
            start=1
        ):

            # ------------------------------------------------
            # Remove cancelled and suspected-fraud records
            # ------------------------------------------------

            if "Order Status" in chunk.columns:
                chunk = chunk[
                    ~chunk["Order Status"]
                    .astype(str)
                    .str.upper()
                    .isin(
                        [
                            "CANCELED",
                            "SUSPECTED_FRAUD",
                        ]
                    )
                ].copy()

            # ------------------------------------------------
            # Write into SQLite
            # ------------------------------------------------

            chunk.to_sql(
                TABLE_NAME,
                connection,
                if_exists="replace" if first_chunk else "append",
                index=False
            )

            first_chunk = False

            total_rows += len(chunk)

            print(
                f"Imported chunk {chunk_number}: "
                f"{len(chunk):,} rows "
                f"| Total: {total_rows:,}"
            )

        # ------------------------------------------------
        # Create indexes for optimal query performance
        # ------------------------------------------------
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_shipments_late_risk ON shipments ("Late_delivery_risk")',
            'CREATE INDEX IF NOT EXISTS idx_shipments_shipping_mode ON shipments ("Shipping Mode")',
            'CREATE INDEX IF NOT EXISTS idx_shipments_market ON shipments ("Market")',
            'CREATE INDEX IF NOT EXISTS idx_shipments_order_region ON shipments ("Order Region")',
            'CREATE INDEX IF NOT EXISTS idx_shipments_customer_segment ON shipments ("Customer Segment")',
        ]
        for query in indexes:
            connection.execute(query)

        connection.commit()

    finally:
        connection.close()

    print("\n" + "=" * 60)
    print("IMPORT COMPLETE")
    print("=" * 60)

    print(
        f"\nRows imported: {total_rows:,}"
    )

    print(
        f"Database created at:\n{DB_PATH}"
    )

    print(
        "\nTable created:"
        f" {TABLE_NAME}"
    )


def create_indexes():
    """Create indexes on existing database without full re-import."""
    if not DB_PATH.exists():
        print(f"Database not found: {DB_PATH}")
        return
    connection = sqlite3.connect(DB_PATH)
    try:
        indexes = [
            'CREATE INDEX IF NOT EXISTS idx_shipments_late_risk ON shipments ("Late_delivery_risk")',
            'CREATE INDEX IF NOT EXISTS idx_shipments_shipping_mode ON shipments ("Shipping Mode")',
            'CREATE INDEX IF NOT EXISTS idx_shipments_market ON shipments ("Market")',
            'CREATE INDEX IF NOT EXISTS idx_shipments_order_region ON shipments ("Order Region")',
            'CREATE INDEX IF NOT EXISTS idx_shipments_customer_segment ON shipments ("Customer Segment")',
        ]
        for query in indexes:
            connection.execute(query)
        connection.commit()
        print("Indexes created successfully on shipments table.")
    finally:
        connection.close()


if __name__ == "__main__":
    main()