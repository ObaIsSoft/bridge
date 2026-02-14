from playwright.async_api import async_playwright
import logging
from typing import List, Dict, Any, Optional
import json
logger = logging.getLogger(__name__)

from app.services.permissions import PermissionService
from app.core.database import AsyncSessionLocal
from app.services.interaction import InteractionService

class CrawlerService:

    async def get_page_content(
        self, 
        url: str, 
        auth_config: Optional[Dict[str, Any]] = None,
        interaction_script: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[str]:
        """Fetch rendered HTML from a URL using Playwright with optional Auth and Interactions"""
        # 1. Check Permissions
        async with AsyncSessionLocal() as db:
            perms = PermissionService()
            if not await perms.check_access(url, db):
                logger.warning(f"Crawling blocked for {url} by PermissionService")
                raise Exception("Access Denied by robots.txt or platform policy")
        
        interaction = InteractionService()

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            try:
                # Create context first to allow cookie injection
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
                )
                
                page = await context.new_page()
                
                # 2. Perform Auth (Cookies/Login) BEFORE Navigation (if cookie) or AFTER (if login flow)
                # But InteractionService.perform_auth handles the logic (cookies added to context)
                if auth_config:
                    await interaction.perform_auth(page, auth_config)

                logger.info(f"Crawling {url}...")
                await page.goto(url, wait_until="networkidle", timeout=30000)
                
                # 3. Execute Interaction Script (Click, Scroll, Wait)
                if interaction_script:
                    await interaction.perform_interaction(page, interaction_script)
                else:
                    # Default behavior if no script: Basic scroll
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
