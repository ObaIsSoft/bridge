#!/usr/bin/env python3
import asyncio
import argparse
import logging
import json
import sys
from typing import Dict, Any

# Ensure project root is in path
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import AsyncSessionLocal
from app.services.permissions import PermissionService
from app.models import DomainPermission
from sqlalchemy import delete, select

# Configure logging
logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger("scan_domain")

async def main():
    parser = argparse.ArgumentParser(description="Bridge.dev Domain Scanner & Permission Checker")
    parser.add_argument("url", help="Target URL to scan (e.g., https://example.com)")
    parser.add_argument("-f", "--force", action="store_true", help="Force refresh (ignore/clear cache)")
    parser.add_argument("-j", "--json", action="store_true", help="Output results as JSON")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose debug logging")
    
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger("app.services.permissions").setLevel(logging.INFO)
        logger.setLevel(logging.INFO)

    result_data: Dict[str, Any] = {
        "url": args.url,
        "domain": "",
        "status": "UNKNOWN",
        "contacts": {},
        "meta": {}
    }

    try:
        async with AsyncSessionLocal() as db:
            service = PermissionService()
            domain = service._get_domain(args.url)
            result_data["domain"] = domain

            # 1. Clear Cache if Requested
            if args.force:
                if not args.json:
                    print(f"🧹 Clearing cache for {domain}...")
                await db.execute(delete(DomainPermission).where(DomainPermission.domain == domain))
                await db.commit()

            # 2. Check Access (This triggers the scrape if not cached)
            if not args.json:
                print(f"🕵️  Scanning {domain}...")
            
            is_allowed = await service.check_access(args.url, db)
            
            # 3. Retrieve Result from DB
            stmt = select(DomainPermission).where(DomainPermission.domain == domain)
            result = await db.execute(stmt)
            permission = result.scalars().first()

            if permission:
                result_data["status"] = permission.status
                result_data["allowed"] = (permission.status == "ALLOWED")
                result_data["contacts"] = {
                    "email": permission.contact_email,
                    "twitter": permission.twitter_handle,
                    "github": permission.github_handle,
                    "linkedin": permission.linkedin_handle
                }
                result_data["meta"] = {
                    "robots_txt": bool(permission.robots_txt),
                    "security_txt": bool(permission.security_txt),
                    "crawl_delay": permission.crawl_delay,
                    "last_checked": permission.last_checked.isoformat() if permission.last_checked else None
                }
            else:
                result_data["error"] = "Failed to persist permission record"

    except Exception as e:
        result_data["status"] = "ERROR"
        result_data["error"] = str(e)
        if not args.json:
            logger.exception("Scan failed")

    # 4. Output
    if args.json:
        print(json.dumps(result_data, indent=2))
    else:
        print_rich_output(result_data)

def print_rich_output(data):
    print("\n" + "="*60)
    print(f"🛡️  Security & Contact Scan: {data['url']}")
    print("="*60)
    
    if data.get("error"):
        print(f"❌ Error: {data['error']}")
        return

    status_icon = "✅" if data.get("allowed") else "Mw"
    print(f"\n{status_icon} Permission: {data['status']}")
    
    contacts = data.get("contacts", {})
    print(f"\n📬 Discovered Contacts:")
    print(f"   • Email:    {contacts.get('email') or 'None'}")
    print(f"   • Twitter:  {contacts.get('twitter') or 'None'}")
    print(f"   • GitHub:   {contacts.get('github') or 'None'}")
    print(f"   • LinkedIn: {contacts.get('linkedin') or 'None'}")
    
    meta = data.get("meta", {})
    print(f"\n🤖 Meta:")
    print(f"   • Crawler:  {'Allowed' if data.get('allowed') else 'Blocked'}")
    print(f"   • Delay:    {meta.get('crawl_delay')}s")
    print(f"   • Robots:   {'Found' if meta.get('robots_txt') else 'Missing'}")
    print(f"   • Security: {'Found' if meta.get('security_txt') else 'Missing'}")
    print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nCancelled.")
