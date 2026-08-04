import random
import logging
from typing import List, Dict, Optional
import httpx

from .base import BaseProvider, ProductResult
from .mock_provider import MockProvider, STORES

logger = logging.getLogger(__name__)

DUMMYJSON_SEARCH_URL = "https://dummyjson.com/products/search"
DUMMYJSON_CATEGORY_URL = "https://dummyjson.com/products/category"

CATEGORY_ALIASES: Dict[str, str] = {
    "car": "vehicle", "auto": "vehicle", "vehicle": "vehicle", "parts": "vehicle", "engine": "vehicle", "tire": "vehicle",
    "motorcycle": "motorcycle", "bike": "motorcycle", "scooter": "motorcycle",
    "phone": "smartphones", "iphone": "smartphones", "mobile": "smartphones", "samsung": "smartphones",
    "laptop": "laptops", "macbook": "laptops", "pc": "laptops", "computer": "laptops",
    "shoe": "mens-shoes", "shoes": "mens-shoes", "sneaker": "mens-shoes",
    "bag": "womens-bags", "handbag": "womens-bags", "backpack": "womens-bags",
    "watch": "mens-watches", "smartwatch": "mens-watches",
    "sunglasses": "sunglasses", "glasses": "sunglasses",
    "furniture": "furniture", "chair": "furniture", "table": "furniture", "desk": "furniture",
    "shirt": "mens-shirts", "clothes": "mens-shirts", "clothing": "mens-shirts",
    "beauty": "beauty", "makeup": "beauty", "skincare": "skin-care",
    "perfume": "fragrances", "fragrance": "fragrances",
    "sports": "sports-accessories", "gym": "sports-accessories",
}

class DummyJsonProvider(BaseProvider):
    """
    Real-time product data provider fetching live items, titles, and photos from DummyJSON API.
    Features multi-level search (exact query -> category alias -> word tokenization -> dynamic keyword images).
    """

    def __init__(self):
        self.mock_fallback = MockProvider()

    def search(self, query: str) -> List[ProductResult]:
        query_str = query.strip()
        if not query_str:
            return []

        # 1. Exact query search
        products = self._fetch_search(query_str)
        if products:
            return self._map_dummyjson_products(query_str, products)

        # 2. Check category aliases (e.g., 'car parts' -> 'vehicle')
        words = query_str.lower().split()
        for word in words:
            if word in CATEGORY_ALIASES:
                cat_name = CATEGORY_ALIASES[word]
                products = self._fetch_category(cat_name)
                if products:
                    return self._map_dummyjson_products(query_str, products, title_prefix=f"{query_str.title()}: ")

        # 3. Individual word tokenization search
        for word in words:
            if len(word) >= 3:
                products = self._fetch_search(word)
                if products:
                    return self._map_dummyjson_products(query_str, products)

        # 4. Fallback to local MockProvider
        return self.mock_fallback.search(query_str)

    def _fetch_search(self, q: str) -> List[dict]:
        try:
            r = httpx.get(DUMMYJSON_SEARCH_URL, params={"q": q, "limit": 6}, timeout=4.0)
            if r.status_code == 200:
                return r.json().get("products", [])
        except Exception as e:
            logger.warning(f"[DummyJsonProvider] Search request failed for '{q}': {e}")
        return []

    def _fetch_category(self, category: str) -> List[dict]:
        try:
            r = httpx.get(f"{DUMMYJSON_CATEGORY_URL}/{category}", params={"limit": 6}, timeout=4.0)
            if r.status_code == 200:
                return r.json().get("products", [])
        except Exception as e:
            logger.warning(f"[DummyJsonProvider] Category request failed for '{category}': {e}")
        return []

    def _map_dummyjson_products(self, query: str, products: List[dict], title_prefix: str = "") -> List[ProductResult]:
        results: List[ProductResult] = []
        num_products = len(products)

        for idx, store in enumerate(STORES):
            p = products[idx % num_products]
            raw_title = p.get("title", query)
            title = f"{title_prefix}{raw_title}" if title_prefix else raw_title
            
            base_price = float(p.get("price", 99.99))
            
            # Minor store price variation (±5%)
            store_seed = (hash(store["name"] + title) % 100) / 1000.0
            price_multiplier = 0.95 + store_seed
            final_price = round(base_price * price_multiplier, 2)
            
            # Stock determination (allows testing restock & out-of-stock features)
            stock_qty = p.get("stock", 10)
            in_stock = stock_qty > 0 and (idx % 4 != 3)

            images = p.get("images", [])
            image_url = p.get("thumbnail") or (images[0] if images else None)

            rating = float(p.get("rating", 4.5))
            review_count = int(rating * 120 + (idx * 45))
            code = str(p.get("id", idx + 100))

            results.append(
                ProductResult(
                    product_name=title,
                    store_name=store["name"],
                    price=final_price,
                    currency="USD",
                    in_stock=in_stock,
                    rating=rating,
                    review_count=review_count,
                    image_url=image_url,
                    product_url=store["url"].format(code=code),
                )
            )

        return results
