import urllib.robotparser
import httpx
import logging
import re
from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import DomainPermission
from app.core.database import AsyncSessionLocal

logger = logging.getLogger(__name__)

class PermissionService:
    def __init__(self):
        self.user_agent = "BridgeBot/1.0 (+https://bridge.dev/bot)"

    async def check_access(self, url: str, db: AsyncSession) -> bool:
        """
        Check if we are allowed to scrape the given URL.
        Returns True if allowed, False otherwise.
        Same logic applies to 'crawl-delay' (not fully enforced here yet, just status).
        """
        domain = self._get_domain(url)
        
        # 1. Check Cache
        permission = await db.get(DomainPermission, domain)
        if permission:
            # Refresh if older than 24h
            if permission.last_checked > datetime.utcnow() - timedelta(hours=24):
                if permission.status == "DENIED":
                    logger.warning(f"Access denied for {url} by cached policy")
                    return False
                return True

        # 2. Fetch & Parse real implementation
        is_allowed, crawl_delay, contact, robots_content, security_content = await self._fetch_permissions(domain)
        
        # 3. Update/Create DB Record
        status = "ALLOWED" if is_allowed else "DENIED"
        
        if permission:
            permission.status = status
            permission.crawl_delay = crawl_delay
            permission.contact_email = contact
            permission.robots_txt = robots_content
            permission.security_txt = security_content
            permission.last_checked = datetime.utcnow()
        else:
            permission = DomainPermission(
                domain=domain,
                status=status,
                crawl_delay=crawl_delay,
                contact_email=contact,
                robots_txt=robots_content,
                security_txt=security_content,
                last_checked=datetime.utcnow()
            )
            db.add(permission)
        
        await db.commit()
        
        if not is_allowed:
            logger.warning(f"Access DENIED for {url} by robots.txt")
            return False
            
        return True

    def _get_domain(self, url: str) -> str:
        from urllib.parse import urlparse
        return urlparse(url).netloc

    async def _fetch_permissions(self, domain: str) -> Tuple[bool, int, Optional[str], Optional[str], Optional[str]]:
        robots_url = f"https://{domain}/robots.txt"
        security_url = f"https://{domain}/.well-known/security.txt"
        
        is_allowed = True
        crawl_delay = 1
        contact = None
        robots_content = None
        security_content = None

        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            # A. Fetch robots.txt
            try:
                resp = await client.get(robots_url)
                if resp.status_code == 200:
                    robots_content = resp.text
                    rp = urllib.robotparser.RobotFileParser()
                    rp.parse(robots_content.splitlines())
                    
                    # Check extraction permission
                    is_allowed = rp.can_fetch(self.user_agent, f"https://{domain}/")
                    
                    # Check crawl delay (if present)
                    # Note: standard library robotparser doesn't support crawl-delay naturally in all versions
                    # We'll do a naive regex check if needed, or stick to default
                    # For now, default 1s
            except Exception as e:
                logger.warning(f"Failed to fetch robots.txt for {domain}: {e}")
                # Fail open (allow) if robots.txt is missing/error, standard practice
                is_allowed = True

            # B. Fetch security.txt
            try:
                resp = await client.get(security_url)
                if resp.status_code == 200:
                    security_content = resp.text
                    # Parse Contact
                    # Format: Contact: mailto:security@example.com
                    match = re.search(r"(?i)^Contact:\s*(.*)$", security_content, re.MULTILINE)
                    if match:
                        contact = match.group(1).strip()
            except Exception as e:
                logger.warning(f"Failed to fetch security.txt for {domain}: {e}")

        return is_allowed, crawl_delay, contact, robots_content, security_content
