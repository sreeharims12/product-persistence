import sys
import os

# Set UTF-8 encoding for Windows console output
sys.stdout.reconfigure(encoding='utf-8')

# Ensure backend root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.providers.amazon_provider import AmazonProvider
from app.providers.flipkart_provider import FlipkartProvider
from app.services.product_search import search_products

def main():
    print("=" * 70)
    print(" TESTING HYBRID E-COMMERCE PRODUCT SCRAPERS ")
    print("=" * 70)

    query = "study table"

    print(f"\nSearching for: '{query}'\n")

    print("[1] Testing AmazonProvider directly...")
    amazon = AmazonProvider()
    amazon_results = amazon.search(query)
    print(f"-> Amazon returned {len(amazon_results)} products:")
    for idx, item in enumerate(amazon_results[:3]):
        print(f"   [{idx+1}] {item.product_name}")
        print(f"       Price: {item.currency} {item.price} | Store: {item.store_name} | Rating: {item.rating}")
        print(f"       Image: {item.image_url[:60] if item.image_url else 'None'}")
        print(f"       URL:   {item.product_url[:60] if item.product_url else 'None'}")

    print("\n[2] Testing FlipkartProvider directly...")
    flipkart = FlipkartProvider()
    flipkart_results = flipkart.search(query)
    print(f"-> Flipkart returned {len(flipkart_results)} products:")
    for idx, item in enumerate(flipkart_results[:3]):
        print(f"   [{idx+1}] {item.product_name}")
        print(f"       Price: {item.currency} {item.price} | Store: {item.store_name} | Rating: {item.rating}")
        print(f"       Image: {item.image_url[:60] if item.image_url else 'None'}")
        print(f"       URL:   {item.product_url[:60] if item.product_url else 'None'}")

    print("\n[3] Testing Aggregated search_products()...")
    total_results = search_products(query)
    print(f"-> Total aggregated products across all providers: {len(total_results)}")

if __name__ == "__main__":
    main()
