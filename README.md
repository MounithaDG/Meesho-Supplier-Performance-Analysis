# Meesho Supply Chain — Checkpoint 2 starter pipeline

## Purpose
This package provides a repeatable Python/SQL pipeline structure for supplier baseline metrics.
It is a reusable implementation template, not a completed analysis of Meesho data.

## Data availability warning
The project page lists `da_bus_routes.csv`, `da_journey_records.csv`, and
`da_ridership_summary.csv`. Their filenames indicate transport/ridership data, not supplier
purchase orders. The actual contents have not been validated here. Do not use these files
to claim supplier OTIF, defect, or lead-time results. Ask the coordinator for the correct
18-month purchase-order dataset.

## Expected source columns
- `po_id`: unique purchase-order line identifier (must be unique in this starter script)
- `supplier_id`
- `product_category`
- `order_date`
- `promised_delivery_date`
- `actual_delivery_date`
- `ordered_qty`
- `received_qty`
- `defect_qty`

If the source has multiple lines per purchase order, use a unique `po_line_id` and update
the script's identifier accordingly. If source column names differ, map/rename them before
running. Confirm how cancelled orders, returns, split deliveries, and missing delivery dates
should be treated with the stakeholder.

## Metric definitions used in this draft
- **OTIF:** A record is on-time when actual delivery date is on or before promised date,
  and in-full when received quantity is at least ordered quantity. OTIF is the percentage
  of records satisfying both conditions.
- **Defect rate:** Total defect units / total received units × 100.
- **Lead-time variance:** (actual delivery date − order date) −
  (promised delivery date − order date), in days. Positive means later than planned.

These definitions are proposed and should be confirmed with the stakeholder before sign-off.
For missing actual delivery dates, the draft treats the record as not on-time and leaves
lead-time variance blank.

## Run the Python pipeline
1. Install Python 3.11 or use Google Colab.
2. Install dependency: `pip install pandas`
3. Place the correct source file at `data/supplier_purchase_orders.csv`.
4. Run:
   `python pipeline.py --input data/supplier_purchase_orders.csv --output outputs`

The pipeline writes:
- `order_level_metrics.csv`
- `supplier_baseline_metrics.csv`
- `supplier_category_metrics.csv`
- `supplier_category_month_metrics.csv`

## SQL workflow
Import the correct CSV into SQLite as `purchase_orders`, then run
`baseline_metrics.sql` in DB Browser for SQLite. The SQL file creates an order-level
view and includes supplier and supplier-category-month queries.

## Baseline result status
No numeric baseline metrics are included because the required supplier purchase-order
dataset has not been provided/verified. Populate results only after running the pipeline
on the correct source data.

## Version control (Git)
From this folder:
```bash
git init
git add pipeline.py baseline_metrics.sql README.md requirements.txt .gitignore
git commit -m "Add supplier performance baseline pipeline"
```
Create a GitHub repository, then connect and push:
```bash
git branch -M main
git remote add origin https://github.com/<your-username>/<repository-name>.git
git push -u origin main
```
Replace the URL placeholder with your actual repository URL. Do not submit a fabricated repository link.
