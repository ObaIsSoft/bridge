import json
import logging
from typing import Dict, Any, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.llm import get_llm_for_user
from app.services.crawler import CrawlerService

logger = logging.getLogger(__name__)

class SchemaDiscoveryService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.crawler = CrawlerService()

    async def discover_schema(self, url: str, user_id: UUID) -> Dict[str, Any]:
        """
        Analyzes a URL and suggests a JSON schema for extraction.
        """
        # 1. Crawl the page to get a sample
        # We use the existing crawler but might want to limit content size or use a specific strategy
        html_content, _ = await self.crawler.get_page_content(url)
        
        if not html_content:
            logger.error(f"Failed to crawl {url} for schema discovery")
            raise Exception("Failed to access URL")

        # 2. Distill/Clean HTML (Naive truncation for now, to be improved in Phase 1.3)
        # TODO: Use readability/DOM distiller here
        truncated_html = html_content[:20000] 

        # 3. Ask LLM to infer schema
        prompt = f"""
        Analyze the following HTML content from {url} and suggest a JSON schema that represents the main data on this page.
        
        Focus on the "primary entity" of the page. 
        - If it's a list (e.g. products, articles), return a schema for the list items.
        - If it's a detail page, return a schema for the single entity.
        
        HTML Content (truncated):
        {truncated_html}
        
        Return ONLY a JSON object complying with JSON Schema standard (or a simplified version compatible with our system).
        Example format:
        {{
            "title": "string",
            "price": "number",
            "description": "string"
        }}
        """

        try:
            # Get LLM provider with automatic failover
            provider = await get_llm_for_user(user_id, self.db)
            
            response = await provider.complete(
                messages=[
                    {"role": "system", "content": "You are a data architect. Output only valid JSON representing a flat extraction schema."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                response_format="json"
            )
            
            result = json.loads(response)
            return result
        except Exception as e:
            logger.error(f"Error during schema discovery: {e}")
            raise e

    async def detect_official_api(self, url: str) -> Dict[str, Any]:
        """
        Surveyor: Detects if an official API exists for the target URL.
        """
        import tldextract
        import aiohttp
        
        extracted = tldextract.extract(url)
        domain = f"{extracted.domain}.{extracted.suffix}"
        
        candidates = [
            f"https://api.{domain}",
            f"https://developer.{domain}",
            f"https://dev.{domain}",
            f"https://docs.{domain}",
            f"https://portal.{domain}",
            f"https://platform.{domain}",
            f"https://www.{domain}/developer",
            f"https://www.{domain}/developers",
            f"https://www.{domain}/docs",
            f"https://www.{domain}/api",
            f"https://{domain}/.well-known/openapi.json",
            f"https://{domain}/swagger.json",
            f"https://{domain}/api/docs"
        ]
        
        found_apis = []
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        # Specific subdomains where a 403 usually means "It exists but is locked" (Strong signal)
        strong_subdomains = ["api", "developer", "dev"]

        timeout = aiohttp.ClientTimeout(total=5)
        conn = aiohttp.TCPConnector(limit=10, ssl=False) # Disable SSL verification for speed/compat

        async with aiohttp.ClientSession(headers=headers, timeout=timeout, connector=conn) as session:
            for candidate in candidates:
                try:
                    # Switch to GET, but only read headers first
                    async with session.get(candidate, allow_redirects=True) as resp:
                        is_strong = any(s in candidate for s in strong_subdomains)
                        
                        # Accept 2xx/3xx OR 403 if it's a strong subdomain
                        if resp.status < 400 or (resp.status == 403 and is_strong):
                            found_apis.append(str(resp.url))
                        else:
                            logger.info(f"Candidate {candidate} returned status {resp.status}")
                except Exception as e:
                    # Ignore connection errors, but log them
                    logger.debug(f"Failed to check {candidate}: {e}")
                    continue
                    
        return {
            "official_api_detected": len(found_apis) > 0,
            "candidates": found_apis,
            "recommendation": "Use Official API" if found_apis else "Proceed with Bridge"
        }
