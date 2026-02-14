
import asyncio
import logging
from app.services.crawler import CrawlerService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_interaction():
    crawler = CrawlerService()
    url = "https://example.com"
    
    # Script: Click the "More information..." link
    # Selector for the link is 'a'
    script = [
        {"action": "wait_for_selector", "selector": "a"},
        {"action": "click", "selector": "a"},
        {"action": "wait", "ms": 2000} # Wait for nav
    ]
    
    logger.info(f"Testing interaction on {url} with script: {script}")
    
    try:
        content = await crawler.get_page_content(url, interaction_script=script)
        
        if content and "IANA-managed Reserved Domains" in content:
            logger.info("SUCCESS: Interaction navigation worked! Found credentials of destination page.")
        else:
            logger.error("FAILURE: Content did not change or expected text not found.")
            if content:
                logger.info(f"Content preview: {content[:200]}")
    except Exception as e:
        logger.error(f"Test failed with error: {e}")

if __name__ == "__main__":
    asyncio.run(test_interaction())
