"""
DuckDB Analytical Engine for Nykaa-Inspired Beauty Commerce
Provides SQL aggregations, window functions, ranking, and co-occurrence queries.
"""

import duckdb
import pandas as pd

class BeautyDuckDBEngine:
    def __init__(self, events_parquet="data/beauty_events.parquet"):
        self.con = duckdb.connect(database=":memory:")
        self.events_parquet = events_parquet
        self._register_views()

    def _register_views(self):
        self.con.execute(f"CREATE OR REPLACE VIEW events AS SELECT * FROM read_parquet('{self.events_parquet}')")

    def get_daily_event_trends(self, category=None):
        """Priority 1: Daily event trend (Pandas/SQL time-series aggregation)."""
        where_clause = f"WHERE category = '{category}'" if category and category != 'All' else ""
        sql = f"""
        SELECT 
            date,
            COUNT(CASE WHEN event = 'view' THEN 1 END) AS views,
            COUNT(CASE WHEN event = 'addtocart' THEN 1 END) AS add_to_carts,
            COUNT(CASE WHEN event = 'transaction' THEN 1 END) AS transactions,
            COUNT(*) AS total_events
        FROM events
        {where_clause}
        GROUP BY date
        ORDER BY date ASC;
        """
        return self.con.execute(sql).df(), sql

    def get_conversion_funnel(self, category=None):
        """Priority 2: Conversion funnel (CTEs, window functions, customer journey analysis)."""
        where_clause = f"WHERE category = '{category}'" if category and category != 'All' else ""
        sql = f"""
        WITH funnel_stages AS (
            SELECT 
                1 AS stage_idx, '1. Product Views' AS stage_name, COUNT(*) AS event_count, COUNT(DISTINCT visitorid) AS unique_visitors
            FROM events {where_clause} {"AND" if where_clause else "WHERE"} event = 'view'
            UNION ALL
            SELECT 
                2, '2. Added to Cart', COUNT(*), COUNT(DISTINCT visitorid)
            FROM events {where_clause} {"AND" if where_clause else "WHERE"} event = 'addtocart'
            UNION ALL
            SELECT 
                3, '3. Purchased (Transactions)', COUNT(*), COUNT(DISTINCT visitorid)
            FROM events {where_clause} {"AND" if where_clause else "WHERE"} event = 'transaction'
        ),
        funnel_metrics AS (
            SELECT 
                stage_idx,
                stage_name,
                event_count,
                unique_visitors,
                FIRST_VALUE(event_count) OVER (ORDER BY stage_idx) AS top_of_funnel,
                LAG(event_count, 1) OVER (ORDER BY stage_idx) AS prev_stage_count,
                -- Step Conversion Rate
                CASE 
                    WHEN LAG(event_count, 1) OVER (ORDER BY stage_idx) IS NULL THEN 100.0
                    ELSE ROUND(event_count * 100.0 / LAG(event_count, 1) OVER (ORDER BY stage_idx), 2)
                END AS step_conversion_pct,
                -- Drop-off Count
                COALESCE(LAG(event_count, 1) OVER (ORDER BY stage_idx) - event_count, 0) AS drop_off_count,
                -- Cumulative Conversion Rate
                ROUND(event_count * 100.0 / FIRST_VALUE(event_count) OVER (ORDER BY stage_idx), 2) AS overall_conversion_pct
            FROM funnel_stages
        )
        SELECT * FROM funnel_metrics ORDER BY stage_idx ASC;
        """
        return self.con.execute(sql).df(), sql

    def get_top_products_ranking(self, top_n=10, category=None):
        """Priority 3: Top products (SQL aggregation & ranking)."""
        where_clause = f"WHERE category = '{category}'" if category and category != 'All' else ""
        sql = f"""
        WITH product_stats AS (
            SELECT 
                itemid,
                item_name,
                category,
                brand,
                AVG(price) AS unit_price,
                ANY_VALUE(image_url) AS image_url,
                ANY_VALUE(tag) AS tag,
                ANY_VALUE(tag_color) AS tag_color,
                ANY_VALUE(rating) AS rating,
                ANY_VALUE(reviews_count) AS reviews_count,
                ANY_VALUE(vibe) AS vibe,
                COUNT(CASE WHEN event = 'view' THEN 1 END) AS views,
                COUNT(CASE WHEN event = 'addtocart' THEN 1 END) AS carts,
                COUNT(CASE WHEN event = 'transaction' THEN 1 END) AS purchases,
                SUM(CASE WHEN event = 'transaction' THEN price ELSE 0 END) AS total_revenue
            FROM events
            {where_clause}
            GROUP BY itemid, item_name, category, brand
        ),
        ranked_products AS (
            SELECT 
                *,
                ROUND(carts * 100.0 / NULLIF(views, 0), 2) AS cart_rate_pct,
                ROUND(purchases * 100.0 / NULLIF(views, 0), 2) AS conversion_rate_pct,
                DENSE_RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank,
                DENSE_RANK() OVER (ORDER BY purchases DESC) AS purchase_rank
            FROM product_stats
        )
        SELECT * FROM ranked_products ORDER BY revenue_rank ASC LIMIT {top_n};
        """
        return self.con.execute(sql).df(), sql

    def get_product_engagement_metrics(self):
        """Priority 4: Product engagement scatter plot metrics (Analytical thinking)."""
        sql = """
        SELECT 
            itemid,
            item_name,
            category,
            brand,
            AVG(price) AS price,
            ANY_VALUE(image_url) AS image_url,
            ANY_VALUE(tag) AS tag,
            ANY_VALUE(rating) AS rating,
            COUNT(CASE WHEN event = 'view' THEN 1 END) AS views,
            COUNT(CASE WHEN event = 'addtocart' THEN 1 END) AS carts,
            COUNT(CASE WHEN event = 'transaction' THEN 1 END) AS purchases,
            SUM(CASE WHEN event = 'transaction' THEN price ELSE 0 END) AS revenue,
            ROUND(COUNT(CASE WHEN event = 'transaction' THEN 1 END) * 100.0 / NULLIF(COUNT(CASE WHEN event = 'view' THEN 1 END), 0), 2) AS view_to_purchase_cvr_pct,
            ROUND(COUNT(CASE WHEN event = 'addtocart' THEN 1 END) * 100.0 / NULLIF(COUNT(CASE WHEN event = 'view' THEN 1 END), 0), 2) AS cart_addition_rate_pct
        FROM events
        GROUP BY itemid, item_name, category, brand
        HAVING views > 0
        ORDER BY views DESC;
        """
        return self.con.execute(sql).df(), sql

    def get_product_cooccurrence_matrix(self, top_n_items=12):
        """Priority 7: Product co-occurrence heatmap (Recommendation systems / Basket analysis)."""
        sql = f"""
        WITH top_items AS (
            SELECT itemid, item_name, COUNT(*) as total_events
            FROM events
            GROUP BY itemid, item_name
            ORDER BY total_events DESC
            LIMIT {top_n_items}
        ),
        user_item_interactions AS (
            SELECT DISTINCT visitorid, itemid
            FROM events
            WHERE itemid IN (SELECT itemid FROM top_items)
        ),
        cooccurrence AS (
            SELECT 
                t1.item_name AS item_a,
                t2.item_name AS item_b,
                COUNT(DISTINCT u1.visitorid) AS cooccurrences
            FROM user_item_interactions u1
            JOIN user_item_interactions u2 ON u1.visitorid = u2.visitorid
            JOIN top_items t1 ON u1.itemid = t1.itemid
            JOIN top_items t2 ON u2.itemid = t2.itemid
            GROUP BY t1.item_name, t2.item_name
        )
        SELECT * FROM cooccurrence ORDER BY item_a, item_b;
        """
        return self.con.execute(sql).df(), sql

    def get_top_recommended_bundles(self, top_n=6):
        """Fetches top co-occurring product pairs for visual Pinterest bundle recommendations."""
        sql = f"""
        WITH user_item_pairs AS (
            SELECT DISTINCT e1.visitorid, e1.itemid AS item_a_id, e2.itemid AS item_b_id
            FROM events e1
            JOIN events e2 ON e1.visitorid = e2.visitorid AND e1.itemid < e2.itemid
            WHERE e1.event IN ('addtocart', 'transaction') AND e2.event IN ('addtocart', 'transaction')
        ),
        pair_counts AS (
            SELECT 
                item_a_id, 
                item_b_id, 
                COUNT(DISTINCT visitorid) AS cooccurrences
            FROM user_item_pairs
            GROUP BY item_a_id, item_b_id
            ORDER BY cooccurrences DESC
            LIMIT {top_n}
        )
        SELECT 
            p.cooccurrences,
            e1.item_name AS item_a_name,
            e1.category AS item_a_category,
            e1.brand AS item_a_brand,
            AVG(e1.price) AS item_a_price,
            ANY_VALUE(e1.image_url) AS item_a_image,
            ANY_VALUE(e1.tag) AS item_a_tag,
            
            e2.item_name AS item_b_name,
            e2.category AS item_b_category,
            e2.brand AS item_b_brand,
            AVG(e2.price) AS item_b_price,
            ANY_VALUE(e2.image_url) AS item_b_image,
            ANY_VALUE(e2.tag) AS item_b_tag
        FROM pair_counts p
        JOIN events e1 ON p.item_a_id = e1.itemid
        JOIN events e2 ON p.item_b_id = e2.itemid
        GROUP BY p.cooccurrences, e1.item_name, e1.category, e1.brand, e2.item_name, e2.category, e2.brand
        ORDER BY p.cooccurrences DESC;
        """
        return self.con.execute(sql).df(), sql

    def get_weekly_cohort_retention(self):
        """Calculates week-by-week user cohort retention decay matrix."""
        sql = """
        WITH user_first_week AS (
            SELECT 
                visitorid,
                MIN(date_trunc('week', strptime(date, '%Y-%m-%d'))) AS cohort_week
            FROM events
            GROUP BY visitorid
        ),
        activity AS (
            SELECT 
                e.visitorid,
                u.cohort_week,
                date_trunc('week', strptime(e.date, '%Y-%m-%d')) AS activity_week,
                DATE_DIFF('week', u.cohort_week, date_trunc('week', strptime(e.date, '%Y-%m-%d'))) AS week_offset
            FROM events e
            JOIN user_first_week u ON e.visitorid = u.visitorid
        ),
        cohort_counts AS (
            SELECT 
                strftime(cohort_week, '%Y-%m-%d') AS cohort_week,
                week_offset,
                COUNT(DISTINCT visitorid) AS active_users
            FROM activity
            GROUP BY cohort_week, week_offset
        ),
        cohort_sizes AS (
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
        """
        return self.con.execute(sql).df(), sql

    def get_rfm_customer_segments(self):
        """Calculates RFM (Recency, Frequency, Monetary) quartiles and customer segments."""
        sql = """
        WITH customer_rfm_raw AS (
            SELECT 
                visitorid,
                DATE_DIFF('day', MAX(strptime(date, '%Y-%m-%d')), (SELECT MAX(strptime(date, '%Y-%m-%d')) + INTERVAL 1 DAY FROM events)) AS recency_days,
                COUNT(CASE WHEN event = 'transaction' THEN 1 END) AS order_frequency,
                COUNT(CASE WHEN event = 'view' THEN 1 END) AS total_views,
                COUNT(CASE WHEN event = 'addtocart' THEN 1 END) AS total_carts,
                COALESCE(SUM(CASE WHEN event = 'transaction' THEN price ELSE 0 END), 0) AS total_spend
            FROM events
            GROUP BY visitorid
        ),
        scored AS (
            SELECT 
                *,
                NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
                NTILE(5) OVER (ORDER BY order_frequency ASC) AS f_score,
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
        """
        return self.con.execute(sql).df(), sql

    def get_category_performance_summary(self):
        """Category-level revenue, unit sales, views, conversion rate, and wallet share."""
        sql = """
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
        """
        return self.con.execute(sql).df(), sql

    def export_tableau_ready_datasets(self, output_dir="data"):
        """Exports clean, star-schema CSV datasets specifically for Tableau & Power BI."""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Sales Orders Dataset (Order line level)
        orders_sql = """
        SELECT 
            e.transactionid,
            e.date,
            e.visitorid,
            e.itemid,
            e.item_name,
            e.category,
            e.brand,
            e.price AS unit_price,
            e.price AS line_revenue
        FROM events e
        WHERE e.event = 'transaction'
        ORDER BY e.date ASC, e.transactionid ASC;
        """
        df_orders = self.con.execute(orders_sql).df()
        orders_path = os.path.join(output_dir, "tableau_sales_orders.csv")
        df_orders.to_csv(orders_path, index=False)

        # 2. Customer RFM Dataset
        df_rfm, _ = self.get_rfm_customer_segments()
        rfm_path = os.path.join(output_dir, "tableau_customer_rfm.csv")
        df_rfm.to_csv(rfm_path, index=False)

        # 3. Cohort Retention Dataset
        df_cohort, _ = self.get_weekly_cohort_retention()
        cohort_path = os.path.join(output_dir, "tableau_cohort_retention.csv")
        df_cohort.to_csv(cohort_path, index=False)

        # 4. Funnel Daily Dataset
        df_funnel, _ = self.get_daily_event_trends()
        funnel_path = os.path.join(output_dir, "tableau_funnel_daily.csv")
        df_funnel.to_csv(funnel_path, index=False)

        return {
            "orders": orders_path,
            "rfm": rfm_path,
            "cohort": cohort_path,
            "funnel": funnel_path
        }

if __name__ == "__main__":
    engine = BeautyDuckDBEngine()
    df_trends, _ = engine.get_daily_event_trends()
    print("Trends sample:\n", df_trends.head())
    df_funnel, _ = engine.get_conversion_funnel()
    print("\nFunnel:\n", df_funnel[['stage_name', 'event_count', 'step_conversion_pct', 'overall_conversion_pct']])
    paths = engine.export_tableau_ready_datasets()
    print("\nTableau datasets exported:\n", paths)
