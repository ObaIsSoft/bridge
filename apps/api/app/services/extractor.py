import json
import logging
from typing import Any, Dict
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.llm import get_llm_for_user

logger = logging.getLogger(__name__)

class ExtractionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def extract_structured_data(
        self,
        html: str, 
        schema: Dict[str, Any],
        user_id: UUID
    ) -> Dict[str, Any]:
        """Use LLM to extract data from HTML based on a JSON schema"""
        prompt = f"""
        Extract data from the following HTML into a JSON object matching this schema:
        {json.dumps(schema, indent=2)}

        HTML Content (truncated):
        {html[:15000]} # Truncated to stay within context limits

        Return ONLY the raw JSON object. Do not include markdown formatting.
        """

        try:
            # Get LLM provider with automatic failover
            provider = await get_llm_for_user(user_id, self.db)
            
            response = await provider.complete(
                messages=[
                    {"role": "system", "content": "You are a specialized data extraction agent. You only output valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0,
                response_format="json"
            )
            
            result = json.loads(response)
            return result
        except Exception as e:
            logger.error(f"Error during LLM extraction: {e}")
            return {"error": str(e)}
