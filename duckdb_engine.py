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

if __name__ == "__main__":
    engine = BeautyDuckDBEngine()
    df_trends, _ = engine.get_daily_event_trends()
    print("Trends sample:\n", df_trends.head())
    df_funnel, _ = engine.get_conversion_funnel()
    print("\nFunnel:\n", df_funnel[['stage_name', 'event_count', 'step_conversion_pct', 'overall_conversion_pct']])
