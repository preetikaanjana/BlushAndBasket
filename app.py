"""
Beauty Commerce Analytics & Recommendation Suite (Pinterest Aesthetic Edition)
Nykaa-Inspired Context · High-End Beauty Moodboard · Consumer-Focused
Built with DuckDB SQL, Scikit-Learn (Unsupervised & Supervised ML), and Streamlit.
"""

import os
import sys
from pathlib import Path
import joblib
import duckdb
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Ensure project root is in sys.path for robust imports across deployment environments
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from duckdb_engine import BeautyDuckDBEngine
from product_images import PRODUCT_METADATA, DEFAULT_METADATA, get_product_metadata

# ---------------------------------------------------------
# Page Setup
# ---------------------------------------------------------
st.set_page_config(
    page_title="Blush & Basket · Beauty E-Commerce Intelligence",
    page_icon="💄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Pinterest Aesthetic CSS Design System
# Color Palette:
# Plum:       #241126
# Deep Berry: #A01B56
# Berry Rose: #C0266D
# Rosy Pink:  #E879A8
# Pastel Lilac:#E9D5FF
# Ivory Blush:#FFF8FA
# Card Glass: rgba(255, 255, 255, 0.95)
# ---------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    /* Global Base */
    .stApp {
        background: linear-gradient(180deg, #FFF8FA 0%, #FAF2F6 100%);
        color: #241126;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        color: #241126 !important;
        font-family: 'Playfair Display', Georgia, serif !important;
        font-weight: 700 !important;
        letter-spacing: -0.5px;
    }
    
    p, span, div, label {
        color: #241126;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Hero Moodboard Header */
    .pinterest-hero {
        background: linear-gradient(135deg, #FFFFFF 0%, #FFF5F9 50%, #FDF2F8 100%);
        border: 1px solid #F3D5E5;
        border-radius: 20px;
        padding: 28px 32px;
        box-shadow: 0 10px 30px rgba(192, 38, 109, 0.05);
        margin-bottom: 24px;
        position: relative;
        overflow: hidden;
    }
    .pinterest-badge {
        display: inline-block;
        background: linear-gradient(135deg, #C0266D 0%, #D84374 100%);
        color: #FFFFFF !important;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        padding: 5px 14px;
        border-radius: 30px;
        margin-bottom: 12px;
        box-shadow: 0 4px 12px rgba(192, 38, 109, 0.25);
    }
    .hero-title {
        font-size: 34px !important;
        line-height: 1.2;
        color: #241126 !important;
        margin-bottom: 8px;
    }
    .hero-subtitle {
        font-size: 16px;
        color: #6E4968;
        max-width: 850px;
        line-height: 1.5;
        margin-bottom: 0;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #241126 !important;
        border-right: 1px solid #3F1D43;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span {
        color: #FFF8FA;
    }
    section[data-testid="stSidebar"] hr {
        border-color: #4A234D !important;
    }
    section[data-testid="stSidebar"] label {
        font-size: 14px !important;
        font-weight: 600 !important;
        color: #F9A8D4 !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    /* Selectbox in sidebar */
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #FFFFFF !important;
        border: 1px solid #E9D5FF !important;
        border-radius: 12px !important;
        color: #241126 !important;
    }
    section[data-testid="stSidebar"] div[data-baseweb="select"] * {
        color: #241126 !important;
        font-weight: 600 !important;
    }

    /* Executive KPI Cards */
    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #F3D5E5;
        border-radius: 16px;
        padding: 18px 20px;
        box-shadow: 0 6px 20px rgba(36, 17, 38, 0.04);
        transition: all 0.25s ease-in-out;
        position: relative;
        overflow: hidden;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 28px rgba(192, 38, 109, 0.08);
        border-color: #E879A8;
    }
    .kpi-label {
        font-size: 12px;
        font-weight: 700;
        color: #8C4773;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 4px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 800;
        color: #241126;
        line-height: 1.15;
        font-feature-settings: "tnum";
    }
    .kpi-subtext {
        font-size: 13px;
        color: #6E4968;
        margin-top: 4px;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    /* Pinterest Pin Card */
    .pin-card {
        background: #FFFFFF;
        border-radius: 18px;
        border: 1px solid #F3D5E5;
        overflow: hidden;
        box-shadow: 0 8px 24px rgba(36, 17, 38, 0.05);
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        margin-bottom: 24px;
    }
    .pin-card:hover {
        transform: translateY(-6px);
        box-shadow: 0 18px 36px rgba(192, 38, 109, 0.12);
        border-color: #E879A8;
    }
    .pin-image-wrapper {
        position: relative;
        width: 100%;
        padding-top: 100%; /* 1:1 Aspect ratio */
        background: #FDF2F8;
        overflow: hidden;
    }
    .pin-image {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.4s ease;
    }
    .pin-card:hover .pin-image {
        transform: scale(1.04);
    }
    .pin-tag {
        position: absolute;
        top: 12px;
        left: 12px;
        background: rgba(255, 255, 255, 0.92);
        backdrop-filter: blur(8px);
        color: #C0266D;
        font-size: 11px;
        font-weight: 700;
        padding: 4px 10px;
        border-radius: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08);
        letter-spacing: 0.3px;
    }
    .pin-rating {
        position: absolute;
        bottom: 12px;
        right: 12px;
        background: rgba(36, 17, 38, 0.85);
        backdrop-filter: blur(8px);
        color: #FFF8FA;
        font-size: 11px;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 12px;
    }
    .pin-body {
        padding: 16px 18px;
        display: flex;
        flex-direction: column;
        flex-grow: 1;
    }
    .pin-brand {
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        color: #A01B56;
        letter-spacing: 1.2px;
        margin-bottom: 4px;
    }
    .pin-title {
        font-family: 'Playfair Display', serif !important;
        font-size: 16px !important;
        font-weight: 700 !important;
        color: #241126 !important;
        line-height: 1.3;
        margin-bottom: 6px;
        min-height: 42px;
    }
    .pin-vibe {
        font-size: 12px;
        color: #715575;
        margin-bottom: 12px;
        font-style: italic;
    }
    .pin-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-top: 1px dashed #F3D5E5;
        padding-top: 10px;
        margin-top: auto;
    }
    .pin-price {
        font-size: 18px;
        font-weight: 800;
        color: #241126;
    }
    .pin-cvr {
        font-size: 12px;
        font-weight: 700;
        color: #C0266D;
        background: #FFF0F5;
        padding: 3px 8px;
        border-radius: 8px;
    }

    /* Bundle Box */
    .bundle-card {
        background: #FFFFFF;
        border: 1px solid #F3D5E5;
        border-radius: 20px;
        padding: 24px;
        box-shadow: 0 10px 30px rgba(36, 17, 38, 0.05);
        margin-bottom: 24px;
        transition: all 0.25s ease;
    }
    .bundle-card:hover {
        border-color: #C0266D;
        box-shadow: 0 14px 34px rgba(192, 38, 109, 0.09);
    }

    /* Tabs Styling */
    button[data-baseweb="tab"] {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 15px !important;
        font-weight: 600 !important;
        color: #715575 !important;
        padding: 10px 20px !important;
        border-radius: 8px 8px 0 0 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: #C0266D !important;
        font-weight: 700 !important;
        border-bottom: 3px solid #C0266D !important;
    }

    /* Button Styling */
    .stButton>button {
        background: linear-gradient(135deg, #C0266D 0%, #9B3264 100%) !important;
        color: #FFFFFF !important;
        font-weight: 600 !important;
        font-size: 15px !important;
        border-radius: 12px !important;
        border: none !important;
        padding: 10px 22px !important;
        box-shadow: 0 4px 14px rgba(192, 38, 109, 0.25) !important;
        transition: all 0.2s ease !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 18px rgba(192, 38, 109, 0.35) !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Load Resources & Self-Healing Cold Starts
# ---------------------------------------------------------
@st.cache_resource
def load_all_resources():
    events_path = BASE_DIR / "data" / "beauty_events.parquet"
    products_path = BASE_DIR / "data" / "beauty_products.parquet"
    bundle_path = BASE_DIR / "models" / "beauty_ml_bundle.joblib"

    if not events_path.exists() or not products_path.exists():
        from data_generator import generate_beauty_ecommerce_data
        generate_beauty_ecommerce_data()

    if not bundle_path.exists():
        from ml_models import train_customer_segmentation_and_purchase_model
        train_customer_segmentation_and_purchase_model(str(events_path), str(BASE_DIR / "models"))

    engine = BeautyDuckDBEngine(str(events_path))
    ml_bundle = joblib.load(str(bundle_path)) if bundle_path.exists() else None
    df_events = pd.read_parquet(str(events_path))
    df_products = pd.read_parquet(str(products_path))
    return engine, ml_bundle, df_events, df_products

engine, ml_bundle, df_events, df_products = load_all_resources()

# ---------------------------------------------------------
# Sidebar Filter & Moodboard Navigation
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 10px 0 16px 0;">
        <span style="font-size: 34px;">💄</span>
        <h2 style="font-family:'Playfair Display', serif; font-size: 24px; color: #FFF8FA; margin: 4px 0 2px 0;">Blush & Basket</h2>
        <p style="font-size: 13px; color: #F9A8D4; margin: 0; letter-spacing: 0.5px;">Beauty E-Commerce Intelligence</p>
    </div>
    """, unsafe_allow_html=True)
    st.divider()

    st.markdown("<p style='font-weight: 700; color: #FFF8FA; font-size: 14px;'>CURATE BY CATEGORY</p>", unsafe_allow_html=True)
    categories = ['All'] + sorted(df_products['category'].unique().tolist())
    selected_category = st.selectbox("Category Filter", categories, index=0)

    st.markdown("<p style='font-weight: 700; color: #FFF8FA; font-size: 14px; margin-top: 16px;'>QUICK SEARCH</p>", unsafe_allow_html=True)
    search_query = st.text_input("Search catalog or brand", placeholder="e.g. Minimalist, Ruby Woo...")

    st.divider()
    st.markdown("""
    <div style="background: rgba(255,255,255,0.06); border: 1px solid rgba(233,213,255,0.15); border-radius: 12px; padding: 14px;">
        <p style="font-size: 12px; color: #F9A8D4; font-weight: 700; margin-bottom: 4px; text-transform: uppercase;">Store Highlights</p>
        <p style="font-size: 13px; color: #FFF8FA; margin-bottom: 2px;">• <strong>75,000+</strong> Real Interactions</p>
        <p style="font-size: 13px; color: #FFF8FA; margin-bottom: 2px;">• <strong>4,500</strong> Active Shoppers</p>
        <p style="font-size: 13px; color: #FFF8FA; margin-bottom: 2px;">• <strong>29</strong> Curated Products</p>
        <p style="font-size: 13px; color: #FFF8FA; margin-bottom: 0;">• <strong>4</strong> Shopper Segments</p>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# Hero Moodboard Header
# ---------------------------------------------------------
st.markdown("""
<div class="pinterest-hero">
    <div class="pinterest-badge">✨ BLUSH & BASKET · COMMERCIAL INTELLIGENCE</div>
    <div class="hero-title">Blush & Basket · Beauty E-Commerce Intelligence</div>
    <div class="hero-subtitle">
        An aesthetic commercial intelligence platform tracking customer journeys, product engagement, 
        shopper segmentation, purchase propensity predictions, and automated routine bundles.
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Dynamic Aggregations & Filter Handling
# ---------------------------------------------------------
filtered_events = df_events.copy()
if selected_category != 'All':
    filtered_events = filtered_events[filtered_events['category'] == selected_category]

if search_query.strip():
    q = search_query.lower()
    filtered_events = filtered_events[
        filtered_events['item_name'].str.lower().str.contains(q) |
        filtered_events['brand'].str.lower().str.contains(q)
    ]

total_events = len(filtered_events)
views_count = len(filtered_events[filtered_events['event'] == 'view'])
carts_count = len(filtered_events[filtered_events['event'] == 'addtocart'])
tx_count = len(filtered_events[filtered_events['event'] == 'transaction'])
cvr_rate = (tx_count * 100.0 / views_count) if views_count > 0 else 0
cart_rate = (carts_count * 100.0 / views_count) if views_count > 0 else 0
total_revenue = filtered_events[filtered_events['event'] == 'transaction']['price'].sum()
aov = (total_revenue / max(1, tx_count))

# ---------------------------------------------------------
# Executive KPI Row
# ---------------------------------------------------------
k1, k2, k3, k4, k5 = st.columns(5)

with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Interactions</div>
        <div class="kpi-value">{total_events:,}</div>
        <div class="kpi-subtext">⚡ Clickstream events</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Catalog Views</div>
        <div class="kpi-value">{views_count:,}</div>
        <div class="kpi-subtext">👀 Browsing volume</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Added to Bag</div>
        <div class="kpi-value">{carts_count:,}</div>
        <div class="kpi-subtext">🛍️ {cart_rate:.1f}% cart rate</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Completed Orders</div>
        <div class="kpi-value" style="color: #C0266D;">{tx_count:,}</div>
        <div class="kpi-subtext">🎯 {cvr_rate:.2f}% conversion rate</div>
    </div>
    """, unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">Gross Revenue (GMV)</div>
        <div class="kpi-value" style="color: #C0266D;">₹{total_revenue:,.0f}</div>
        <div class="kpi-subtext">🏷️ Avg Order: ₹{aov:.0f}</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# ---------------------------------------------------------
# Pinterest-Themed Feature Tabs
# ---------------------------------------------------------
(
    tab_moodboard,
    tab_bundles,
    tab_trends,
    tab_funnel,
    tab_products,
    tab_scatter,
    tab_segmentation,
    tab_supervised,
    tab_cooccurrence,
    tab_guide
) = st.tabs([
    "📌 Visual Catalog",
    "✨ Routine Bundles",
    "📈 Daily Trends",
    "🎯 Conversion Funnel",
    "🏆 Product Leaderboard",
    "🔍 Opportunity Matrix",
    "👥 Customer Personas",
    "🤖 Purchase Predictions",
    "🔥 Co-Occurrence Affinity",
    "📖 About Blush & Basket"
])

# =========================================================
# TAB: PINTEREST MOODBOARD & VISUAL CATALOG
# =========================================================
with tab_moodboard:
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h3 style="font-size: 26px; margin-bottom: 4px;">Pinterest Catalog Moodboard</h3>
        <p style="font-size: 15px; color: #6E4968;">
            Curated high-resolution beauty product visuals with authentic e-commerce performance metrics, ratings, and aesthetics.
        </p>
    </div>
    """, unsafe_allow_html=True)

    catalog_df = df_products.copy()
    if selected_category != 'All':
        catalog_df = catalog_df[catalog_df['category'] == selected_category]
    if search_query.strip():
        q = search_query.lower()
        catalog_df = catalog_df[
            catalog_df['item_name'].str.lower().str.contains(q) |
            catalog_df['brand'].str.lower().str.contains(q)
        ]

    # Calculate real-time conversion rates per product from events
    prod_metrics = df_events.groupby('itemid').agg(
        views=('event', lambda e: (e == 'view').sum()),
        carts=('event', lambda e: (e == 'addtocart').sum()),
        purchases=('event', lambda e: (e == 'transaction').sum())
    ).reset_index()
    prod_metrics['cvr'] = (prod_metrics['purchases'] * 100.0 / prod_metrics['views'].replace(0, 1)).round(1)

    catalog_df = catalog_df.merge(prod_metrics, on='itemid', how='left').fillna(0)

    # 4-Column Pinterest Masonry Grid
    cols = st.columns(4)
    for idx, (_, row) in enumerate(catalog_df.iterrows()):
        col = cols[idx % 4]
        with col:
            img_url = row.get('image_url') or DEFAULT_METADATA['image_url']
            tag = row.get('tag', 'Bestseller')
            rating = row.get('rating', 4.8)
            reviews = row.get('reviews_count', 1200)
            vibe = row.get('vibe', 'Clean beauty formula')
            cvr_val = row.get('cvr', 6.2)

            st.markdown(f"""
            <div class="pin-card">
                <div class="pin-image-wrapper">
                    <img src="{img_url}" alt="{row['item_name']}" class="pin-image" loading="lazy" />
                    <div class="pin-tag">{tag}</div>
                    <div class="pin-rating">★ {rating} ({reviews:,})</div>
                </div>
                <div class="pin-body">
                    <div class="pin-brand">{row['brand']}</div>
                    <div class="pin-title">{row['item_name']}</div>
                    <div class="pin-vibe">"{vibe}"</div>
                    <div class="pin-footer">
                        <div class="pin-price">₹{row['price']:,.0f}</div>
                        <div class="pin-cvr">CVR: {cvr_val:.1f}%</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# =========================================================
# TAB: FREQUENTLY BOUGHT TOGETHER BUNDLES
# =========================================================
with tab_bundles:
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h3 style="font-size: 26px; margin-bottom: 4px;">Frequently Bought Together (Curated Bundles)</h3>
        <p style="font-size: 15px; color: #6E4968;">
            Algorithmic product co-occurrence affinity powering high-converting cross-sell and routine bundles.
        </p>
    </div>
    """, unsafe_allow_html=True)

    bundles_df, _ = engine.get_top_recommended_bundles(top_n=4)

    for _, row in bundles_df.iterrows():
        item_a_price = float(row['item_a_price'])
        item_b_price = float(row['item_b_price'])
        total_bundle_price = item_a_price + item_b_price
        discounted_bundle_price = total_bundle_price * 0.85
        savings = total_bundle_price - discounted_bundle_price

        st.markdown(f"""
        <div class="bundle-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
                <div>
                    <span style="background: #FFF0F5; color: #C0266D; font-weight: 700; font-size: 12px; padding: 4px 12px; border-radius: 20px; border: 1px solid #F3D5E5;">
                        HIGH AFFINITY BUNDLE · {row['cooccurrences']} Shoppers Co-Purchased
                    </span>
                </div>
                <div>
                    <span style="background: #E8F5E9; color: #2E7D32; font-weight: 700; font-size: 12px; padding: 4px 12px; border-radius: 20px;">
                        Save ₹{savings:,.0f} (15% OFF)
                    </span>
                </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr auto 1fr auto 1.2fr; gap: 20px; align-items: center;">
                <!-- Product 1 -->
                <div style="display: flex; gap: 14px; align-items: center;">
                    <img src="{row['item_a_image']}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 14px; border: 1px solid #F3D5E5;" />
                    <div>
                        <div style="font-size: 11px; text-transform: uppercase; color: #A01B56; font-weight: 700;">{row['item_a_brand']}</div>
                        <div style="font-weight: 700; font-size: 15px; color: #241126;">{row['item_a_name']}</div>
                        <div style="font-size: 14px; font-weight: 800; color: #C0266D;">₹{item_a_price:,.0f}</div>
                    </div>
                </div>
                <!-- Plus Symbol -->
                <div style="font-size: 26px; font-weight: 700; color: #C0266D; text-align: center;">+</div>
                <!-- Product 2 -->
                <div style="display: flex; gap: 14px; align-items: center;">
                    <img src="{row['item_b_image']}" style="width: 80px; height: 80px; object-fit: cover; border-radius: 14px; border: 1px solid #F3D5E5;" />
                    <div>
                        <div style="font-size: 11px; text-transform: uppercase; color: #A01B56; font-weight: 700;">{row['item_b_brand']}</div>
                        <div style="font-weight: 700; font-size: 15px; color: #241126;">{row['item_b_name']}</div>
                        <div style="font-size: 14px; font-weight: 800; color: #C0266D;">₹{item_b_price:,.0f}</div>
                    </div>
                </div>
                <!-- Equals Symbol -->
                <div style="font-size: 26px; font-weight: 700; color: #6E4968; text-align: center;">=</div>
                <!-- Bundle Pricing -->
                <div style="background: #FFF8FA; border: 1px solid #F3D5E5; border-radius: 14px; padding: 14px 18px; text-align: right;">
                    <div style="font-size: 12px; color: #715575; text-decoration: line-through;">Total: ₹{total_bundle_price:,.0f}</div>
                    <div style="font-size: 22px; font-weight: 800; color: #C0266D;">Bundle: ₹{discounted_bundle_price:,.0f}</div>
                    <div style="font-size: 12px; color: #2E7D32; font-weight: 600;">1-Click Routine Pairing</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# TAB: DAILY EVENT TREND
# =========================================================
with tab_trends:
    st.markdown("""
    <div style="margin-bottom: 16px;">
        <h3 style="font-size: 22px; margin-bottom: 2px;">Daily Customer Engagement Trends</h3>
        <p style="font-size: 14px; color: #6E4968;">Track daily catalog browsing, bag additions, and completed customer orders over time.</p>
    </div>
    """, unsafe_allow_html=True)

    df_daily, _ = engine.get_daily_event_trends(selected_category)

    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=df_daily['date'], y=df_daily['views'],
        name='Catalog Views',
        line=dict(color='#241126', width=2.5),
        mode='lines'
    ))
    fig_trend.add_trace(go.Scatter(
        x=df_daily['date'], y=df_daily['add_to_carts'],
        name='Added to Bag',
        line=dict(color='#C0266D', width=2.5),
        mode='lines'
    ))
    fig_trend.add_trace(go.Scatter(
        x=df_daily['date'], y=df_daily['transactions'],
        name='Completed Orders',
        line=dict(color='#E879A8', width=3),
        mode='lines'
    ))

    fig_trend.update_layout(
        height=380,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=13)),
        xaxis=dict(showgrid=True, gridcolor='#FFF8FA', title="Date"),
        yaxis=dict(showgrid=True, gridcolor='#FBEBF2', title="Daily Interactions")
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# =========================================================
# TAB: CONVERSION FUNNEL
# =========================================================
with tab_funnel:
    st.markdown("""
    <div style="margin-bottom: 16px;">
        <h3 style="font-size: 22px; margin-bottom: 2px;">Customer Conversion Funnel & Drop-Offs</h3>
        <p style="font-size: 14px; color: #6E4968;">Analyze shopper journey progression and drop-offs from catalog view to completed purchase.</p>
    </div>
    """, unsafe_allow_html=True)

    col_fn1, col_fn2 = st.columns([1.6, 1.2])
    df_funnel, _ = engine.get_conversion_funnel(selected_category)

    with col_fn1:
        fig_fn = go.Figure(go.Funnel(
            y=df_funnel['stage_name'],
            x=df_funnel['event_count'],
            textinfo="value+percent previous+percent initial",
            textfont=dict(size=14, color="#FFFFFF", family="Plus Jakarta Sans"),
            marker=dict(color=['#241126', '#C0266D', '#E879A8']),
            connector=dict(line=dict(color='#E9D5FF', width=2))
        ))
        fig_fn.update_layout(
            height=340,
            margin=dict(l=10, r=10, t=10, b=10),
            plot_bgcolor='#FFFFFF',
            paper_bgcolor='#FFFFFF'
        )
        st.plotly_chart(fig_fn, use_container_width=True)

    with col_fn2:
        st.markdown("<h4 style='font-size: 17px; margin-bottom: 8px;'>Stage-by-Stage Journey Audit</h4>", unsafe_allow_html=True)
        fn_display = df_funnel[['stage_name', 'event_count', 'step_conversion_pct', 'drop_off_count', 'overall_conversion_pct']].copy()
        fn_display.columns = ['Stage', 'Volume', 'Step CVR (%)', 'Drop-Offs', 'Cumulative CVR (%)']
        st.dataframe(fn_display, hide_index=True)

        st.markdown("""
        <div style="background-color:#FFFFFF; border:1px solid #F3D5E5; border-radius:12px; padding:16px; margin-top:12px;">
            <p style="font-size:14px; font-weight:700; color:#C0266D; margin-bottom:4px;">💡 Strategic Customer Journey Takeaway:</p>
            <p style="font-size:13px; color:#6E4968; margin-bottom:0; line-height:1.5;">
                The primary drop-off occurs between <strong>Views and Bag Additions</strong> (~84% attrition). 
                However, once an item is added to the bag, over <strong>45%</strong> transition into completed orders, highlighting high downstream checkout efficiency.
            </p>
        </div>
        """, unsafe_allow_html=True)

# =========================================================
# TAB: TOP PRODUCTS LEADERBOARD
# =========================================================
with tab_products:
    st.markdown("""
    <div style="margin-bottom: 16px;">
        <h3 style="font-size: 22px; margin-bottom: 2px;">Product Performance Leaderboard</h3>
        <p style="font-size: 14px; color: #6E4968;">Rank bestsellers by total gross revenue, order volume, and conversion percentage.</p>
    </div>
    """, unsafe_allow_html=True)

    df_top_prod, _ = engine.get_top_products_ranking(top_n=10, category=selected_category)

    # Visual Cards for Top 3 Bestsellers
    st.markdown("<h4 style='font-size: 18px; margin-bottom: 12px;'>🥇 Podium Bestsellers</h4>", unsafe_allow_html=True)
    podium_cols = st.columns(3)
    medals = ["🥇 1st Place", "🥈 2nd Place", "🥉 3rd Place"]

    for i in range(min(3, len(df_top_prod))):
        row = df_top_prod.iloc[i]
        with podium_cols[i]:
            st.markdown(f"""
            <div style="background:#FFFFFF; border:1px solid #F3D5E5; border-radius:16px; padding:16px; box-shadow:0 6px 18px rgba(36,17,38,0.05); display:flex; gap:14px; align-items:center;">
                <img src="{row['image_url']}" style="width:75px; height:75px; object-fit:cover; border-radius:12px; border:1px solid #F3D5E5;" />
                <div>
                    <span style="background:#FFF0F5; color:#C0266D; font-weight:700; font-size:11px; padding:3px 8px; border-radius:10px;">{medals[i]}</span>
                    <div style="font-weight:700; font-size:14px; color:#241126; margin-top:4px;">{row['item_name']}</div>
                    <div style="font-size:13px; color:#6E4968;">Revenue: <strong style="color:#C0266D;">₹{row['total_revenue']:,.0f}</strong> · CVR: {row['conversion_rate_pct']:.1f}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.write("")

    # Full Leaderboard Dataframe
    display_cols = ['revenue_rank', 'item_name', 'brand', 'category', 'unit_price', 'views', 'carts', 'purchases', 'total_revenue', 'conversion_rate_pct']
    top_table = df_top_prod[display_cols].copy()
    top_table.columns = ['Rank', 'Product Name', 'Brand', 'Category', 'Price (₹)', 'Views', 'Bag Adds', 'Orders', 'Revenue (₹)', 'CVR (%)']
    st.dataframe(top_table.style.format({'Price (₹)': '₹{:.0f}', 'Revenue (₹)': '₹{:,.0f}', 'CVR (%)': '{:.2f}%'}), hide_index=True)

# =========================================================
# TAB: ENGAGEMENT SCATTER PLOT
# =========================================================
with tab_scatter:
    st.markdown("""
    <div style="margin-bottom: 16px;">
        <h3 style="font-size: 22px; margin-bottom: 2px;">Product Opportunity Quad-Matrix</h3>
        <p style="font-size: 14px; color: #6E4968;">Balancing catalog traffic against conversion rate to identify strategic merchandising opportunities.</p>
    </div>
    """, unsafe_allow_html=True)

    df_eng, _ = engine.get_product_engagement_metrics()

    fig_scatter = px.scatter(
        df_eng,
        x='views',
        y='view_to_purchase_cvr_pct',
        size='revenue',
        color='category',
        text='item_name',
        labels={
            'views': 'Browsing Volume (Views)',
            'view_to_purchase_cvr_pct': 'Conversion Rate (%)',
            'revenue': 'Revenue (₹)'
        },
        color_discrete_sequence=['#C0266D', '#241126', '#E879A8', '#853A68', '#A855F7', '#EC4899']
    )
    fig_scatter.update_traces(textposition='top center', textfont=dict(size=11, family="Plus Jakarta Sans"))

    median_views = df_eng['views'].median()
    median_cvr = df_eng['view_to_purchase_cvr_pct'].median()
    fig_scatter.add_vline(x=median_views, line_dash="dash", line_color="#E9D5FF")
    fig_scatter.add_hline(y=median_cvr, line_dash="dash", line_color="#E9D5FF")

    fig_scatter.update_layout(
        height=480,
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor='#FFFFFF',
        paper_bgcolor='#FFFFFF',
        xaxis=dict(showgrid=True, gridcolor='#FBEBF2'),
        yaxis=dict(showgrid=True, gridcolor='#FBEBF2')
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    c_q1, c_q2, c_q3, c_q4 = st.columns(4)
    c_q1.info("⭐ **Top-Right (Stars)**: High Views + High CVR (Core revenue drivers)")
    c_q2.success("💎 **Top-Left (Hidden Gems)**: Lower Views + High CVR (Prime for homepage feature)")
    c_q3.warning("👀 **Bottom-Right (Traffic Traps)**: High Views + Low CVR (Audit pricing or imagery)")
    c_q4.error("💤 **Bottom-Left (Laggards)**: Low Views + Low CVR (Phase out or reposition)")

# =========================================================
# TAB: CUSTOMER SEGMENTATION
# =========================================================
with tab_segmentation:
    st.markdown("""
    <div style="margin-bottom: 16px;">
        <h3 style="font-size: 22px; margin-bottom: 2px;">Customer Personas & Segmentation</h3>
        <p style="font-size: 14px; color: #6E4968;">Behavioral grouping of 4,500 beauty shoppers based on browsing frequency, intent, and total spend.</p>
    </div>
    """, unsafe_allow_html=True)

    if ml_bundle:
        df_seg = ml_bundle['visitor_segments']
        col_s1, col_s2 = st.columns([1.7, 1.1])

        with col_s1:
            st.markdown("<h4 style='font-size: 17px;'>Customer Persona Clusters (2D Projection)</h4>", unsafe_allow_html=True)
            fig_cluster = px.scatter(
                df_seg.sample(min(2500, len(df_seg))),
                x='pca_x',
                y='pca_y',
                color='segment_name',
                labels={'pca_x': 'Engagement & Browsing Frequency', 'pca_y': 'Purchase Intent & Spend'},
                color_discrete_sequence=['#C0266D', '#241126', '#E879A8', '#715575']
            )
            fig_cluster.update_layout(
                height=400,
                margin=dict(l=10, r=10, t=10, b=10),
                plot_bgcolor='#FFFFFF',
                paper_bgcolor='#FFFFFF',
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=12))
            )
            st.plotly_chart(fig_cluster, use_container_width=True)

        with col_s2:
            st.markdown("<h4 style='font-size: 17px;'>Persona Attributes & Targeted Strategy</h4>", unsafe_allow_html=True)
            seg_summary = df_seg.groupby('segment_name').agg(
                users=('visitorid', 'count'),
                avg_spend=('total_spend', 'mean'),
                avg_orders=('purchases_count', 'mean'),
                avg_views=('views_count', 'mean')
            ).reset_index()

            for _, row in seg_summary.iterrows():
                st.markdown(f"""
                <div style="background-color:#FFFFFF; border:1px solid #F3D5E5; border-radius:12px; padding:12px 14px; margin-bottom:10px;">
                    <p style="font-size:14px; font-weight:700; color:#C0266D; margin-bottom:2px;">{row['segment_name']}</p>
                    <p style="font-size:13px; color:#241126; margin-bottom:0;">
                        <strong>Audience:</strong> {row['users']:,} shoppers | <strong>Avg Spend:</strong> ₹{row['avg_spend']:.0f}<br>
                        <strong>Avg Orders:</strong> {row['avg_orders']:.1f} | <strong>Avg Views:</strong> {row['avg_views']:.1f}
                    </p>
                </div>
                """, unsafe_allow_html=True)

# =========================================================
# TAB: PURCHASE PROPENSITY PREDICTION
# =========================================================
with tab_supervised:
    st.markdown("""
    <div style="margin-bottom: 16px;">
        <h3 style="font-size: 22px; margin-bottom: 2px;">Purchase Propensity Predictions</h3>
        <p style="font-size: 14px; color: #6E4968;">Predictive intelligence identifying high-intent shoppers ready to buy based on real-time browsing behavior.</p>
    </div>
    """, unsafe_allow_html=True)

    if ml_bundle:
        metrics = ml_bundle['metrics']

        # Metrics Row
        m_c1, m_c2, m_c3, m_c4 = st.columns(4)
        m_c1.metric("Predictive Accuracy (ROC-AUC)", f"{metrics['ROC_AUC']:.3f}", "Industry Leading")
        m_c2.metric("Intent Precision (PR-AUC)", f"{metrics['PR_AUC']:.3f}", "High precision")
        m_c3.metric("Balanced F1-Score", f"{metrics['F1_Score']:.3f}", "Optimal balance")
        m_c4.metric("Buyer Capture (Recall)", f"{metrics['Recall']:.1%}", "Buyer detection")

        st.markdown("---")
        col_eval1, col_eval2 = st.columns(2)

        with col_eval1:
            st.markdown("<h4 style='font-size: 17px;'>Model Prediction Performance Curve</h4>", unsafe_allow_html=True)
            roc_data = ml_bundle['roc_curve']
            fig_roc = go.Figure()
            fig_roc.add_trace(go.Scatter(
                x=roc_data['fpr'], y=roc_data['tpr'],
                name=f"Predictive Model (AUC = {metrics['ROC_AUC']:.3f})",
                line=dict(color='#C0266D', width=3)
            ))
            fig_roc.add_trace(go.Scatter(
                x=[0, 1], y=[0, 1],
                name="Baseline",
                line=dict(color='#715575', dash='dash')
            ))
            fig_roc.update_layout(
                height=340,
                margin=dict(l=10, r=10, t=10, b=10),
                plot_bgcolor='#FFFFFF',
                paper_bgcolor='#FFFFFF',
                xaxis_title="False Positive Rate",
                yaxis_title="True Positive Rate"
            )
            st.plotly_chart(fig_roc, use_container_width=True)

        with col_eval2:
            st.markdown("<h4 style='font-size: 17px;'>Top Signals Influencing Purchase Intent</h4>", unsafe_allow_html=True)
            feat_df = ml_bundle['feature_importance'].sort_values('importance', ascending=True)
            fig_feat = px.bar(
                feat_df,
                x='importance',
                y='feature',
                orientation='h',
                color_discrete_sequence=['#C0266D']
            )
            fig_feat.update_layout(
                height=340,
                margin=dict(l=10, r=10, t=10, b=10),
                plot_bgcolor='#FFFFFF',
                paper_bgcolor='#FFFFFF',
                xaxis_title="Impact Weight",
                yaxis_title=""
            )
            st.plotly_chart(fig_feat, use_container_width=True)

# =========================================================
# TAB: CO-OCCURRENCE AFFINITY
# =========================================================
with tab_cooccurrence:
    st.markdown("""
    <div style="margin-bottom: 16px;">
        <h3 style="font-size: 22px; margin-bottom: 2px;">Product Co-Occurrence Affinity</h3>
        <p style="font-size: 14px; color: #6E4968;">Pairwise shopping affinity matrix identifying products frequently bought together for cross-selling.</p>
    </div>
    """, unsafe_allow_html=True)

    df_coocc, _ = engine.get_product_cooccurrence_matrix(top_n_items=10)
    heatmap_matrix = df_coocc.pivot(index='item_a', columns='item_b', values='cooccurrences').fillna(0)

    fig_heat = px.imshow(
        heatmap_matrix,
        labels=dict(x="Associated Product", y="Primary Product", color="Co-Interactions"),
        x=heatmap_matrix.columns,
        y=heatmap_matrix.index,
        color_continuous_scale=[[0, '#FFF8FA'], [0.35, '#F3D5E5'], [0.7, '#E879A8'], [1.0, '#C0266D']],
        aspect="auto"
    )
    fig_heat.update_layout(
        height=520,
        margin=dict(l=10, r=10, t=10, b=10)
    )
    st.plotly_chart(fig_heat, use_container_width=True)

# =========================================================
# TAB: ABOUT BLUSH & BASKET
# =========================================================
with tab_guide:
    st.markdown("""
    <div style="background:#FFFFFF; border:1px solid #F3D5E5; border-radius:18px; padding:28px; box-shadow:0 8px 24px rgba(36,17,38,0.05);">
        <h2 style="font-family:'Playfair Display', serif; font-size:28px; color:#241126; margin-bottom:12px;">
            💄 About Blush & Basket
        </h2>
        <p style="font-size:15px; color:#6E4968; line-height:1.6;">
            <strong>Blush & Basket</strong> is a modern commercial intelligence platform designed for high-growth beauty 
            and cosmetics brands. It brings together clickstream analytics, conversion funnel optimization, 
            customer behavioral clustering, and automated routine recommendations in an aesthetic, executive interface.
        </p>

        <hr style="border-color:#F3D5E5; margin:20px 0;" />

        <h3 style="font-size:20px; color:#C0266D; margin-bottom:8px;">1. Full-Funnel Journey Optimization</h3>
        <p style="font-size:14px; color:#241126; line-height:1.6;">
            Monitors customer transitions through every step of the shopping journey. By quantifying drop-offs from initial 
            catalog discovery to shopping bag additions and final checkout, growth teams can pinpoint exactly where 
            friction occurs and optimize conversion rates.
        </p>

        <h3 style="font-size:20px; color:#C0266D; margin-top:20px; margin-bottom:8px;">2. Customer Personas & Personalization</h3>
        <p style="font-size:14px; color:#241126; line-height:1.6;">
            Instead of treating all visitors alike, shoppers are categorized into distinct behavioral personas—from 
            <strong>VIP Beauty Mavens</strong> to <strong>High-Intent Shoppers</strong> and <strong>Engaged Window Shoppers</strong>. 
            This enables hyper-personalized marketing campaigns, exclusive rewards, and targeted flash offers.
        </p>

        <h3 style="font-size:20px; color:#C0266D; margin-top:20px; margin-bottom:8px;">3. Automated Routine Bundles</h3>
        <p style="font-size:14px; color:#241126; line-height:1.6;">
            Using market basket affinity algorithms, Blush & Basket automatically pairs complementary products (such as serums with sunscreens 
            or foundations with lip colors) to present customers with 1-click routine bundles, driving higher Average Order Values (AOV).
        </p>
    </div>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("""
<div style="text-align: center; padding: 30px 0 10px 0; color: #715575; font-size: 13px;">
    Blush & Basket · Commercial Intelligence Platform · Pinterest Aesthetic Edition
</div>
""", unsafe_allow_html=True)
