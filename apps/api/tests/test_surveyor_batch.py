
import asyncio
from app.services.discovery import SchemaDiscoveryService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_batch_test():
    service = SchemaDiscoveryService()
    
    # List of domains with known APIs or interesting structures
    targets = [
        "https://stripe.com",       # docs.stripe.com
        "https://twilio.com",       # www.twilio.com/docs
        "https://slack.com",        # api.slack.com
        "https://twitter.com",      # developer.twitter.com
        "https://reddit.com",       # www.reddit.com/dev/api
        "https://discord.com",      # discord.com/developers
        "https://ghibliapi.vercel.app", # Direct API URL
        "https://pokeapi.co",       # Direct API URL
        "https://openai.com",       # platform.openai.com
        "https://www.notion.so"     # developers.notion.com
    ]

    print(f"{'DOMAIN':<30} | {'DETECTED':<10} | {'CANDIDATES'}")
    print("-" * 80)

    for url in targets:
        try:
            result = await service.detect_official_api(url)
            detected = "YES" if result["official_api_detected"] else "NO"
            candidates = ", ".join(result["candidates"][:2]) + ("..." if len(result["candidates"]) > 2 else "")
            print(f"{url:<30} | {detected:<10} | {candidates}")
        except Exception as e:
            print(f"{url:<30} | ERROR      | {e}")

if __name__ == "__main__":
    asyncio.run(run_batch_test())
