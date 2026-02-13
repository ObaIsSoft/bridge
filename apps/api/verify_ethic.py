import asyncio
import sys
from app.services.permissions import PermissionService
from app.core.database import AsyncSessionLocal
from app.models import Base
from app.core.database import engine

async def verify_permissions(url):
    print(f"🛡️ Verifying Ethical Moat for: {url}")
    
    # 1. Init DB tables (since we added a new one without migration)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 2. Check Permissions
    service = PermissionService()
    
    async with AsyncSessionLocal() as db:
        print("   Checking robots.txt & security.txt...")
        allowed = await service.check_access(url, db)
        
        # 3. Read back from DB to confirm data capture
        domain = service._get_domain(url)
        from app.models import DomainPermission
        permission = await db.get(DomainPermission, domain)
        
        if permission:
            print(f"\n✅ Result for {domain}:")
            print(f"   - Permission: {'ALLOWED' if allowed else 'DENIED'}")
            print(f"   - Contact: {permission.contact_email or 'Not Found'}")
            print(f"   - Robots.txt Cached: {'Yes' if permission.robots_txt else 'No'}")
            print(f"   - Security.txt Cached: {'Yes' if permission.security_txt else 'No'}")
        else:
            print("❌ Failed to save permission record.")

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://obafemiadebayo.vercel.app"
    asyncio.run(verify_permissions(url))
