import re
import os
import subprocess
import requests
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# Common Secret Patterns
SECRET_PATTERNS = {
    "OpenAI API Key": r"sk-(?:proj-)?[a-zA-Z0-9]{32,128}",
    "Anthropic API Key": r"ant-api-key-v1-[a-zA-Z0-9-_]{80,}",
    "Google Cloud API Key": r"AIza[0-9A-Za-z-_]{35}",
    "AWS Access Key ID": r"AKIA[0-9A-Z]{16}",
    "AWS Secret Access Key": r"(?i)aws(.{0,20})?['\"][0-9a-zA-Z\/+]{40}['\"]",
    "GitHub Personal Access Token": r"ghp_[a-zA-Z0-9]{36}",
    "Stripe Secret Key": r"sk_live_[0-9a-zA-Z]{24}",
    "Slack Bot Token": r"xoxb-[0-9]{11}-[0-9]{12}-[a-zA-Z0-9]{24}",
}

class SecretScanner:
    @staticmethod
    def scan_string(content: str) -> List[Dict[str, Any]]:
        findings = []
        for name, pattern in SECRET_PATTERNS.items():
            matches = re.finditer(pattern, content)
            for match in matches:
                val = match.group()
                redacted = val[:6] + "..." + val[-4:] if len(val) > 10 else "****"
                findings.append({
                    "type": name,
                    "match": redacted,
                    "raw": val, # Needed for validation
                    "start": match.start(),
                    "end": match.end()
                })
        return findings

    @staticmethod
    def scan_file(file_path: str) -> List[Dict[str, Any]]:
        findings = []
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                file_findings = SecretScanner.scan_string(content)
                for finding in file_findings:
                    finding["file"] = file_path
                    findings.append(finding)
        except Exception:
            pass
        return findings

    @staticmethod
    def scan_directory(root_dir: str, exclude_dirs: List[str] = None) -> List[Dict[str, Any]]:
        if exclude_dirs is None:
            exclude_dirs = [".git", "node_modules", "__pycache__", "venv", ".next", "dist"]
            
        all_findings = []
        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                file_path = os.path.join(root, file)
                findings = SecretScanner.scan_file(file_path)
                all_findings.extend(findings)
        return all_findings

    @staticmethod
    def scan_git_history(repo_path: str) -> List[Dict[str, Any]]:
        """Scans the entire git history for secrets using git log -p."""
        findings = []
        try:
            # Get the full diff of all commits
            cmd = ["git", "-C", repo_path, "log", "-p", "--all"]
            result = subprocess.run(cmd, capture_output=True, text=True, errors="ignore")
            if result.returncode == 0:
                # We can refine this to track commit SHAs if needed
                all_findings = SecretScanner.scan_string(result.stdout)
                for f in all_findings:
                    f["source"] = "git_history"
                    findings.append(f)
        except Exception as e:
            print(f"Git scan failed: {e}")
        return findings

    @staticmethod
    async def validate_key(key_type: str, key: str) -> str:
        """Performs a non-destructive check to see if a key is active."""
        try:
            if "OpenAI" in key_type:
                resp = requests.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {key}"},
                    timeout=5
                )
                return "active" if resp.status_code == 200 else "revoked"
            
            if "Google" in key_type:
                # Simple check for Google API key validity via a public discovery API
                resp = requests.get(
                    f"https://www.googleapis.com/discovery/v1/apis?key={key}",
                    timeout=5
                )
                return "active" if resp.status_code == 200 else "revoked"
            
            # Add more validators as needed
            return "unknown"
        except Exception:
            return "unknown"
