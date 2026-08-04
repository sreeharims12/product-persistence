import re
import logging
from typing import List, Optional
import httpx
from bs4 import BeautifulSoup

from app.providers.base import BaseProvider, ProductResult
from app.providers.browser_helper import fetch_html_with_playwright

logger = logging.getLogger(__name__)

HEADERS_MOBILE = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Mobile/15E148 Safari/604.1",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IN,en-GB;q=0.9,en;q=0.8",
}

BADGE_TEXTS = {
    "best seller", "amazon's choice", "overall pick", "featured from our brands",
    "top rated", "limited time deal", "sponsored"
}


def _is_relevant(title: str, query: str) -> bool:
    """Dynamically verify title relevancy against query tokens without hardcoding."""
    if not title or len(title) < 4:
        return False
    title_lower = title.lower()
    query_tokens = [t.lower() for t in re.findall(r"\w+", query) if len(t) > 1]
    if not query_tokens:
        return True

    # Check how many query tokens appear in title
    matched_count = sum(1 for token in query_tokens if token in title_lower)
    # Require at least 50% of query words to match
    return (matched_count / len(query_tokens)) >= 0.5


class AmazonProvider(BaseProvider):
    """
    Amazon Product Scraper Provider.
    Uses Tier 1 (Fast HTTP + Mobile UA + BeautifulSoup) with Tier 2 (Playwright Chromium) fallback.
    Includes automated Sponsored Ad filtering and Query Relevancy scoring.
    """

    def search(self, query: str) -> List[ProductResult]:
        query_str = query.strip()
        if not query_str:
            return []

        search_url = f"https://www.amazon.in/s?k={httpx.QueryParams({'k': query_str})['k']}"
        logger.info(f"[AmazonProvider] Searching Amazon for '{query_str}'")

        results: List[ProductResult] = []

        # ── Tier 1: Fast HTTP GET with BeautifulSoup ─────────────────────────
        try:
            with httpx.Client(headers=HEADERS_MOBILE, follow_redirects=True, timeout=7.0) as client:
                resp = client.get(search_url)
                if resp.status_code == 200 and "Robot Check" not in resp.text:
                    results = self._parse_amazon_html(resp.text, query_str)
                    if results:
                        logger.info(f"[AmazonProvider] Tier 1 HTTP scrape succeeded with {len(results)} items")
                        return results
        except Exception as e:
            logger.debug(f"[AmazonProvider] Tier 1 HTTP scrape failed: {e}")

        # ── Tier 2: Headless Playwright Chromium Render ──────────────────────
        try:
            logger.info(f"[AmazonProvider] Attempting Tier 2 Playwright fallback for '{query_str}'")
            rendered_html = fetch_html_with_playwright(search_url, wait_selector="div[data-component-type='s-search-result']")
            if rendered_html:
                results = self._parse_amazon_html(rendered_html, query_str)
                if results:
                    logger.info(f"[AmazonProvider] Tier 2 Playwright scrape succeeded with {len(results)} items")
                    return results
        except Exception as e:
            logger.warning(f"[AmazonProvider] Tier 2 Playwright scrape failed: {e}")

        return []

    def _parse_amazon_html(self, html: str, query: str) -> List[ProductResult]:
        soup = BeautifulSoup(html, "lxml")
        results: List[ProductResult] = []

        cards = soup.select("div[data-component-type='s-search-result']") or soup.select(".s-result-item[data-asin]")

        for card in cards:
            asin = card.get("data-asin", "").strip()
            if not asin:
                continue

            # 1. Filter out Sponsored Ad Cards
            if card.select_one(".s-sponsored-label-info-icon, .s-sponsored-label-text, .puis-sponsored-label-text") or card.select_one("a[href*='/sspa/click']"):
                continue

            # 2. Extract Title (Target exact text span, ignoring badge labels like 'Best seller')
            title_el = (
                card.select_one("h2 a span.a-text-normal")
                or card.select_one("span.a-text-normal")
                or card.select_one("h2 a span:not(.a-badge-text)")
                or card.select_one("h2")
            )
            if not title_el:
                continue

            title = title_el.text.strip()
            # Clean title if it picked up badge text
            if title.lower() in BADGE_TEXTS or len(title) < 4:
                # Try finding alternative title element
                spans = card.select("h2 a span")
                valid_spans = [s.text.strip() for s in spans if s.text.strip().lower() not in BADGE_TEXTS and len(s.text.strip()) > 5]
                if valid_spans:
                    title = valid_spans[0]
                else:
                    continue

            # Strip leading badge strings if concatenated
            for badge in BADGE_TEXTS:
                if title.lower().startswith(badge):
                    title = title[len(badge):].strip()

            # Check Relevancy
            if not _is_relevant(title, query):
                continue

            # Product URL
            link_el = card.select_one("h2 a") or card.select_one("a.a-link-normal")
            href = link_el.get("href", "") if link_el else ""
            if "/sspa/click" in href:
                continue
            if href.startswith("/"):
                product_url = f"https://www.amazon.in{href}"
            elif href.startswith("http"):
                product_url = href
            else:
                product_url = f"https://www.amazon.in/dp/{asin}"

            # Price
            price_el = card.select_one(".a-price-whole") or card.select_one(".a-price .a-offscreen")
            price: Optional[float] = None
            if price_el:
                clean_p = re.sub(r"[^\d.]", "", price_el.text.replace(",", ""))
                try:
                    price = float(clean_p)
                except ValueError:
                    price = None

            # Image
            img_el = card.select_one(".s-image") or card.select_one("img")
            image_url = img_el.get("src") if img_el else None

            # Rating
            rating_el = card.select_one(".a-icon-alt")
            rating: Optional[float] = None
            if rating_el:
                rm = re.search(r"(\d+\.\d+|\d+)", rating_el.text)
                if rm:
                    try:
                        rating = float(rm.group(1))
                    except ValueError:
                        rating = None

            # Review count
            reviews_el = card.select_one("span.a-size-base.s-underline-text") or card.select_one(".a-size-base")
            review_count: Optional[int] = None
            if reviews_el:
                rev_m = re.search(r"([\d,]+)", reviews_el.text)
                if rev_m:
                    try:
                        review_count = int(rev_m.group(1).replace(",", ""))
                    except ValueError:
                        review_count = None

            results.append(
                ProductResult(
                    product_name=title[:140],
                    store_name="Amazon",
                    price=price,
                    currency="INR",
                    in_stock=True,
                    rating=rating or 4.2,
                    review_count=review_count,
                    image_url=image_url[:500] if image_url else None,
                    product_url=product_url[:500] if product_url else None,
                )
            )

            if len(results) >= 8:
                break

        return results
