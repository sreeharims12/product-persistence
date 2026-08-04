from typing import List
from app.providers.live_scraper_provider import LiveScraperProvider
from app.providers.base import ProductResult

# Registry of active providers
_providers = [LiveScraperProvider()]


def search_products(query: str) -> List[ProductResult]:
    """Search all registered providers and return aggregated results."""
    results: List[ProductResult] = []
    for provider in _providers:
        try:
            results.extend(provider.search(query))
        except Exception as e:
            print(f"[ProductSearch] Provider {type(provider).__name__} failed: {e}")
    return results
