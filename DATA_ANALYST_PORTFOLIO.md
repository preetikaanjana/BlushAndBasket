# 📊 Blush & Basket · Data Analyst Portfolio & Interview Pack

This comprehensive guide is designed to help you leverage the **Blush & Basket** project to land **Data Analyst**, **Business Intelligence (BI) Analyst**, or **Product Analyst** roles.

---

## 📄 1. Resume Project Bullets (Google XYZ Format)

Copy-paste these bullet points directly into the **Projects** section of your resume:

### Option A: Balanced Data Analyst (SQL + Tableau + Python)
> **Blush & Basket — E-Commerce Analytics & Business Intelligence Suite** | *SQL, Tableau, Python, DuckDB*
> - Engineered an end-to-end commercial analytics pipeline processing **75,000+ clickstream interaction events** across 4,500 unique shoppers and 29 catalog products using **DuckDB SQL** and **Python**.
> - Built a **Weekly Cohort Retention Matrix** and **Customer Conversion Funnel** using advanced SQL window functions (`LAG`, `FIRST_VALUE`), diagnosing an **84% drop-off** at the view-to-bag stage while identifying a **45% downstream checkout conversion**.
> - Implemented an **RFM (Recency, Frequency, Monetary) segmentation model** and market-basket bundling algorithm, identifying prime cross-sell routines that boosted simulated Average Order Value (AOV) by **15%**.
> - Designed interactive **Tableau/Power BI dashboards** with Level of Detail (`{FIXED}`) LOD calculations and CSV data pipelines to visualize customer lifetime value and product opportunity matrices.

### Option B: Tableau & BI Focused
> **Blush & Basket — Commercial BI & Customer Retention Dashboard** | *Tableau, SQL, Streamlit*
> - Architected a multi-dimensional retail BI dashboard analyzing **₹4.38M in gross revenue** across 4,400+ transactions with 60-day historical time-series aggregation.
> - Developed Tableau-ready star-schema data extracts and Level of Detail (LOD) expressions (`{FIXED [Visitor ID]: MIN([Order Date])}`) to model week-over-week cohort retention decay and customer repurchase intervals.
> - Designed an **Engagement Quad-Matrix** balancing browsing traffic against conversion rates to classify inventory into *Stars*, *Hidden Gems*, *Traffic Traps*, and *Laggards*, enabling strategic inventory repositioning.

---

## 🎙️ 2. The STAR Interview Framework

Use this structured story whenever an interviewer asks: *"Tell me about a data analytics project you worked on."*

### 📍 Situation
> *"In e-commerce marketplaces like Nykaa or Sephora, businesses capture huge volumes of browsing telemetry, but struggle to pinpoint where customer drop-offs happen, which products actually convert, and how to increase average order values. I built **Blush & Basket**, an end-to-end commercial intelligence platform that processes 75,000+ clickstream events to optimize conversion funnels and customer retention."*

### 🎯 Task
> *"My goal was threefold: First, build a high-performance analytical pipeline that could aggregate clickstream data in sub-milliseconds without heavy database infrastructure. Second, diagnose funnel drop-off points and categorize shoppers into actionable behavioral segments. Third, build a Tableau-ready reporting ecosystem with automated routine cross-sell bundles."*

### 🛠️ Action
> *"I used **DuckDB SQL** to perform vectorized in-memory analytics directly on Parquet files, writing complex queries with CTEs, window functions like `DENSE_RANK()`, `LAG()`, and `NTILE(5)` for RFM quartile scoring. I built an interactive **Weekly Cohort Retention Matrix** to evaluate customer decay over 8-week intervals and developed a **Market Basket co-occurrence matrix** to power 'Frequently Bought Together' bundles. Finally, I built a Pinterest-aesthetic interactive web app and exported pre-cleaned CSV data models with Tableau LOD formulas for BI reporting."*

### 🏆 Result
> *"The project revealed that while 84% of viewers dropped off before adding to cart, 45% of shoppers who added to cart went on to complete checkout—proving that checkout friction was low, but top-of-funnel consideration needed stronger visual proof and bundling. The automated bundling algorithm unlocked high-affinity routine pairs saving customers 15% while increasing the store's Average Order Value."*

---

## 💡 3. Top 5 Technical Interview Q&A (Based on This Project)

### Q1: "How did you calculate the Cohort Retention Matrix in SQL?"
**Your Answer:**
> *"I used a multi-step CTE in SQL: First, I found each user's initial acquisition week using `MIN(date_trunc('week', order_date)) GROUP BY visitorid`. Second, I joined that back to all user activity events and calculated the week offset using `DATE_DIFF('week', cohort_week, activity_week)`. Third, I counted distinct users per cohort week and offset, partitioned by cohort week with `FIRST_VALUE()` to get the Week 0 baseline size, and divided to compute the retention percentage."*

### Q2: "What is an LOD Expression in Tableau and where did you use it?"
**Your Answer:**
> *"Level of Detail (LOD) expressions allow you to compute values at the data source level without depending on the visualization's dimensional granularity. In Blush & Basket, I used Fixed LODs like `{FIXED [Visitor ID]: MIN([Order Date])}` to anchor the customer's acquisition date, and `{FIXED [Visitor ID]: COUNTD([Transaction ID])}` to classify shoppers as first-time vs. repeat buyers regardless of the date filters applied on the sheet."*

### Q3: "How does your RFM Segmentation model work?"
**Your Answer:**
> *"RFM stands for Recency, Frequency, and Monetary value. I aggregated each customer's days since last visit, total completed orders, and gross spend. Then, using SQL `NTILE(5)`, I scored each customer from 1 to 5 across all three dimensions. Combining these scores allowed me to identify 6 distinct commercial segments—such as 'Champions' (high R, high F, high M) and 'At-Risk High Value' (high spenders who haven't visited recently) to drive targeted CRM campaigns."*

### Q4: "Why use DuckDB instead of standard Pandas or PostgreSQL?"
**Your Answer:**
> *"Pandas executes row-oriented Python bytecode in memory, which slows down on complex window functions across large clickstream datasets, while PostgreSQL requires running a separate database server. DuckDB provides vectorized columnar SQL execution directly against Parquet files in-process, running complex window queries and joins in under 15 milliseconds with zero operational overhead."*

### Q5: "What is the difference between Step Conversion Rate and Cumulative Conversion Rate in a funnel?"
**Your Answer:**
> *"Cumulative conversion rate measures the percentage of users at any given stage relative to the top of the funnel (e.g. Purchases / Initial Views). Step conversion rate uses the SQL `LAG()` window function to measure conversion relative to the immediately preceding step (e.g. Purchases / Added to Bag). This distinction is vital because cumulative conversion only tells you the overall conversion, but step conversion pinpoints the exact transition stage where leakage is worst."*

---

## 📱 4. LinkedIn Project Announcement Template

> 💄 Excited to share my latest Data Analytics & Business Intelligence project: **Blush & Basket**!
>
> Inspired by top beauty retailers like Nykaa and Sephora, I built an end-to-end commercial analytics suite analyzing 75,000+ clickstream events to answer key e-commerce questions:
>
> 🔹 **Customer Journey Analytics:** Analyzed full-funnel drop-offs using SQL window functions (`LAG`, `FIRST_VALUE`).
> 🔹 **Weekly Cohort Retention:** Modeled customer decay curves over 8-week intervals to track repeat replenishment.
> 🔹 **RFM Customer Segmentation:** Classified 4,500 shoppers into 6 actionable commercial segments using `NTILE(5)` scoring.
> 🔹 **Market Basket Recommendations:** Computed cross-product affinities to power 1-click routine bundles.
> 🔹 **Tableau & BI Integration:** Built star-schema CSV exports with custom Level of Detail (`{FIXED}`) LOD calculations.
>
> 🛠️ Tech Stack: DuckDB SQL | Python | Tableau | Scikit-Learn | Streamlit | Plotly
>
> 🔗 Live Project & Code: [Link to GitHub / Demo]
>
> #DataAnalytics #Tableau #SQL #BusinessIntelligence #Python #ProductAnalytics #DataScience
