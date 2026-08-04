from typing import List
from app.providers.base import ProductResult
from app.providers.amazon_provider import AmazonProvider
from app.providers.flipkart_provider import FlipkartProvider
from app.providers.live_scraper_provider import LiveScraperProvider

# Registry of active e-commerce providers
_providers = [
    AmazonProvider(),
    FlipkartProvider(),
    LiveScraperProvider(),
]


def search_products(query: str) -> List[ProductResult]:
    """Search all registered providers and return aggregated results."""
    results: List[ProductResult] = []
    for provider in _providers:
        try:
            res = provider.search(query)
            if res:
                results.extend(res)
        except Exception as e:
            print(f"[ProductSearch] Provider {type(provider).__name__} failed: {e}")
    return results

