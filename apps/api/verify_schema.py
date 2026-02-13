import asyncio
import sys
import logging
from app.services.discovery import SchemaDiscoveryService
from app.models import Base
from app.core.database import engine

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def verify_schema_discovery(url):
    print(f"🧠 Verifying Phase 1 (Schema Discovery) for: {url}")
    print("   (Using REAL database via SQLite)")
    
    # Ensure tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    try:
        service = SchemaDiscoveryService()
        print("   Running discovery (this may take a few seconds)...")
        schema = await service.discover_schema(url)
        
        print(f"\n✅ Schema Discovered:")
        import json
        print(json.dumps(schema, indent=2))
        
    except Exception as e:
        print(f"❌ Error during discovery: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://news.ycombinator.com"
    asyncio.run(verify_schema_discovery(url))
