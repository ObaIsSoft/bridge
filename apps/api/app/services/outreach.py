import os
import logging
import aiosmtplib
from email.message import EmailMessage
import tweepy
from github import Github
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class OutreachService:
    def __init__(self):
        # Email Config
        self.smtp_host = os.getenv("SMTP_HOST")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_pass = os.getenv("SMTP_PASS")
        self.email_from = os.getenv("EMAIL_FROM", "bot@bridge.dev")

        # Twitter Config
        self.twitter_api_key = os.getenv("TWITTER_API_KEY")
        self.twitter_api_secret = os.getenv("TWITTER_API_SECRET")
        self.twitter_access_token = os.getenv("TWITTER_ACCESS_TOKEN")
        self.twitter_access_secret = os.getenv("TWITTER_ACCESS_SECRET")

        # GitHub Config
        self.github_token = os.getenv("GITHUB_TOKEN")

    async def send_email(self, to_email: str, subject: str, body: str) -> Optional[str]:
        """Sends an email and returns the message ID (or None on failure)."""
        if not (self.smtp_host and self.smtp_user and self.smtp_pass):
            logger.warning("SMTP credentials not configured. Skipping email.")
            return None

        message = EmailMessage()
        message["From"] = self.email_from
        message["To"] = to_email
        message["Subject"] = subject
        message.set_content(body)

        try:
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_pass,
                start_tls=True,
            )
            # aiosmtplib doesn't return a message ID easily, so we generate/return a success marker
            return "sent-via-smtp" 
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            raise e

    async def send_tweet(self, handle: str, text: str) -> Optional[str]:
        """Posts a tweet mentioning the user. Returns Tweet ID."""
        if not (self.twitter_api_key and self.twitter_api_secret and self.twitter_access_token and self.twitter_access_secret):
             logger.warning("Twitter credentials not configured. Skipping tweet.")
             return None
        
        try:
            # Authenticate
            client = tweepy.Client(
                consumer_key=self.twitter_api_key,
                consumer_secret=self.twitter_api_secret,
                access_token=self.twitter_access_token,
                access_token_secret=self.twitter_access_secret
            )
            
            # Post Tweet
            # Note: Free tier might have limits, handle appropriately
            full_text = f"{handle} {text}"
            response = client.create_tweet(text=full_text)
            
            return response.data['id']
        except Exception as e:
            logger.error(f"Failed to send tweet to {handle}: {e}")
            raise e

    async def create_github_issue(self, repo_url: str, title: str, body: str) -> Optional[str]:
        """Creates an issue on the given GitHub repo. Returns Issue URL."""
        if not self.github_token:
            logger.warning("GitHub token not configured. Skipping issue creation.")
            return None

        try:
            # Extract owner/repo from URL (e.g., https://github.com/owner/repo)
            parts = repo_url.rstrip("/").split("/")
            if len(parts) < 2:
                 raise ValueError(f"Invalid GitHub URL: {repo_url}")
            
            repo_name = f"{parts[-2]}/{parts[-1]}" # owner/repo
            
            g = Github(self.github_token)
            repo = g.get_repo(repo_name)
            issue = repo.create_issue(title=title, body=body)
            
            return str(issue.number)
        except Exception as e:
            logger.error(f"Failed to create GitHub issue on {repo_url}: {e}")
            raise e
