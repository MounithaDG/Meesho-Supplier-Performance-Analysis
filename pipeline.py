"""
Meesho Supplier Performance Pipeline
Input: supplier_purchase_orders.csv
Expected columns:
po_id, supplier_id, product_category, order_date, promised_delivery_date,
actual_delivery_date, ordered_qty, received_qty, defect_qty

Run:
  python pipeline.py --input data/supplier_purchase_orders.csv --output outputs
"""
import argparse
from pathlib import Path
import pandas as pd

REQUIRED = [
    "po_id", "supplier_id", "product_category", "order_date",
    "promised_delivery_date", "actual_delivery_date",
    "ordered_qty", "received_qty", "defect_qty"
]

def load_and_validate(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(
            "Input file is missing required columns: " + ", ".join(missing) +
            ". Check README.md and map your source columns before running."
        )
    for col in ["order_date", "promised_delivery_date", "actual_delivery_date"]:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    for col in ["ordered_qty", "received_qty", "defect_qty"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    if df["po_id"].isna().any():
        raise ValueError("po_id contains blank values.")
    if df[["ordered_qty", "received_qty", "defect_qty"]].isna().any().any():
        raise ValueError("Quantity columns contain missing or non-numeric values.")
    if (df[["ordered_qty", "received_qty", "defect_qty"]] < 0).any().any():
        raise ValueError("Quantity columns cannot contain negative values.")
    if df["po_id"].duplicated().any():
        raise ValueError(
            "Duplicate po_id values found. If the source has multiple product lines "
            "per PO, create/use a unique po_line_id and update the script accordingly."
        )
    return df

def calculate_metrics(df: pd.DataFrame):
    # Order is OTIF only when delivered on/before promise date AND received quantity
    # is at least the ordered quantity. Missing actual dates are not on time.
    df["on_time"] = (
        df["actual_delivery_date"].notna() &
        df["promised_delivery_date"].notna() &
        (df["actual_delivery_date"] <= df["promised_delivery_date"])
    )
    df["in_full"] = df["received_qty"] >= df["ordered_qty"]
    df["otif"] = df["on_time"] & df["in_full"]
    df["actual_lead_time_days"] = (
        df["actual_delivery_date"] - df["order_date"]
    ).dt.days
    df["planned_lead_time_days"] = (
        df["promised_delivery_date"] - df["order_date"]
    ).dt.days
    df["lead_time_variance_days"] = (
        df["actual_lead_time_days"] - df["planned_lead_time_days"]
    )
    df["month"] = df["order_date"].dt.to_period("M").astype(str)

    def summarize(group):
        received = group["received_qty"].sum()
        defects = group["defect_qty"].sum()
        return pd.Series({
            "total_orders": group["po_id"].nunique(),
            "otif_orders": int(group["otif"].sum()),
            "otif_rate_pct": round(group["otif"].mean() * 100, 2),
            "defect_units": int(defects),
            "received_units": int(received),
            "defect_rate_pct": round((defects / received) * 100, 2) if received else 0,
            "avg_lead_time_variance_days": round(group["lead_time_variance_days"].mean(), 2)
        })

    supplier = df.groupby("supplier_id", dropna=False).apply(summarize, include_groups=False).reset_index()
    category = df.groupby(["supplier_id", "product_category"], dropna=False).apply(
        summarize, include_groups=False
    ).reset_index()
    monthly = df.groupby(["supplier_id", "product_category", "month"], dropna=False).apply(
        summarize, include_groups=False
    ).reset_index()
    return df, supplier, category, monthly

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="Path to supplier purchase order CSV")
    parser.add_argument("--output", default="outputs", help="Output directory")
    args = parser.parse_args()
    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    data = load_and_validate(Path(args.input))
    detail, supplier, category, monthly = calculate_metrics(data)
    detail.to_csv(output / "order_level_metrics.csv", index=False)
    supplier.to_csv(output / "supplier_baseline_metrics.csv", index=False)
    category.to_csv(output / "supplier_category_metrics.csv", index=False)
    monthly.to_csv(output / "supplier_category_month_metrics.csv", index=False)
    print("Pipeline completed. Output files saved to:", output.resolve())

if __name__ == "__main__":
    main()
