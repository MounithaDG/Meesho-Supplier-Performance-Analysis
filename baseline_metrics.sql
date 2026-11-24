-- Meesho Supplier Performance: baseline SQL (SQLite)
-- Import supplier_purchase_orders.csv as table: purchase_orders
-- Expected columns are listed in README.md.

-- 1. Order-level OTIF and lead-time calculations
CREATE VIEW IF NOT EXISTS order_level_metrics AS
SELECT
    po_id, supplier_id, product_category, order_date,
    promised_delivery_date, actual_delivery_date,
    ordered_qty, received_qty, defect_qty,
    CASE WHEN actual_delivery_date IS NOT NULL
              AND promised_delivery_date IS NOT NULL
              AND date(actual_delivery_date) <= date(promised_delivery_date)
         THEN 1 ELSE 0 END AS on_time,
    CASE WHEN received_qty >= ordered_qty THEN 1 ELSE 0 END AS in_full,
    CASE WHEN actual_delivery_date IS NOT NULL
              AND promised_delivery_date IS NOT NULL
              AND date(actual_delivery_date) <= date(promised_delivery_date)
              AND received_qty >= ordered_qty
         THEN 1 ELSE 0 END AS otif,
    CAST(julianday(actual_delivery_date) - julianday(order_date) AS INTEGER)
      - CAST(julianday(promised_delivery_date) - julianday(order_date) AS INTEGER)
      AS lead_time_variance_days,
    strftime('%Y-%m', order_date) AS month
FROM purchase_orders;

-- 2. Supplier baseline metrics
SELECT
    supplier_id,
    COUNT(DISTINCT po_id) AS total_orders,
    SUM(otif) AS otif_orders,
    ROUND(100.0 * AVG(otif), 2) AS otif_rate_pct,
    SUM(defect_qty) AS defect_units,
    SUM(received_qty) AS received_units,
    ROUND(100.0 * SUM(defect_qty) / NULLIF(SUM(received_qty), 0), 2) AS defect_rate_pct,
    ROUND(AVG(lead_time_variance_days), 2) AS avg_lead_time_variance_days
FROM order_level_metrics
GROUP BY supplier_id
ORDER BY otif_rate_pct DESC;

-- 3. Drill-down: supplier -> product category -> month
SELECT
    supplier_id, product_category, month,
    COUNT(DISTINCT po_id) AS total_orders,
    ROUND(100.0 * AVG(otif), 2) AS otif_rate_pct,
    ROUND(100.0 * SUM(defect_qty) / NULLIF(SUM(received_qty), 0), 2) AS defect_rate_pct,
    ROUND(AVG(lead_time_variance_days), 2) AS avg_lead_time_variance_days
FROM order_level_metrics
GROUP BY supplier_id, product_category, month
ORDER BY supplier_id, product_category, month;
