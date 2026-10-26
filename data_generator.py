"""
Beauty Commerce Dataset Generator (Nykaa-Inspired RetailRocket Schema)
Generates realistic beauty catalog and event logs with authentic co-occurrence.
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_beauty_ecommerce_data(n_events=75000, random_state=42):
    np.random.seed(random_state)
    print(f"Generating Nykaa-inspired beauty commerce dataset ({n_events} events)...")

    # 1. Beauty Product Catalog (Nykaa Inspired)
    products = [
        {"itemid": 101, "item_name": "Matte to Last Liquid Lipstick", "category": "Lip Makeup", "brand": "Nykaa Cosmetics", "price": 599},
        {"itemid": 102, "item_name": "Ultra Matte Lipstick - Nude Twist", "category": "Lip Makeup", "brand": "Nykaa Cosmetics", "price": 450},
        {"itemid": 103, "item_name": "Liquid Matte Minis Lipstick", "category": "Lip Makeup", "brand": "Huda Beauty", "price": 1950},
        {"itemid": 104, "item_name": "Retro Matte Lipstick - Ruby Woo", "category": "Lip Makeup", "brand": "MAC Cosmetics", "price": 2300},
        {"itemid": 105, "item_name": "Matteinee Lip Crayon", "category": "Lip Makeup", "brand": "Kay Beauty", "price": 799},
        
        {"itemid": 201, "item_name": "All Day Matte Foundation", "category": "Face Makeup", "brand": "Nykaa Cosmetics", "price": 599},
        {"itemid": 202, "item_name": "Fit Me Matte+Poreless Foundation", "category": "Face Makeup", "brand": "Maybelline New York", "price": 649},
        {"itemid": 203, "item_name": "Studio Fix Fluid SPF 15", "category": "Face Makeup", "brand": "MAC Cosmetics", "price": 3600},
        {"itemid": 204, "item_name": "Hydrating Foundation", "category": "Face Makeup", "brand": "Kay Beauty", "price": 1200},
        {"itemid": 205, "item_name": "Infallible Fresh Wear Foundation", "category": "Face Makeup", "brand": "L'Oréal Paris", "price": 1199},
        
        {"itemid": 301, "item_name": "10% Niacinamide Face Serum", "category": "Skincare Serums", "brand": "Minimalist", "price": 599},
        {"itemid": 302, "item_name": "Hyaluronic Acid 2% + B5 Serum", "category": "Skincare Serums", "brand": "The Ordinary", "price": 700},
        {"itemid": 303, "item_name": "15% Vitamin C Glow Serum", "category": "Skincare Serums", "brand": "Plum Goodness", "price": 675},
        {"itemid": 304, "item_name": "AHA 30% + BHA 2% Peeling Solution", "category": "Skincare Serums", "brand": "The Ordinary", "price": 950},
        {"itemid": 305, "item_name": "SkinRX 2% Salicylic Acid Serum", "category": "Skincare Serums", "brand": "Nykaa SKINRX", "price": 799},
        
        {"itemid": 401, "item_name": "Cica Calming Daily Sunscreen SPF 50", "category": "Sun Protection", "brand": "Dot & Key", "price": 495},
        {"itemid": 402, "item_name": "Ultra Matte Gel Sunscreen SPF 50", "category": "Sun Protection", "brand": "Minimalist", "price": 399},
        {"itemid": 403, "item_name": "Watermelon Cooling Sunscreen", "category": "Sun Protection", "brand": "Dot & Key", "price": 545},
        {"itemid": 404, "item_name": "Chamomile Sheer Sunscreen", "category": "Sun Protection", "brand": "Plum Goodness", "price": 520},
        
        {"itemid": 501, "item_name": "Ceramide Barrier Repair Moisturizer", "category": "Moisturizers", "brand": "Minimalist", "price": 599},
        {"itemid": 502, "item_name": "72h Hydrating Super Gel", "category": "Moisturizers", "brand": "Dot & Key", "price": 495},
        {"itemid": 503, "item_name": "Green Tea Oil-Free Night Gel", "category": "Moisturizers", "brand": "Plum Goodness", "price": 575},
        {"itemid": 504, "item_name": "Natural Glow Cream", "category": "Moisturizers", "brand": "The Ordinary", "price": 850},
        
        {"itemid": 601, "item_name": "Hyaluronic Moisture Shampoo", "category": "Haircare", "brand": "L'Oréal Paris", "price": 499},
        {"itemid": 602, "item_name": "Rosemary Anti-Hair Fall Oil", "category": "Haircare", "brand": "Nykaa Naturals", "price": 399},
        {"itemid": 603, "item_name": "Maleic Bond Repair Complex Hair Mask", "category": "Haircare", "brand": "Minimalist", "price": 699},
        
        {"itemid": 701, "item_name": "Moi By Nykaa - Amour Perfume", "category": "Fragrance", "brand": "Nykaa Cosmetics", "price": 1800},
        {"itemid": 702, "item_name": "Vanilla Vibes Body Mist", "category": "Fragrance", "brand": "Plum Goodness", "price": 575},
        {"itemid": 703, "item_name": "Love Child Perfume", "category": "Fragrance", "brand": "Kay Beauty", "price": 1499}
    ]
    
    # Enrich with Pinterest aesthetic imagery & metadata
    from product_images import PRODUCT_METADATA, DEFAULT_METADATA
    for p in products:
        meta = PRODUCT_METADATA.get(p["itemid"], DEFAULT_METADATA)
        p["image_url"] = meta["image_url"]
        p["tag"] = meta["tag"]
        p["tag_color"] = meta["tag_color"]
        p["rating"] = meta["rating"]
        p["reviews_count"] = meta["reviews"]
        p["vibe"] = meta["vibe"]

    df_products = pd.DataFrame(products)

    # Co-occurrence Affinity Rules:
    # Serums (301-305) often co-occur with Sunscreens (401-404) & Moisturizers (501-504)
    # Lipsticks (101-105) often co-occur with Foundation (201-205)
    skincare_items = [301, 302, 303, 304, 305, 401, 402, 403, 404, 501, 502, 503, 504]
    makeup_items = [101, 102, 103, 104, 105, 201, 202, 203, 204, 205]
    all_item_ids = df_products['itemid'].tolist()

    # 2. Visitors & Sessions Generation
    n_visitors = 4500
    visitor_ids = np.random.randint(100000, 100000 + n_visitors, size=n_events)
    
    # 60 days time range
    start_date = datetime(2026, 8, 1, 0, 0, 0)
    timestamps_sec = np.sort(np.random.uniform(0, 60 * 86400, size=n_events))
    event_datetimes = [start_date + timedelta(seconds=float(s)) for s in timestamps_sec]
    timestamps_ms = [int(dt.timestamp() * 1000) for dt in event_datetimes]

    event_records = []
    transaction_counter = 50000

    # User personas
    # 0 = Skincare lover, 1 = Makeup enthusiast, 2 = General shopper
    user_personas = {vid: np.random.choice([0, 1, 2], p=[0.45, 0.40, 0.15]) for vid in np.unique(visitor_ids)}

    for i in range(n_events):
        vid = visitor_ids[i]
        dt = event_datetimes[i]
        ts = timestamps_ms[i]
        persona = user_personas[vid]

        # Select item based on persona
        if persona == 0:
            item_choice = np.random.choice(skincare_items if np.random.rand() < 0.8 else all_item_ids)
        elif persona == 1:
            item_choice = np.random.choice(makeup_items if np.random.rand() < 0.8 else all_item_ids)
        else:
            item_choice = np.random.choice(all_item_ids)

        # Event type probabilities: View (~82%), AddToCart (~13%), Transaction (~5%)
        # Some items have naturally higher conversion (e.g. Nykaa lipstick, Minimalist Niacinamide)
        p_roll = np.random.rand()
        if p_roll < 0.81:
            event_type = 'view'
            tx_id = None
        elif p_roll < 0.94:
            event_type = 'addtocart'
            tx_id = None
        else:
            event_type = 'transaction'
            transaction_counter += 1
            tx_id = transaction_counter

        event_records.append({
            'timestamp': ts,
            'datetime': dt,
            'date': dt.strftime('%Y-%m-%d'),
            'visitorid': vid,
            'event': event_type,
            'itemid': item_choice,
            'transactionid': tx_id
        })

    df_events = pd.DataFrame(event_records)

    # Merge product details
    df_merged = df_events.merge(df_products, on='itemid', how='left')

    os.makedirs("data", exist_ok=True)
    events_path = "data/beauty_events.parquet"
    products_path = "data/beauty_products.parquet"
    
    df_merged.to_parquet(events_path, index=False)
    df_products.to_parquet(products_path, index=False)

    print("Beauty commerce dataset generated successfully!")
    print(f"Total events: {len(df_merged):,}")
    print(f"Events by type:\n{df_merged['event'].value_counts()}")
    print(f"Unique visitors: {df_merged['visitorid'].nunique():,}")
    print(f"Unique products: {df_products['itemid'].nunique():,}")

    return df_merged, df_products

if __name__ == "__main__":
    generate_beauty_ecommerce_data()
