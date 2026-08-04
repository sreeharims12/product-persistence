import logging
from typing import Optional
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError

logger = logging.getLogger(__name__)

# Stealth Chrome User Agent
DEFAULT_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"


def fetch_html_with_playwright(url: str, wait_selector: Optional[str] = None, timeout_ms: int = 12000) -> str:
    """
    Renders dynamic Client-Side Rendered (CSR) JavaScript web pages using a headless Chromium browser.
    Blocks media assets (images, fonts) to maximize performance and speed.
    """
    logger.info(f"[Playwright] Rendering URL in headless Chromium: {url}")
    html_content = ""

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--disable-infobars",
                ]
            )

            context = browser.new_context(
                user_agent=DEFAULT_UA,
                viewport={"width": 1280, "height": 800},
                locale="en-US,en;q=0.9",
            )

            # Extra stealth scripts to bypass navigator.webdriver detection
            context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
            """)

            page = context.new_page()

            # Abort media requests to speed up page load
            def handle_route(route):
                if route.request.resource_type in ["image", "media", "font", "stylesheet"]:
                    route.abort()
                else:
                    route.continue_()

            try:
                page.route("**/*", handle_route)
            except Exception:
                pass

            try:
                page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
                if wait_selector:
                    page.wait_for_selector(wait_selector, timeout=5000)
                else:
                    page.wait_for_timeout(2000)

                html_content = page.content()
            except PlaywrightTimeoutError:
                logger.warning(f"[Playwright] Page load timed out for {url}, returning partial content.")
                html_content = page.content()
            except Exception as e:
                logger.error(f"[Playwright] Failed to load {url}: {e}")

            browser.close()
    except Exception as e:
        logger.error(f"[Playwright] Engine failure for {url}: {e}")

    return html_content
