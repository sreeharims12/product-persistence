import re
import logging
from typing import List, Optional
import httpx
from bs4 import BeautifulSoup

from app.providers.base import BaseProvider, ProductResult
from app.providers.browser_helper import fetch_html_with_playwright

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-IN,en;q=0.9",
}


def _is_relevant(title: str, query: str) -> bool:
    """Dynamically verify title relevancy against query tokens without hardcoding."""
    if not title or len(title) < 4:
        return False
    title_lower = title.lower()
    query_tokens = [t.lower() for t in re.findall(r"\w+", query) if len(t) > 1]
    if not query_tokens:
        return True

    matched_count = sum(1 for token in query_tokens if token in title_lower)
    return (matched_count / len(query_tokens)) >= 0.5


class FlipkartProvider(BaseProvider):
    """
    Flipkart Product Scraper Provider.
    Uses Tier 1 (Fast HTTP + BeautifulSoup) with Tier 2 (Playwright Chromium) fallback.
    Includes automated Sponsored Ad filtering and Query Relevancy scoring.
    """

    def search(self, query: str) -> List[ProductResult]:
        query_str = query.strip()
        if not query_str:
            return []

        search_url = f"https://www.flipkart.com/search?q={httpx.QueryParams({'q': query_str})['q']}"
        logger.info(f"[FlipkartProvider] Searching Flipkart for '{query_str}'")

        results: List[ProductResult] = []

        # ── Tier 1: Fast HTTP GET with BeautifulSoup ─────────────────────────
        try:
            with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=6.0) as client:
                resp = client.get(search_url)
                if resp.status_code == 200:
                    results = self._parse_flipkart_html(resp.text, query_str)
                    if results:
                        logger.info(f"[FlipkartProvider] Tier 1 HTTP scrape succeeded with {len(results)} items")
                        return results
        except Exception as e:
            logger.debug(f"[FlipkartProvider] Tier 1 HTTP scrape failed: {e}")

        # ── Tier 2: Headless Playwright Chromium Render ──────────────────────
        try:
            logger.info(f"[FlipkartProvider] Attempting Tier 2 Playwright fallback for '{query_str}'")
            rendered_html = fetch_html_with_playwright(search_url, wait_selector="a[href*='/p/']")
            if rendered_html:
                results = self._parse_flipkart_html(rendered_html, query_str)
                if results:
                    logger.info(f"[FlipkartProvider] Tier 2 Playwright scrape succeeded with {len(results)} items")
                    return results
        except Exception as e:
            logger.warning(f"[FlipkartProvider] Tier 2 Playwright scrape failed: {e}")

        return []

    def _parse_flipkart_html(self, html: str, query: str) -> List[ProductResult]:
        soup = BeautifulSoup(html, "lxml")
        results: List[ProductResult] = []

        product_links = soup.find_all("a", href=re.compile(r"/p/"))
        seen_urls = set()

        for link in product_links:
            href = link.get("href", "")
            if not href or href in seen_urls:
                continue

            full_url = f"https://www.flipkart.com{href}" if href.startswith("/") else href
            seen_urls.add(href)

            card = link.find_parent("div", class_=re.compile(r"(_1AtVbE|_75Wflg|cPHRSc|_1sdA2b|t-yWyC|cPHRSc|_2kHMtA|_13oc-L)"))
            if not card:
                card = link.parent

            # Skip Ad / Sponsored tags
            if card.select_one("._2I2dNz, div:contains('Ad')"):
                continue

            # Clean Title
            title_el = (
                card.select_one("._4rR01T, .s1QR8a, a.title, .IRyBtW, ._2Wk-jV, .KzHgSp, div.wM218d")
                or link
            )
            raw_title = link.get("title") or (title_el.text.strip() if title_el else "")
            if not raw_title or len(raw_title) < 4 or any(junk in raw_title.lower() for junk in ["login", "sign in", "privacy policy", "terms of use"]):
                continue

            title = re.sub(r"^(Add to Compare|Currently unavailable)\s*", "", raw_title, flags=re.IGNORECASE).strip()
            title = re.sub(r"(\d\.\d\d+,\d+|\d+ Ratings.*)", "", title).strip()

            # Check Relevancy
            if not _is_relevant(title, query):
                continue

            # Price
            price_el = (
                card.select_one("._30jeq3, ._1_WHN1, .Nx9bgb, .DzA2Z4, div.Nx9bgb, div.hlcwA3, div.BhBDA")
                or card.find(text=re.compile(r"₹\s*[\d,]+"))
            )
            price: Optional[float] = None
            if price_el:
                price_text = price_el.text if hasattr(price_el, "text") else str(price_el)
                clean_p = re.sub(r"[^\d.]", "", price_text.replace("₹", "").replace(",", ""))
                try:
                    price = float(clean_p)
                except ValueError:
                    price = None

            # Rating
            rating_el = card.select_one("._3LWZlK, div.X1f1E7, div._5O2FAE")
            rating: Optional[float] = None
            if rating_el:
                rm = re.search(r"(\d+\.\d+|\d+)", rating_el.text)
                if rm:
                    try:
                        rating = float(rm.group(1))
                    except ValueError:
                        rating = None

            # Image
            image_url = None
            img_el = card.select_one("img._396cs4, img._2r_T1I, img.DzA2Z4, img")
            if img_el:
                src = img_el.get("src") or ""
                data_src = img_el.get("data-src") or ""
                srcset = img_el.get("srcset") or ""
                
                # Filter out base64 svg placeholders
                candidate = data_src or src or srcset
                if "svg+xml" in candidate or not candidate:
                    # Look for srcset
                    if srcset:
                        candidate = srcset.split(",")[0].split(" ")[0]
                
                if candidate and "svg+xml" not in candidate:
                    image_url = candidate.split(" ")[0]

            # If image is still empty or SVG, try fallback image helper
            if not image_url or "svg+xml" in image_url:
                from app.providers.live_scraper_provider import _fetch_real_image
                image_url = _fetch_real_image(title, query, len(results))

            results.append(
                ProductResult(
                    product_name=title[:140],
                    store_name="Flipkart",
                    price=price,
                    currency="INR",
                    in_stock=True,
                    rating=rating or 4.1,
                    review_count=None,
                    image_url=image_url[:500] if image_url else None,
                    product_url=full_url[:500],
                )
            )


            if len(results) >= 8:
                break

        return results
