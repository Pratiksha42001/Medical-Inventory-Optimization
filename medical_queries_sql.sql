/* USE DATABASE */
USE demo;

SELECT COUNT(*) AS total_rows FROM medical_inventory_cleaned;

/*
1️ ABC Analysis — top drugs contributing to ~80% revenue
*/
WITH per_drug AS (
  SELECT DrugName, SUM(Final_Sales) AS total_revenue
  FROM medical_inventory_cleaned
  GROUP BY DrugName
),
tot AS (SELECT SUM(total_revenue) AS grand_total FROM per_drug),
ranked AS (
  SELECT 
    p.DrugName,
    p.total_revenue,
    ROUND(p.total_revenue / t.grand_total * 100, 4) AS pct_of_total,
    SUM(p.total_revenue) OVER (ORDER BY p.total_revenue DESC) AS cumulative_revenue,
    ROUND(SUM(p.total_revenue) OVER (ORDER BY p.total_revenue DESC) / t.grand_total * 100, 4) AS cumulative_pct
  FROM per_drug p CROSS JOIN tot t
)
SELECT *
FROM ranked
WHERE cumulative_pct <= 80
ORDER BY total_revenue DESC;

/*
2️ Safety Stock — rolling 90-day average net sales qty for top 5 drugs
*/
WITH top5 AS (
  SELECT DrugName, SUM(Quantity - COALESCE(ReturnQuantity,0)) AS net_qty
  FROM medical_inventory_cleaned
  WHERE LOWER(Typeofsales) LIKE '%sale%'
  GROUP BY DrugName
  ORDER BY net_qty DESC
  LIMIT 5
),
daily AS (
  SELECT
    DrugName,
    COALESCE(
      STR_TO_DATE(Dateofbill,'%d-%m-%Y'),
      STR_TO_DATE(Dateofbill,'%Y-%m-%d')
    ) AS bill_date,
    SUM(Quantity - COALESCE(ReturnQuantity,0)) AS day_net_qty
  FROM medical_inventory_cleaned
  WHERE LOWER(Typeofsales) LIKE '%sale%'
  GROUP BY DrugName, bill_date
)
SELECT
  d.DrugName,
  d.bill_date,
  ROUND((
    SELECT AVG(d2.day_net_qty)
    FROM daily d2
    WHERE d2.DrugName = d.DrugName
      AND d2.bill_date BETWEEN DATE_SUB(d.bill_date, INTERVAL 89 DAY) AND d.bill_date
  ), 2) AS rolling_90day_avg
FROM daily d
JOIN top5 t ON d.DrugName = t.DrugName
ORDER BY d.DrugName, d.bill_date;

/*
3️ Wastage Rate — top 10 SubCat1 by total RtnMRP and % of sales value
*/
SELECT
  SubCat1,
  SUM(RtnMRP) AS total_wastage,
  SUM(Final_Sales) AS total_sales_value,
  ROUND(SUM(RtnMRP) / NULLIF(SUM(Final_Sales),0) * 100, 4) AS wastage_pct_of_sales
FROM medical_inventory_cleaned
GROUP BY SubCat1
ORDER BY total_wastage DESC
LIMIT 10;

/*
4️ Return Hotspots — % of sold quantity returned per Specialisation
*/
SELECT
  Specialisation,
  SUM(COALESCE(ReturnQuantity,0)) AS total_returned_qty,
  SUM(COALESCE(Quantity,0)) AS total_sold_qty,
  ROUND(SUM(COALESCE(ReturnQuantity,0)) / NULLIF(SUM(COALESCE(Quantity,0)),0) * 100, 4) AS return_pct
FROM medical_inventory_cleaned
GROUP BY Specialisation
ORDER BY return_pct DESC;

/*
5️ Cost Leakage — gross profit margin per Formulation
*/
SELECT
  Formulation,
  SUM(Final_Sales) AS sales_value,
  SUM(Final_Cost) AS cost_value,
  SUM(Final_Sales) - SUM(Final_Cost) AS gross_profit,
  ROUND((SUM(Final_Sales) - SUM(Final_Cost)) / NULLIF(SUM(Final_Sales),0) * 100, 4) AS gross_margin_pct
FROM medical_inventory_cleaned
GROUP BY Formulation
ORDER BY gross_margin_pct DESC;

/*
6️ Low Margin Alerts — drugs with margin ≤ 5%
*/
SELECT
  DrugName,
  SUM(Final_Sales) AS tot_sales,
  SUM(Final_Cost) AS tot_cost,
  ROUND((SUM(Final_Sales) - SUM(Final_Cost)) / NULLIF(SUM(Final_Sales),0) * 100, 4) AS margin_pct
FROM medical_inventory_cleaned
GROUP BY DrugName
HAVING margin_pct <= 5
ORDER BY margin_pct ASC;

/*
7️ MoM & YoY growth in net sales quantity (company-level)
*/
WITH monthly AS (
  SELECT
    DATE_FORMAT(
      COALESCE(
        STR_TO_DATE(Dateofbill,'%d-%m-%Y'),
        STR_TO_DATE(Dateofbill,'%Y-%m-%d')
      ), '%Y-%m-01'
    ) AS month_start,
    SUM(Quantity - COALESCE(ReturnQuantity,0)) AS net_qty
  FROM medical_inventory_cleaned
  WHERE LOWER(Typeofsales) LIKE '%sale%'
  GROUP BY month_start
)
SELECT
  month_start,
  net_qty,
  LAG(net_qty,1) OVER (ORDER BY month_start) AS prev_month_qty,
  ROUND((net_qty - LAG(net_qty,1) OVER (ORDER BY month_start)) / NULLIF(LAG(net_qty,1) OVER (ORDER BY month_start),0) * 100, 2) AS mom_pct,
  LAG(net_qty,12) OVER (ORDER BY month_start) AS prev_year_qty,
  ROUND((net_qty - LAG(net_qty,12) OVER (ORDER BY month_start)) / NULLIF(LAG(net_qty,12) OVER (ORDER BY month_start),0) * 100, 2) AS yoy_pct
FROM monthly
ORDER BY month_start;


/* 8) Peak Demand Periods — top 3 months last 2 years for 'ANTI-INFECTIVES' */

USE demo ;
SELECT SubCat1, Dateofbill, Quantity, ReturnQuantity 
FROM medical_inventory_cleaned
LIMIT 10;

WITH parsed AS (
  SELECT 
    (CASE 
      WHEN STR_TO_DATE(Dateofbill, '%d-%m-%Y') IS NOT NULL THEN STR_TO_DATE(Dateofbill, '%d-%m-%Y')
      WHEN STR_TO_DATE(Dateofbill, '%Y-%m-%d') IS NOT NULL THEN STR_TO_DATE(Dateofbill, '%Y-%m-%d')
      ELSE NULL 
    END) AS bill_date,
    SubCat1,
    Quantity,
    ReturnQuantity
  FROM medical_inventory_cleaned
  WHERE LOWER(SubCat1) LIKE '%anti%'
)
SELECT 
  DATE_FORMAT(bill_date, '%Y-%m') AS Month_Year,
  SUM(Quantity - COALESCE(ReturnQuantity, 0)) AS Net_Sales_Qty
FROM parsed
WHERE bill_date >= DATE_SUB(CURDATE(), INTERVAL 2 YEAR)
GROUP BY Month_Year
ORDER BY Net_Sales_Qty DESC
LIMIT 3;





/*
9️ Departmental Rank — monthly rank by net sales
*/
WITH MonthlyDeptSales AS (
  SELECT
    DATE_FORMAT(
      COALESCE(
        STR_TO_DATE(Dateofbill,'%d-%m-%Y'),
        STR_TO_DATE(Dateofbill,'%Y-%m-%d')
      ), '%Y-%m'
    ) AS month,
    Dept,
    SUM(Final_Sales) AS Total_Sales
  FROM medical_inventory_cleaned
  WHERE LOWER(Typeofsales) LIKE '%sale%'
  GROUP BY month, Dept
)
SELECT
  month,
  Dept,
  Total_Sales,
  RANK() OVER (PARTITION BY month ORDER BY Total_Sales DESC) AS DeptRank
FROM MonthlyDeptSales
ORDER BY month, DeptRank;

/*
10 First Sale Date per Drug
*/
SELECT
  DrugName,
  MIN(
    COALESCE(
      STR_TO_DATE(Dateofbill,'%d-%m-%Y'),
      STR_TO_DATE(Dateofbill,'%Y-%m-%d')
    )
  ) AS First_Sale_Date
FROM medical_inventory_cleaned
WHERE LOWER(Typeofsales) LIKE '%sale%'
GROUP BY DrugName
ORDER BY First_Sale_Date;

/*
1️1 Seasonal Patterns — avg sales qty per drug by quarter
*/
SELECT
  DrugName,
  CONCAT('Q', QUARTER(
    COALESCE(
      STR_TO_DATE(Dateofbill,'%d-%m-%Y'),
      STR_TO_DATE(Dateofbill,'%Y-%m-%d')
    )
  )) AS Quarter,
  ROUND(AVG(Quantity - COALESCE(ReturnQuantity,0)), 2) AS Avg_Sales_Quantity
FROM medical_inventory_cleaned
WHERE LOWER(Typeofsales) LIKE '%sale%'
GROUP BY DrugName, Quarter
ORDER BY DrugName, Quarter;

/*
1️2 New Drug Adoption — newest 5 drugs (first 90 days)
*/
WITH first_sale AS (
  SELECT
    DrugName,
    MIN(COALESCE(
      STR_TO_DATE(Dateofbill,'%d-%m-%Y'),
      STR_TO_DATE(Dateofbill,'%Y-%m-%d')
    )) AS first_sale_date
  FROM medical_inventory_cleaned
  WHERE LOWER(Typeofsales) LIKE '%sale%'
  GROUP BY DrugName
),
five_newest AS (
  SELECT DrugName, first_sale_date
  FROM first_sale
  ORDER BY first_sale_date DESC
  LIMIT 5
)
SELECT
  m.DrugName,
  DATEDIFF(
    COALESCE(
      STR_TO_DATE(m.Dateofbill,'%d-%m-%Y'),
      STR_TO_DATE(m.Dateofbill,'%Y-%m-%d')
    ),
    f.first_sale_date
  ) AS Days_Since_Intro,
  SUM(m.Quantity - COALESCE(m.ReturnQuantity,0)) AS Total_Sales_Volume
FROM medical_inventory_cleaned m
JOIN five_newest f ON m.DrugName = f.DrugName
WHERE LOWER(m.Typeofsales) LIKE '%sale%'
  AND COALESCE(
      STR_TO_DATE(m.Dateofbill,'%d-%m-%Y'),
      STR_TO_DATE(m.Dateofbill,'%Y-%m-%d')
  ) BETWEEN f.first_sale_date AND DATE_ADD(f.first_sale_date, INTERVAL 90 DAY)
GROUP BY m.DrugName, Days_Since_Intro
ORDER BY m.DrugName, Days_Since_Intro;

/*
1️3 Transaction Audit — invalid return quantities
*/
SELECT
  Dateofbill, DrugName, Dept, Quantity, ReturnQuantity
FROM medical_inventory_cleaned
WHERE COALESCE(ReturnQuantity,0) > COALESCE(Quantity,0)
ORDER BY Dateofbill;

SELECT COUNT(*) AS invalid_count
FROM medical_inventory_cleaned
WHERE COALESCE(ReturnQuantity,0) > COALESCE(Quantity,0);

/*
1️4 Sales Trigger — update inventory after insert
*/
DROP TRIGGER IF EXISTS trg_UpdateInventory_med;
DELIMITER $$
CREATE TRIGGER trg_UpdateInventory_med
AFTER INSERT ON medical_inventory_cleaned
FOR EACH ROW
BEGIN
  IF LOWER(NEW.Typeofsales) LIKE '%sale%' THEN
    UPDATE FactInventory
    SET StockQty = StockQty - COALESCE(NEW.Quantity,0) + COALESCE(NEW.ReturnQuantity,0)
    WHERE DrugName = NEW.DrugName;
  END IF;
END$$
DELIMITER ;

/*
1️5 Cost Change Tracking — log cost changes
*/
CREATE TABLE IF NOT EXISTS CostAudit (
  AuditID INT AUTO_INCREMENT PRIMARY KEY,
  DrugName VARCHAR(200),
  Old_Cost DECIMAL(10,2),
  New_Cost DECIMAL(10,2),
  ChangedAt DATETIME DEFAULT CURRENT_TIMESTAMP
);

DROP TRIGGER IF EXISTS trg_CostChange;
DELIMITER $$
CREATE TRIGGER trg_CostChange
AFTER UPDATE ON medical_inventory_cleaned
FOR EACH ROW
BEGIN
  IF NEW.Final_Cost <> OLD.Final_Cost THEN
    INSERT INTO CostAudit (DrugName, Old_Cost, New_Cost)
    VALUES (NEW.DrugName, OLD.Final_Cost, NEW.Final_Cost);
  END IF;
END$$
DELIMITER ;

/*
18 Top Customer Products — for top revenue patient
*/
WITH top_customer AS (
  SELECT Patient_ID, SUM(Final_Sales) AS revenue
  FROM medical_inventory_cleaned
  GROUP BY Patient_ID
  ORDER BY revenue DESC
  LIMIT 1
)
SELECT m.DrugName, SUM(m.Quantity - COALESCE(m.ReturnQuantity,0)) AS net_qty
FROM medical_inventory_cleaned m
JOIN top_customer t ON m.Patient_ID = t.Patient_ID
GROUP BY m.DrugName
ORDER BY net_qty DESC
LIMIT 5;

/*
1-- 9) Sales Frequency — Average days between sales for a specific DrugName*/
SET @drug_name = ' Paracetamol 650mg';

SELECT 
  ROUND(AVG(diff_days), 2) AS avg_days_between_sales
FROM (
  SELECT 
    bill_date,
    DATEDIFF(bill_date, LAG(bill_date) OVER (ORDER BY bill_date)) AS diff_days
  FROM (
    SELECT 
      DISTINCT
      CASE
        WHEN Dateofbill LIKE '%-%-%' THEN STR_TO_DATE(Dateofbill, '%Y-%m-%d')
        WHEN Dateofbill LIKE '%/%/%' THEN STR_TO_DATE(Dateofbill, '%d/%m/%Y')
        ELSE STR_TO_DATE(Dateofbill, '%d-%m-%Y')
      END AS bill_date
    FROM 
      medical_inventory_cleaned
    WHERE 
      DrugName = @drug_name 
      AND LOWER(Typeofsales) LIKE '%sale%' 
      AND Dateofbill IS NOT NULL
  ) AS dated_sales
) AS calculated
WHERE diff_days IS NOT NULL;


/*
2️0 Specialisation Impact — % contribution to total sales
*/
SELECT
  Specialisation,
  SUM(Final_Sales) AS sales_value,
  ROUND(SUM(Final_Sales) / NULLIF((SELECT SUM(Final_Sales) FROM medical_inventory_cleaned),0) * 100, 4) AS pct_of_total
FROM medical_inventory_cleaned
GROUP BY Specialisation
ORDER BY sales_value DESC;


