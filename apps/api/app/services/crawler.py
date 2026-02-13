from playwright.async_api import async_playwright
import logging
from typing import List, Dict, Any, Optional
import json
logger = logging.getLogger(__name__)

from app.services.permissions import PermissionService
from app.core.database import AsyncSessionLocal

class CrawlerService:
    async def get_page_content(self, url: str) -> Optional[str]:
        """Fetch rendered HTML from a URL using Playwright"""
        # 1. Check Permissions
        async with AsyncSessionLocal() as db:
            perms = PermissionService()
            if not await perms.check_access(url, db):
                logger.warning(f"Crawling blocked for {url} by PermissionService")
                raise Exception("Access Denied by robots.txt or platform policy")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            try:
                page = await browser.new_page()
                # Set a common user agent to avoid basic blocks
                await page.set_extra_http_headers({
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                })
                
                logger.info(f"Crawling {url}...")
                await page.goto(url, wait_until="networkidle", timeout=30000)
                
                # Basic scroll to trigger lazy loading
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await page.wait_for_timeout(2000)
                
                content = await page.content()
                return content
            except Exception as e:
                logger.error(f"Error crawling {url}: {e}")
                return None
            finally:
                await browser.close()

    async def get_visual_elements(self, url: str) -> List[Dict[str, Any]]:
        """Identify interactive and structural elements to assist in schema creation"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            try:
                page = await browser.new_page()
                await page.goto(url, wait_until="networkidle", timeout=30000)
                
                # Extract interesting elements
                elements = await page.evaluate("""() => {
                    const selectors = ['a', 'button', 'h1', 'h2', 'h3', '.title', '.price', 'article'];
                    const results = [];
                    selectors.forEach(sel => {
                        document.querySelectorAll(sel).forEach(el => {
                            if (el.innerText.trim().length > 0) {
                                results.push({
                                    tag: el.tagName.toLowerCase(),
                                    text: el.innerText.trim().substring(0, 50),
                                    selector: sel,
                                    path: el.id ? `#${el.id}` : `${el.tagName.toLowerCase()}.${el.className.split(' ').join('.')}`
                                });
                            }
                        });
                    });
                    return results.slice(0, 50); // Limit to top 50
                }""")
                return elements
            except Exception as e:
                logger.error(f"Error getting visual elements for {url}: {e}")
                return []
            finally:
                await browser.close()
