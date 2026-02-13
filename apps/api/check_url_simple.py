import asyncio
import sys
from app.services.permissions import PermissionService

async def check_url_simple(url):
    print(f"🛡️ Checking Ethical Moat for: {url} (Playwright Enabled)")
    
    service = PermissionService()
    from urllib.parse import urlparse
    domain = urlparse(url).netloc
    
    print(f"   Fetching permissions for domain: {domain}...")
    try:
        # Unpack the new 6th return value (socials)
        is_allowed, crawl_delay, contact, robots_content, security_content, socials = await service._fetch_permissions(domain)
        
        print(f"\n✅ Result for {domain}:")
        print(f"   - Permission: {'ALLOWED' if is_allowed else 'DENIED'}")
        print(f"   - Contact Email: {contact or 'None found'}")
        print(f"   - Socials:")
        print(f"     • Twitter:  {socials.get('twitter') or 'None'}")
        print(f"     • GitHub:   {socials.get('github') or 'None'}")
        print(f"     • LinkedIn: {socials.get('linkedin') or 'None'}")
        print(f"   - Robots.txt found: {'Yes' if robots_content else 'No'}")
        print(f"   - Security.txt found: {'Yes' if security_content else 'No'}")
            
    except Exception as e:
        print(f"❌ Error fetching permissions: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://obafemiadebayo.vercel.app"
    asyncio.run(check_url_simple(url))
