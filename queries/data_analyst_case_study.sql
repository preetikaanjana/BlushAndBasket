-- ==============================================================================
-- BLUSH & BASKET: E-COMMERCE DATA ANALYST SQL CASE STUDY
-- Industry Standard: RetailRocket Clickstream Schema (Adapted for Beauty/Cosmetics)
-- Engine: DuckDB / PostgreSQL / Snowflake Compatible SQL
-- Author: Data Analytics Portfolio
-- ==============================================================================

-- ------------------------------------------------------------------------------
-- BUSINESS QUESTION 1: EXECUTIVE COMMERCIAL METRICS & KPI AUDIT
-- Problem: Calculate total store revenue, order count, total visitors, AOV, 
-- and overall conversion rate across the entire catalog.
-- ------------------------------------------------------------------------------
SELECT 
    COUNT(CASE WHEN event = 'view' THEN 1 END) AS total_views,
    COUNT(CASE WHEN event = 'addtocart' THEN 1 END) AS total_carts,
    COUNT(CASE WHEN event = 'transaction' THEN 1 END) AS total_orders,
    COUNT(DISTINCT visitorid) AS total_unique_visitors,
    SUM(CASE WHEN event = 'transaction' THEN price ELSE 0 END) AS gross_revenue_gmv,
    -- Average Order Value (AOV)
    ROUND(SUM(CASE WHEN event = 'transaction' THEN price ELSE 0 END) / 
          NULLIF(COUNT(CASE WHEN event = 'transaction' THEN 1 END), 0), 2) AS avg_order_value_aov,
    -- Conversion Rates
    ROUND(COUNT(CASE WHEN event = 'addtocart' THEN 1 END) * 100.0 / 
          NULLIF(COUNT(CASE WHEN event = 'view' THEN 1 END), 0), 2) AS view_to_cart_rate_pct,
    ROUND(COUNT(CASE WHEN event = 'transaction' THEN 1 END) * 100.0 / 
          NULLIF(COUNT(CASE WHEN event = 'view' THEN 1 END), 0), 2) AS overall_cvr_pct
FROM events;


-- ------------------------------------------------------------------------------
-- BUSINESS QUESTION 2: WEEKLY USER COHORT RETENTION MATRIX (HEATMAP)
-- Problem: Cohort decay analysis. Group users by their acquisition week (first 
-- activity) and measure retention percentage in subsequent weeks (Week 0 to Week 7).
-- Essential for: Product Analytics, User Churn, and Lifetime Value (LTV) models.
-- ------------------------------------------------------------------------------
WITH user_first_week AS (
    -- Step 1: Identify acquisition week for each user
    SELECT 
        visitorid,
        MIN(date_trunc('week', strptime(date, '%Y-%m-%d'))) AS cohort_week
    FROM events
    GROUP BY visitorid
),
activity AS (
    -- Step 2: Calculate week offset for every subsequent activity
    SELECT 
        e.visitorid,
        u.cohort_week,
        date_trunc('week', strptime(e.date, '%Y-%m-%d')) AS activity_week,
        DATE_DIFF('week', u.cohort_week, date_trunc('week', strptime(e.date, '%Y-%m-%d'))) AS week_offset
    FROM events e
    JOIN user_first_week u ON e.visitorid = u.visitorid
),
cohort_counts AS (
    -- Step 3: Count distinct active users per cohort and week offset
    SELECT 
        strftime(cohort_week, '%Y-%m-%d') AS cohort_week,
        week_offset,
        COUNT(DISTINCT visitorid) AS active_users
    FROM activity
    GROUP BY cohort_week, week_offset
),
cohort_sizes AS (
    -- Step 4: Baseline cohort size at Week 0
    SELECT 
        cohort_week,
        active_users AS cohort_size
    FROM cohort_counts
    WHERE week_offset = 0
)
SELECT 
    c.cohort_week,
    c.week_offset,
    c.active_users,
    s.cohort_size,
    ROUND(c.active_users * 100.0 / s.cohort_size, 1) AS retention_pct
FROM cohort_counts c
JOIN cohort_sizes s ON c.cohort_week = s.cohort_week
WHERE c.week_offset <= 7
ORDER BY c.cohort_week, c.week_offset;


-- ------------------------------------------------------------------------------
-- BUSINESS QUESTION 3: CUSTOMER RFM (RECENCY, FREQUENCY, MONETARY) SEGMENTATION
-- Problem: Rank shoppers on a 1-5 scale using NTILE() window functions and assign
-- high-value marketing segments (Champions, Loyal Customers, At-Risk Churn).
-- ------------------------------------------------------------------------------
WITH customer_rfm_raw AS (
    SELECT 
        visitorid,
        -- Recency: Days elapsed since customer's last interaction
        DATE_DIFF('day', MAX(strptime(date, '%Y-%m-%d')), 
                  (SELECT MAX(strptime(date, '%Y-%m-%d')) + INTERVAL 1 DAY FROM events)) AS recency_days,
        -- Frequency: Total orders completed
        COUNT(CASE WHEN event = 'transaction' THEN 1 END) AS order_frequency,
        COUNT(CASE WHEN event = 'view' THEN 1 END) AS total_views,
        COUNT(CASE WHEN event = 'addtocart' THEN 1 END) AS total_carts,
        -- Monetary: Total gross spend
        COALESCE(SUM(CASE WHEN event = 'transaction' THEN price ELSE 0 END), 0) AS total_spend
    FROM events
    GROUP BY visitorid
),
scored AS (
    SELECT 
        *,
        -- 5 = Most recent (lowest recency days), 1 = Least recent
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        -- 5 = Highest frequency, 1 = Lowest
        NTILE(5) OVER (ORDER BY order_frequency ASC) AS f_score,
        -- 5 = Highest spend, 1 = Lowest
        NTILE(5) OVER (ORDER BY total_spend ASC) AS m_score
    FROM customer_rfm_raw
)
SELECT 
    visitorid,
    recency_days,
    order_frequency,
    total_views,
    total_carts,
    total_spend,
    r_score,
    f_score,
    m_score,
    ROUND((r_score + f_score + m_score) / 3.0, 1) AS rfm_avg,
    CASE 
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal Customers'
        WHEN r_score >= 4 AND f_score <= 2 THEN 'Promising / New'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk (High Value)'
        WHEN r_score <= 2 AND f_score <= 2 THEN 'Hibernating / Churned'
        ELSE 'Potential Loyalists'
    END AS rfm_segment
FROM scored
ORDER BY total_spend DESC;


-- ------------------------------------------------------------------------------
-- BUSINESS QUESTION 4: FULL-FUNNEL JOURNEY DROP-OFF ANALYSIS
-- Problem: Quantify conversion drop-offs between View -> Cart -> Purchase using
-- Window Functions (LAG and FIRST_VALUE).
-- ------------------------------------------------------------------------------
WITH funnel_stages AS (
    SELECT 1 AS stage_idx, '1. Product Views' AS stage_name, COUNT(*) AS event_count, COUNT(DISTINCT visitorid) AS unique_visitors
    FROM events WHERE event = 'view'
    UNION ALL
    SELECT 2, '2. Added to Bag', COUNT(*), COUNT(DISTINCT visitorid)
    FROM events WHERE event = 'addtocart'
    UNION ALL
    SELECT 3, '3. Purchased (Transactions)', COUNT(*), COUNT(DISTINCT visitorid)
    FROM events WHERE event = 'transaction'
)
SELECT 
    stage_idx,
    stage_name,
    event_count,
    unique_visitors,
    -- Step Conversion Rate (% of shoppers continuing from previous stage)
    CASE 
        WHEN LAG(event_count, 1) OVER (ORDER BY stage_idx) IS NULL THEN 100.0
        ELSE ROUND(event_count * 100.0 / LAG(event_count, 1) OVER (ORDER BY stage_idx), 2)
    END AS step_conversion_pct,
    -- Drop-Off Volume
    COALESCE(LAG(event_count, 1) OVER (ORDER BY stage_idx) - event_count, 0) AS drop_off_count,
    -- Overall Cumulative Conversion (% from top of funnel)
    ROUND(event_count * 100.0 / FIRST_VALUE(event_count) OVER (ORDER BY stage_idx), 2) AS overall_conversion_pct
FROM funnel_stages
ORDER BY stage_idx ASC;


-- ------------------------------------------------------------------------------
-- BUSINESS QUESTION 5: CATEGORY PERFORMANCE & WALLET SHARE BREAKDOWN
-- Problem: Calculate category gross revenue, order volume, and percentage share
-- of total store wallet.
-- ------------------------------------------------------------------------------
WITH cat_totals AS (
    SELECT 
        category,
        COUNT(CASE WHEN event = 'view' THEN 1 END) AS views,
        COUNT(CASE WHEN event = 'addtocart' THEN 1 END) AS carts,
        COUNT(CASE WHEN event = 'transaction' THEN 1 END) AS orders,
        COALESCE(SUM(CASE WHEN event = 'transaction' THEN price ELSE 0 END), 0) AS revenue,
        COUNT(DISTINCT visitorid) AS unique_shoppers
    FROM events
    GROUP BY category
),
grand_total AS (
    SELECT SUM(revenue) AS total_revenue FROM cat_totals
)
SELECT 
    c.category,
    c.views,
    c.carts,
    c.orders,
    c.revenue,
    c.unique_shoppers,
    ROUND(c.orders * 100.0 / NULLIF(c.views, 0), 2) AS conversion_rate_pct,
    ROUND(c.revenue * 100.0 / g.total_revenue, 1) AS share_of_wallet_pct,
    ROUND(c.revenue / NULLIF(c.orders, 0), 0) AS avg_order_value
FROM cat_totals c, grand_total g
ORDER BY c.revenue DESC;


-- ------------------------------------------------------------------------------
-- BUSINESS QUESTION 6: MARKET BASKET CO-OCCURRENCE AFFINITY (ROUTINE BUNDLES)
-- Problem: Self-join transactions to identify pairs of products frequently purchased 
-- or carted in the same shopping session.
-- ------------------------------------------------------------------------------
WITH user_item_pairs AS (
    SELECT DISTINCT 
        e1.visitorid, 
        e1.itemid AS item_a_id, 
        e2.itemid AS item_b_id
    FROM events e1
    JOIN events e2 ON e1.visitorid = e2.visitorid AND e1.itemid < e2.itemid
    WHERE e1.event IN ('addtocart', 'transaction') 
      AND e2.event IN ('addtocart', 'transaction')
),
pair_counts AS (
    SELECT 
        item_a_id, 
        item_b_id, 
        COUNT(DISTINCT visitorid) AS cooccurrences
    FROM user_item_pairs
    GROUP BY item_a_id, item_b_id
    ORDER BY cooccurrences DESC
    LIMIT 10
)
SELECT 
    p.cooccurrences,
    e1.item_name AS item_a_name,
    e1.category AS item_a_category,
    AVG(e1.price) AS item_a_price,
    e2.item_name AS item_b_name,
    e2.category AS item_b_category,
    AVG(e2.price) AS item_b_price,
    ROUND(AVG(e1.price) + AVG(e2.price), 0) AS bundle_full_price,
    ROUND((AVG(e1.price) + AVG(e2.price)) * 0.85, 0) AS bundle_discounted_price
FROM pair_counts p
JOIN events e1 ON p.item_a_id = e1.itemid
JOIN events e2 ON p.item_b_id = e2.itemid
GROUP BY p.cooccurrences, e1.item_name, e1.category, e2.item_name, e2.category
ORDER BY p.cooccurrences DESC;
