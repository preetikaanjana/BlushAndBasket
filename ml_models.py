"""
Machine Learning Engine for Beauty Commerce Analytics
Implements:
- Priority 5: Customer Segmentation (Unsupervised ML - K-Means & PCA)
- Priority 6: Purchase Model Evaluation (Supervised ML - Classification, ROC/PR curves)
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    roc_curve, roc_auc_score, precision_recall_curve,
    average_precision_score, confusion_matrix, accuracy_score,
    f1_score, precision_score, recall_score
)

def train_customer_segmentation_and_purchase_model(events_path="data/beauty_events.parquet", models_dir="models"):
    print("Loading beauty events for ML...")
    df_events = pd.read_parquet(events_path)
    
    # Reference date for recency calculation (latest date + 1 day)
    ref_timestamp = df_events['timestamp'].max() + 86400 * 1000

    # 1. Feature Aggregation at Visitor Level
    visitor_stats = df_events.groupby('visitorid').agg(
        recency_days=('timestamp', lambda ts: (ref_timestamp - ts.max()) / (1000 * 86400)),
        total_events=('event', 'count'),
        views_count=('event', lambda e: (e == 'view').sum()),
        carts_count=('event', lambda e: (e == 'addtocart').sum()),
        purchases_count=('event', lambda e: (e == 'transaction').sum()),
        unique_items=('itemid', 'nunique'),
        unique_categories=('category', 'nunique'),
        total_spend=('price', lambda p: p[df_events.loc[p.index, 'event'] == 'transaction'].sum())
    ).reset_index()

    visitor_stats['cart_to_view_ratio'] = (visitor_stats['carts_count'] / (visitor_stats['views_count'] + 0.1)).round(3)
    visitor_stats['has_purchased'] = (visitor_stats['purchases_count'] > 0).astype(int)

    # -------------------------------------------------------------
    # Priority 5: Customer Segmentation (Unsupervised ML - KMeans)
    # -------------------------------------------------------------
    print("Fitting K-Means Customer Segmentation...")
    cluster_features = [
        'recency_days', 'total_events', 'views_count', 
        'carts_count', 'purchases_count', 'unique_items', 'total_spend'
    ]
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(visitor_stats[cluster_features])
    
    kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
    visitor_stats['cluster'] = kmeans.fit_predict(X_scaled)
    
    # 2D PCA projection for beautiful visualization
    pca = PCA(n_components=2, random_state=42)
    pca_coords = pca.fit_transform(X_scaled)
    visitor_stats['pca_x'] = pca_coords[:, 0]
    visitor_stats['pca_y'] = pca_coords[:, 1]

    # Map Clusters to Business Personas based on centroids
    centroids = visitor_stats.groupby('cluster')[['purchases_count', 'carts_count', 'views_count', 'total_spend', 'recency_days']].mean()
    
    # Identify clusters
    vip_cluster = centroids['total_spend'].idxmax()
    cart_cluster = centroids['carts_count'].idxmax() if centroids['carts_count'].idxmax() != vip_cluster else centroids['carts_count'].nlargest(2).index[1]
    window_cluster = centroids['views_count'].idxmax() if centroids['views_count'].idxmax() not in [vip_cluster, cart_cluster] else centroids['views_count'].nlargest(3).index[2]
    other_clusters = [c for c in range(4) if c not in [vip_cluster, cart_cluster, window_cluster]]
    casual_cluster = other_clusters[0] if other_clusters else 3

    persona_map = {
        vip_cluster: "VIP Beauty Mavens (High Spend)",
        cart_cluster: "High-Intent Shoppers (Frequent Carts)",
        window_cluster: "Engaged Window Shoppers (High Views)",
        casual_cluster: "Casual / Occasional Browsers"
    }
    visitor_stats['segment_name'] = visitor_stats['cluster'].map(persona_map)
    print("Customer Segments distribution:\n", visitor_stats['segment_name'].value_counts())

    # -------------------------------------------------------------
    # Priority 6: Purchase Model Evaluation (Supervised ML)
    # -------------------------------------------------------------
    print("Training Purchase Prediction Classification Model...")
    ml_features = [
        'recency_days', 'total_events', 'views_count', 
        'carts_count', 'unique_items', 'unique_categories', 'cart_to_view_ratio'
    ]
    
    X = visitor_stats[ml_features]
    y = visitor_stats['has_purchased']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    clf = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42, class_weight='balanced')
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    y_prob = clf.predict_proba(X_test)[:, 1]

    # Model Evaluation Metrics
    auc = roc_auc_score(y_test, y_prob)
    pr_auc = average_precision_score(y_test, y_prob)
    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred)

    # ROC Curve points
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    # PR Curve points
    pr_precision, pr_recall, _ = precision_recall_curve(y_test, y_prob)

    # Feature Importance
    feat_imp = pd.DataFrame({
        'feature': ml_features,
        'importance': clf.feature_importances_
    }).sort_values('importance', ascending=False).reset_index(drop=True)

    print(f"Purchase Model -> ROC-AUC: {auc:.4f} | PR-AUC: {pr_auc:.4f} | F1: {f1:.4f} | Recall: {rec:.4f}")
    print("\nTop Feature Importances:\n", feat_imp)

    # Save artifacts
    os.makedirs(models_dir, exist_ok=True)
    bundle = {
        'visitor_segments': visitor_stats,
        'cluster_centroids': centroids,
        'persona_map': persona_map,
        'model': clf,
        'features': ml_features,
        'metrics': {
            'ROC_AUC': round(auc, 4),
            'PR_AUC': round(pr_auc, 4),
            'Accuracy': round(acc, 4),
            'F1_Score': round(f1, 4),
            'Precision': round(prec, 4),
            'Recall': round(rec, 4),
            'Confusion_Matrix': cm.tolist()
        },
        'roc_curve': {'fpr': fpr.tolist(), 'tpr': tpr.tolist()},
        'pr_curve': {'precision': pr_precision.tolist(), 'recall': pr_recall.tolist()},
        'feature_importance': feat_imp
    }

    bundle_path = os.path.join(models_dir, "beauty_ml_bundle.joblib")
    joblib.dump(bundle, bundle_path)
    print(f"ML artifacts saved to {bundle_path}")

    return bundle

if __name__ == "__main__":
    train_customer_segmentation_and_purchase_model()
