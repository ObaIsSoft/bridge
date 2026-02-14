
import logging
from typing import List, Dict, Any, Optional
from playwright.async_api import Page
import asyncio

logger = logging.getLogger(__name__)

class InteractionService:
    async def perform_interaction(self, page: Page, script: List[Dict[str, Any]]):
        """
        Executes a sequence of actions on the page.
        Script Format: [ {"action": "click", "selector": "#btn"}, {"action": "wait", "ms": 2000} ]
        """
        if not script:
            return

        logger.info(f"Executing interaction script with {len(script)} steps")
        
        for step in script:
            action = step.get("action")
            selector = step.get("selector")
            
            try:
                if action == "click":
                    logger.info(f"Clicking: {selector}")
                    await page.click(selector, timeout=5000)
                
                elif action == "type":
                    text = step.get("text", "")
                    logger.info(f"Typing into {selector}")
                    await page.fill(selector, text, timeout=5000)
                
                elif action == "scroll_bottom":
                    logger.info("Scrolling to bottom")
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                
                elif action == "wait":
                    ms = step.get("ms", 1000)
                    logger.info(f"Waiting {ms}ms")
                    await page.wait_for_timeout(ms)
                
                elif action == "wait_for_selector":
                    logger.info(f"Waiting for selector: {selector}")
                    await page.wait_for_selector(selector, timeout=10000)

                elif action == "screenshot":
                    # Debugging only
                    logger.info("Taking debug screenshot")
                    await page.screenshot(path="debug_interaction.png")

                # Small pause between actions to be human-like
                await page.wait_for_timeout(500)
                
            except Exception as e:
                logger.error(f"Error executing step {step}: {e}")
                # We log but continue, or should we abort?
                # For now, continue best effort.

    async def inject_session_data(self, page: Page, session_data: Dict[str, Any]):
        """Restores cookies and local storage from saved session data."""
        if not session_data:
            return

        cookies = session_data.get("cookies", [])
        if cookies:
            logger.info(f"Restoring {len(cookies)} session cookies")
            await page.context.add_cookies(cookies)
        
        # LocalStorage injection requires being on the domain, so we might need a dummy navigation
        # or handle it after initial goto. For now, focusing on cookies.

    async def capture_session_data(self, page: Page) -> Dict[str, Any]:
        """Captures current cookies and storage to save session state."""
        cookies = await page.context.cookies()
        logger.info(f"Captured {len(cookies)} session cookies")
        
        return {
            "cookies": cookies,
            "timestamp": "iso-now" # TODO: Add real timestamp
        }

    async def perform_auth(self, page: Page, auth_config: Dict[str, Any]):
        """
        Handles authentication before extraction.
        Config Format: { "type": "cookie", "cookies": [...] }
        """
        if not auth_config:
            return

        auth_type = auth_config.get("type")
        
        if auth_type == "cookie":
            cookies = auth_config.get("cookies", [])
            logger.info(f"Injecting {len(cookies)} config cookies")
            await page.context.add_cookies(cookies)
            try:
                await page.reload()
            except:
                pass

        elif auth_type == "login_flow":
            # Complex login flow defined as interaction steps
            steps = auth_config.get("steps", [])
            logger.info("Executing Login Flow")
            await self.perform_interaction(page, steps)
            # Wait for navigation/redirect
            await page.wait_for_load_state("networkidle")

