"""
Product Imagery & Aesthetic Metadata Registry
Provides Pinterest-style high-resolution photography URLs, aesthetic tags,
ratings, reviews counts, and fallback visual generators for all beauty catalog items.
"""

# Map of itemid to curated aesthetic beauty photography and metadata
PRODUCT_METADATA = {
    # Lip Makeup
    101: {
        "image_url": "https://images.unsplash.com/photo-1586495777744-4413f21062fa?auto=format&fit=crop&w=600&q=80",
        "tag": "Pinterest Favorite",
        "tag_color": "#C0266D",
        "rating": 4.8,
        "reviews": 3420,
        "vibe": "Velvet Matte Finish · 12H Wear"
    },
    102: {
        "image_url": "https://images.unsplash.com/photo-1625093742435-6fa192b6fb10?auto=format&fit=crop&w=600&q=80",
        "tag": "Trending Aesthetic",
        "tag_color": "#D84374",
        "rating": 4.7,
        "reviews": 1850,
        "vibe": "Soft Petal Nude · Creamy Glide"
    },
    103: {
        "image_url": "https://images.unsplash.com/photo-1571781926291-c477ebfd024b?auto=format&fit=crop&w=600&q=80",
        "tag": "Luxe Must-Have",
        "tag_color": "#9B3264",
        "rating": 4.9,
        "reviews": 4210,
        "vibe": "Featherlight Liquid · Transfer-Proof"
    },
    104: {
        "image_url": "https://images.unsplash.com/photo-1596462502278-27bfdc403348?auto=format&fit=crop&w=600&q=80",
        "tag": "Iconic Cult Classic",
        "tag_color": "#C0266D",
        "rating": 4.9,
        "reviews": 5600,
        "vibe": "Signature Blue-Red · Intense Pigment"
    },
    105: {
        "image_url": "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?auto=format&fit=crop&w=600&q=80",
        "tag": "Clean Beauty Pick",
        "tag_color": "#B8729A",
        "rating": 4.6,
        "reviews": 980,
        "vibe": "Hydrating Marula Oil Infusion"
    },

    # Face Makeup
    201: {
        "image_url": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=600&q=80",
        "tag": "Bestseller",
        "tag_color": "#C0266D",
        "rating": 4.7,
        "reviews": 2980,
        "vibe": "Seamless Natural Matte · Pore-Blurring"
    },
    202: {
        "image_url": "https://images.unsplash.com/photo-1631729371254-42c2892f0e6e?auto=format&fit=crop&w=600&q=80",
        "tag": "Daily Essential",
        "tag_color": "#D84374",
        "rating": 4.6,
        "reviews": 6400,
        "vibe": "Micro-Powder Oil Control Formula"
    },
    203: {
        "image_url": "https://images.unsplash.com/photo-1616683693504-3ea7e9ad6fec?auto=format&fit=crop&w=600&q=80",
        "tag": "Runway Luxe",
        "tag_color": "#9B3264",
        "rating": 4.9,
        "reviews": 3890,
        "vibe": "24H Flawless Medium-to-Full Coverage"
    },
    204: {
        "image_url": "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?auto=format&fit=crop&w=600&q=80",
        "tag": "Dewy Radiance",
        "tag_color": "#E879A8",
        "rating": 4.8,
        "reviews": 1240,
        "vibe": "Avocado & Hyaluronic Glow Infusion"
    },
    205: {
        "image_url": "https://images.unsplash.com/photo-1515688594390-b649af70d282?auto=format&fit=crop&w=600&q=80",
        "tag": "Transfer-Proof",
        "tag_color": "#B8729A",
        "rating": 4.7,
        "reviews": 2150,
        "vibe": "Breathable 32H Waterproof Complex"
    },

    # Skincare Serums
    301: {
        "image_url": "https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=600&q=80",
        "tag": "#1 Skincare Star",
        "tag_color": "#C0266D",
        "rating": 4.9,
        "reviews": 8420,
        "vibe": "10% Pure Niacinamide + EUK-134"
    },
    302: {
        "image_url": "https://images.unsplash.com/photo-1608248597359-4974fcf37d7a?auto=format&fit=crop&w=600&q=80",
        "tag": "Moisture Drench",
        "tag_color": "#D84374",
        "rating": 4.8,
        "reviews": 6120,
        "vibe": "Multi-Molecular Hydration Plumping"
    },
    303: {
        "image_url": "https://images.unsplash.com/photo-1601049541289-9b1b7bbbfe19?auto=format&fit=crop&w=600&q=80",
        "tag": "Glow Viral Pick",
        "tag_color": "#E879A8",
        "rating": 4.8,
        "reviews": 4760,
        "vibe": "Ethyl Ascorbic Acid + Japanese Mandarin"
    },
    304: {
        "image_url": "https://images.unsplash.com/photo-1617897903246-719242758050?auto=format&fit=crop&w=600&q=80",
        "tag": "Exfoliating Cult",
        "tag_color": "#9B3264",
        "rating": 4.9,
        "reviews": 7300,
        "vibe": "10-Minute Exfoliating Facial Peel"
    },
    305: {
        "image_url": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?auto=format&fit=crop&w=600&q=80",
        "tag": "Blemish Clear",
        "tag_color": "#B8729A",
        "rating": 4.6,
        "reviews": 1690,
        "vibe": "Dermatologist Tested Pore Purifier"
    },

    # Sun Protection
    401: {
        "image_url": "https://images.unsplash.com/photo-1556228720-195a672e8a03?auto=format&fit=crop&w=600&q=80",
        "tag": "Glass Skin Shield",
        "tag_color": "#C0266D",
        "rating": 4.9,
        "reviews": 5190,
        "vibe": "Zero White Cast · Soothing Cica Gel"
    },
    402: {
        "image_url": "https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?auto=format&fit=crop&w=600&q=80",
        "tag": "Matte Sun Armor",
        "tag_color": "#D84374",
        "rating": 4.8,
        "reviews": 4350,
        "vibe": "Broad Spectrum PA++++ Hybrid Filters"
    },
    403: {
        "image_url": "https://images.unsplash.com/photo-1567928815104-b7980ee5032e?auto=format&fit=crop&w=600&q=80",
        "tag": "Cooling Hydration",
        "tag_color": "#E879A8",
        "rating": 4.7,
        "reviews": 2320,
        "vibe": "Watermelon Extract + Instant Refresh"
    },
    404: {
        "image_url": "https://images.unsplash.com/photo-1576426863848-c21f53c60b19?auto=format&fit=crop&w=600&q=80",
        "tag": "Calming Sheer",
        "tag_color": "#B8729A",
        "rating": 4.6,
        "reviews": 1420,
        "vibe": "Chamomile Infusion for Sensitive Skin"
    },

    # Moisturizers
    501: {
        "image_url": "https://images.unsplash.com/photo-1556228722-d0b5de70b77b?auto=format&fit=crop&w=600&q=80",
        "tag": "Barrier Hero",
        "tag_color": "#C0266D",
        "rating": 4.9,
        "reviews": 6800,
        "vibe": "0.3% Pure Ceramide Complex + Bisabolol"
    },
    502: {
        "image_url": "https://images.unsplash.com/photo-1563178406-4cdc2923acbc?auto=format&fit=crop&w=600&q=80",
        "tag": "Ultra Hydrator",
        "tag_color": "#D84374",
        "rating": 4.8,
        "reviews": 3900,
        "vibe": "Oil-Free Lightweight Water Drop Burst"
    },
    503: {
        "image_url": "https://images.unsplash.com/photo-1608248597359-4974fcf37d7a?auto=format&fit=crop&w=600&q=80",
        "tag": "Overnight Calm",
        "tag_color": "#B8729A",
        "rating": 4.7,
        "reviews": 2650,
        "vibe": "Antioxidant Green Tea Clear Gel"
    },
    504: {
        "image_url": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=600&q=80",
        "tag": "Botanical Glow",
        "tag_color": "#E879A8",
        "rating": 4.6,
        "reviews": 1820,
        "vibe": "Natural Moisturizing Factors + Phytosterols"
    },

    # Haircare
    601: {
        "image_url": "https://images.unsplash.com/photo-1535585209827-a15fcdbc4c2d?auto=format&fit=crop&w=600&q=80",
        "tag": "Silk Strands",
        "tag_color": "#D84374",
        "rating": 4.7,
        "reviews": 3100,
        "vibe": "72H Hyaluronic Acid Moisture Lock"
    },
    602: {
        "image_url": "https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?auto=format&fit=crop&w=600&q=80",
        "tag": "Root Revival",
        "tag_color": "#C0266D",
        "rating": 4.8,
        "reviews": 4890,
        "vibe": "Pure Rosemary Leaf Essential Oil Elixir"
    },
    603: {
        "image_url": "https://images.unsplash.com/photo-1527799820374-dcf8d9d4a388?auto=format&fit=crop&w=600&q=80",
        "tag": "Bond Multiplier",
        "tag_color": "#9B3264",
        "rating": 4.9,
        "reviews": 2980,
        "vibe": "5% Maleic Bond Repair Strengthening"
    },

    # Fragrance
    701: {
        "image_url": "https://images.unsplash.com/photo-1592945403244-b3fbafd7f539?auto=format&fit=crop&w=600&q=80",
        "tag": "Signature Scent",
        "tag_color": "#C0266D",
        "rating": 4.9,
        "reviews": 2750,
        "vibe": "Parisian Rose, Violet Petals & Amber Vanilla"
    },
    702: {
        "image_url": "https://images.unsplash.com/photo-1547887537-6158d64c35b3?auto=format&fit=crop&w=600&q=80",
        "tag": "Warm Gourmand",
        "tag_color": "#E879A8",
        "rating": 4.7,
        "reviews": 3840,
        "vibe": "Sweet Madagascar Vanilla & Marshmallow Mist"
    },
    703: {
        "image_url": "https://images.unsplash.com/photo-1523293182086-7651a899d37f?auto=format&fit=crop&w=600&q=80",
        "tag": "Celebrity Scent",
        "tag_color": "#9B3264",
        "rating": 4.8,
        "reviews": 1960,
        "vibe": "Velvety Plum, Cedarwood & White Musks"
    }
}

DEFAULT_METADATA = {
    "image_url": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?auto=format&fit=crop&w=600&q=80",
    "tag": "Beauty Curated",
    "tag_color": "#C0266D",
    "rating": 4.7,
    "reviews": 1500,
    "vibe": "Premium Beauty Formulation"
}

def get_product_metadata(itemid):
    """Retrieve curated aesthetic imagery and metadata for a product."""
    return PRODUCT_METADATA.get(itemid, DEFAULT_METADATA)
