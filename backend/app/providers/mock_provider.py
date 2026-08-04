import random
import math
import time
from typing import List, Optional
from .base import BaseProvider, ProductResult


# ──────────────────────────────────────────────────────────────────────────────
# Store catalogue
# ──────────────────────────────────────────────────────────────────────────────
STORES = [
    {"name": "Amazon",   "url": "https://www.amazon.com/dp/B0{code}"},
    {"name": "Walmart",  "url": "https://www.walmart.com/ip/{code}"},
    {"name": "Best Buy", "url": "https://www.bestbuy.com/site/product/{code}.p"},
    {"name": "Target",   "url": "https://www.target.com/p/-/A-{code}"},
    {"name": "eBay",     "url": "https://www.ebay.com/itm/{code}"},
    {"name": "Newegg",   "url": "https://www.newegg.com/p/N82E{code}"},
    {"name": "B&H Photo","url": "https://www.bhphotovideo.com/c/product/{code}"},
    {"name": "Costco",   "url": "https://www.costco.com/product.product.{code}.html"},
]

# ──────────────────────────────────────────────────────────────────────────────
# Product templates keyed by category keywords
# ──────────────────────────────────────────────────────────────────────────────
PRODUCT_TEMPLATES = {
    "iphone": [
        {"name": "Apple iPhone 15 Pro Max 256GB Natural Titanium", "base_price": 1199.99, "img_seed": 10},
        {"name": "Apple iPhone 15 Pro 128GB Black Titanium",        "base_price": 999.99,  "img_seed": 11},
        {"name": "Apple iPhone 15 256GB Blue",                      "base_price": 829.99,  "img_seed": 12},
        {"name": "Apple iPhone 14 128GB Midnight",                  "base_price": 699.99,  "img_seed": 13},
        {"name": "Apple iPhone SE (3rd Gen) 64GB Starlight",        "base_price": 429.99,  "img_seed": 14},
    ],
    "samsung": [
        {"name": "Samsung Galaxy S24 Ultra 512GB Titanium Black",   "base_price": 1299.99, "img_seed": 20},
        {"name": "Samsung Galaxy S24+ 256GB Cobalt Violet",         "base_price": 999.99,  "img_seed": 21},
        {"name": "Samsung Galaxy S24 128GB Onyx Black",             "base_price": 799.99,  "img_seed": 22},
        {"name": "Samsung Galaxy A55 5G 128GB Navy",                "base_price": 449.99,  "img_seed": 23},
        {"name": "Samsung Galaxy Z Fold 6 256GB Navy",              "base_price": 1799.99, "img_seed": 24},
    ],
    "laptop": [
        {"name": "Apple MacBook Pro 16\" M3 Pro 512GB",             "base_price": 2499.99, "img_seed": 30},
        {"name": "Dell XPS 15 Intel Core i9 1TB RTX 4070",         "base_price": 1999.99, "img_seed": 31},
        {"name": "ASUS ROG Zephyrus G14 Ryzen 9 1TB RTX 4060",     "base_price": 1649.99, "img_seed": 32},
        {"name": "Lenovo ThinkPad X1 Carbon Gen 12 512GB",         "base_price": 1599.99, "img_seed": 33},
        {"name": "HP Spectre x360 14\" Intel Core Ultra 7",         "base_price": 1399.99, "img_seed": 34},
        {"name": "Microsoft Surface Laptop Studio 2 RTX 4060",     "base_price": 1799.99, "img_seed": 35},
    ],
    "headphones": [
        {"name": "Sony WH-1000XM5 Wireless Noise Canceling",        "base_price": 349.99,  "img_seed": 40},
        {"name": "Apple AirPods Pro 2nd Generation",                "base_price": 249.99,  "img_seed": 41},
        {"name": "Bose QuietComfort Ultra Headphones",              "base_price": 429.99,  "img_seed": 42},
        {"name": "Sennheiser Momentum 4 Wireless",                  "base_price": 349.99,  "img_seed": 43},
        {"name": "Jabra Evolve2 85 ANC Headset",                    "base_price": 449.99,  "img_seed": 44},
    ],
    "gpu": [
        {"name": "NVIDIA GeForce RTX 4090 24GB GDDR6X",            "base_price": 1599.99, "img_seed": 50},
        {"name": "NVIDIA GeForce RTX 4080 Super 16GB",             "base_price": 999.99,  "img_seed": 51},
        {"name": "AMD Radeon RX 7900 XTX 24GB",                    "base_price": 899.99,  "img_seed": 52},
        {"name": "NVIDIA GeForce RTX 4070 Ti Super 16GB",          "base_price": 799.99,  "img_seed": 53},
        {"name": "AMD Radeon RX 7800 XT 16GB",                     "base_price": 499.99,  "img_seed": 54},
    ],
    "gaming": [
        {"name": "PlayStation 5 Console (Disc Edition)",            "base_price": 499.99,  "img_seed": 60},
        {"name": "Xbox Series X 1TB Console",                       "base_price": 499.99,  "img_seed": 61},
        {"name": "Nintendo Switch OLED Model",                      "base_price": 349.99,  "img_seed": 62},
        {"name": "Steam Deck OLED 512GB",                           "base_price": 549.99,  "img_seed": 63},
        {"name": "Xbox Series S 512GB Carbon Black",                "base_price": 299.99,  "img_seed": 64},
    ],
    "tv": [
        {"name": "LG C3 65\" OLED evo 4K Smart TV",                "base_price": 1499.99, "img_seed": 70},
        {"name": "Samsung 65\" QN90C Neo QLED 4K Smart TV",        "base_price": 1799.99, "img_seed": 71},
        {"name": "Sony Bravia XR 55\" A95L QD-OLED 4K",            "base_price": 2499.99, "img_seed": 72},
        {"name": "TCL 75\" Q8 Series QLED 4K Google TV",           "base_price": 799.99,  "img_seed": 73},
        {"name": "Hisense 65\" U8K Mini-LED ULED 4K",              "base_price": 999.99,  "img_seed": 74},
    ],
    "camera": [
        {"name": "Sony Alpha a7 IV Full-Frame Mirrorless Camera",  "base_price": 2499.99, "img_seed": 80},
        {"name": "Canon EOS R6 Mark II Mirrorless Camera",         "base_price": 2499.99, "img_seed": 81},
        {"name": "Nikon Z6 III Full-Frame Mirrorless",             "base_price": 1999.99, "img_seed": 82},
        {"name": "Fujifilm X-T5 40MP APS-C Mirrorless",           "base_price": 1699.99, "img_seed": 83},
        {"name": "GoPro HERO12 Black Action Camera",               "base_price": 349.99,  "img_seed": 84},
    ],
    "watch": [
        {"name": "Apple Watch Ultra 2 49mm Titanium Case",         "base_price": 799.99,  "img_seed": 90},
        {"name": "Apple Watch Series 9 45mm GPS + Cellular",       "base_price": 499.99,  "img_seed": 91},
        {"name": "Samsung Galaxy Watch 6 Classic 47mm",            "base_price": 399.99,  "img_seed": 92},
        {"name": "Garmin Fenix 7X Pro Solar GPS Smartwatch",       "base_price": 899.99,  "img_seed": 93},
        {"name": "Fitbit Sense 2 Advanced Health Smartwatch",      "base_price": 249.99,  "img_seed": 94},
    ],
}

DEFAULT_TEMPLATES = [
    {"name": "{query} Premium Edition",             "base_price": 199.99,  "img_seed": 100},
    {"name": "{query} Pro Model 2024",              "base_price": 299.99,  "img_seed": 101},
    {"name": "{query} Standard Version",            "base_price": 99.99,   "img_seed": 102},
    {"name": "{query} Elite Bundle Pack",           "base_price": 399.99,  "img_seed": 103},
    {"name": "{query} Wireless Bluetooth Edition",  "base_price": 149.99,  "img_seed": 104},
    {"name": "{query} Smart Home Compatible",       "base_price": 249.99,  "img_seed": 105},
]

UNSPLASH_PHOTOS = {
    "iphone": [
        "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1598327105666-5b89351aff97?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1565849906660-4d693a7e559e?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1616348436168-de43ad0db179?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1510557880182-3d4d3cba35a5?q=80&w=400&h=400&fit=crop",
    ],
    "samsung": [
        "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1580910051074-3eb694886505?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1565630916779-e303be97b6f5?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1523206489230-c012c64b2b48?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1584006682522-dc17d6c0d9cb?q=80&w=400&h=400&fit=crop",
    ],
    "laptop": [
        "https://images.unsplash.com/photo-1496181130204-7552cc1534e0?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1531297484001-80022131f5a1?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1499951360447-b19be8fe80f5?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1603302576837-37561b2e2302?q=80&w=400&h=400&fit=crop",
    ],
    "headphones": [
        "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1546435770-a3e426bf472b?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1583394838336-acd977736f90?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1487215078519-e21cc028cb29?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?q=80&w=400&h=400&fit=crop",
    ],
    "gpu": [
        "https://images.unsplash.com/photo-1591488320449-011701bb6704?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1587202372775-e229f172b9d7?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1555680202-c86f0e12f086?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1614624532983-4ce03382d63d?q=80&w=400&h=400&fit=crop",
    ],
    "gaming": [
        "https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1605901309584-818e25960a8f?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1592840496694-26d035b52b48?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1550745165-9bc0b252726f?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1612287230202-1bf1d85d1bdf?q=80&w=400&h=400&fit=crop",
    ],
    "tv": [
        "https://images.unsplash.com/photo-1593305841991-05c297ba4575?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1552975084-6e027cd345c2?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1601944179066-297cbd3d10ff?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1593789198777-f29bc259780e?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1461151304267-38535e780c79?q=80&w=400&h=400&fit=crop",
    ],
    "camera": [
        "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1510127034890-ba27508e9f1c?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1495707902641-75cac588d2e9?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?q=80&w=400&h=400&fit=crop",
    ],
    "watch": [
        "https://images.unsplash.com/photo-1523275335684-37898b6baf30?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1542496658-e33a6d0d50f6?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1434494878577-86c23bcb06b9?q=80&w=400&h=400&fit=crop",
    ],
    "fallback": [
        "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1572635196237-14b3f281503f?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1542291026-7eec264c27ff?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1532298229144-0ec0c57515c7?q=80&w=400&h=400&fit=crop",
        "https://images.unsplash.com/photo-1559563458-527698bf5295?q=80&w=400&h=400&fit=crop",
    ]
}


def _get_templates(query: str):
    q = query.lower()
    for key, templates in PRODUCT_TEMPLATES.items():
        if key in q:
            return templates
    # Fall back to generic templates
    return [
        {**t, "name": t["name"].replace("{query}", query.title())}
        for t in DEFAULT_TEMPLATES
    ]


def _get_category(query: str) -> str:
    q = query.lower()
    for key in PRODUCT_TEMPLATES.keys():
        if key in q:
            return key
    return "fallback"


def _stable_hash(s: str) -> int:
    """Deterministic integer hash for seeding randomness per store+product."""
    h = 0
    for c in s:
        h = (h * 31 + ord(c)) & 0xFFFFFFFF
    return h


class MockProvider(BaseProvider):
    """
    Simulates product search results with realistic price fluctuations and
    stock status changes, enabling the change-detection engine to fire.
    """

    def search(self, query: str) -> List[ProductResult]:
        templates = _get_templates(query)
        category = _get_category(query)
        photos = UNSPLASH_PHOTOS.get(category, UNSPLASH_PHOTOS["fallback"])
        results: List[ProductResult] = []

        # Pick 6 random stores for this search
        selected_stores = random.sample(STORES, min(6, len(STORES)))

        for idx, store in enumerate(selected_stores):
            # Pick a product template (cycle through)
            template = templates[idx % len(templates)]

            # Deterministic base seed for this store + product combo
            combo_seed = _stable_hash(f"{query}:{store['name']}:{template['name']}")
            rng = random.Random(combo_seed)

            # Apply per-store price adjustment (±20% from base)
            store_factor = rng.uniform(0.82, 1.18)
            base_price = round(template["base_price"] * store_factor, 2)

            # Add live market noise (±5%) — varies each call via current minute
            live_seed = _stable_hash(f"{query}:{store['name']}:{int(time.time() // 300)}")
            live_rng = random.Random(live_seed)
            noise = live_rng.uniform(-0.05, 0.05)
            final_price = round(base_price * (1 + noise), 2)

            # Stock status — mostly in stock, 15% chance out of stock
            in_stock = live_rng.random() > 0.15

            # Rating — consistent per store+product
            rating = round(rng.uniform(3.6, 5.0), 1)
            review_count = rng.randint(42, 28000)

            # Build product URL
            url_code = str(abs(combo_seed))[:8]
            product_url = store["url"].replace("{code}", url_code)

            # Image from Unsplash category photos list
            img_url = photos[idx % len(photos)]

            results.append(ProductResult(
                product_name=template["name"],
                store_name=store["name"],
                price=final_price,
                currency="USD",
                in_stock=in_stock,
                rating=rating,
                review_count=review_count,
                image_url=img_url,
                product_url=product_url,
            ))

        return results
