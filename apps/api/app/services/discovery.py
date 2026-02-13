import json
import logging
from typing import Dict, Any, Optional
import openai
from app.core.config import settings
from app.services.crawler import CrawlerService

logger = logging.getLogger(__name__)

class SchemaDiscoveryService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)
        self.crawler = CrawlerService()

    async def discover_schema(self, url: str) -> Dict[str, Any]:
        """
        Analyzes a URL and suggests a JSON schema for extraction.
        """
        # 1. Crawl the page to get a sample
        # We use the existing crawler but might want to limit content size or use a specific strategy
        html_content = await self.crawler.get_page_content(url)
        
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
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a data architect. Output only valid JSON representing a flat extraction schema."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            logger.error(f"Error during schema discovery: {e}")
            raise e
