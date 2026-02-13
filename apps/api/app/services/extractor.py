import openai
import json
import logging
from typing import Any, Dict
from app.core.config import settings

logger = logging.getLogger(__name__)

class ExtractionService:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.openai_api_key)

    async def extract_structured_data(self, html: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Use LLM to extract data from HTML based on a JSON schema"""
        prompt = f"""
        Extract data from the following HTML into a JSON object matching this schema:
        {json.dumps(schema, indent=2)}

        HTML Content (truncated):
        {html[:15000]} # Truncated to stay within context limits

        Return ONLY the raw JSON object. Do not include markdown formatting.
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a specialized data extraction agent. You only output valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            logger.error(f"Error during LLM extraction: {e}")
            return {"error": str(e)}
