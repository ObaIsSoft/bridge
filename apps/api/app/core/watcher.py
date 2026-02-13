import time
import logging
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from app.services.scanner import SecretScanner

logger = logging.getLogger("security_watcher")

class SecretWatcherHandler(FileSystemEventHandler):
    def __init__(self):
        self.scanner = SecretScanner()

    def on_modified(self, event):
        if event.is_directory:
            return
        
        # Avoid scanning specific excluded directories/files
        if any(x in event.src_path for x in [".git", "node_modules", ".next", "venv", "__pycache__"]):
            return

        logger.info(f"File modified: {event.src_path}. Running security scan...")
        findings = self.scanner.scan_file(event.src_path)
        if findings:
            logger.warning(f"⚠️ SECURITY ALERT: {len(findings)} secrets detected in {event.src_path}!")
            for f in findings:
                logger.warning(f"  - [{f['type']}] detected (redacted: {f['match']})")
        else:
            logger.info(f"✅ No secrets found in {event.src_path}.")

class SecurityWatcher:
    def __init__(self, watch_path: str):
        self.watch_path = watch_path
        self.observer = Observer()
        self.handler = SecretWatcherHandler()
        self.thread = None

    def start(self):
        logger.info(f"Starting Security Watcher on {self.watch_path}...")
        self.observer.schedule(self.handler, self.watch_path, recursive=True)
        self.observer.start()
        
    def stop(self):
        logger.info("Stopping Security Watcher...")
        self.observer.stop()
        self.observer.join()

# Global watcher instance
_watcher = None

def start_background_watcher(path: str):
    global _watcher
    if _watcher is None:
        _watcher = SecurityWatcher(path)
        _watcher.start()

def stop_background_watcher():
    global _watcher
    if _watcher:
        _watcher.stop()
        _watcher = None
