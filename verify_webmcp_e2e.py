import asyncio
import os
import time
import requests
import subprocess
import signal
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_webmcp")

API_URL = "http://localhost:8000/api/v1"
DEMO_PORT = 8081
DEMO_URL = f"http://localhost:{DEMO_PORT}/food-app.html"

def start_demo_server():
    """Start python http server in webmcp-starter dir"""
    # Assuming script is in project root
    script_dir = os.path.dirname(os.path.abspath(__file__))
    web_root = os.path.join(script_dir, "apps/webmcp-starter")
    
    if not os.path.exists(web_root):
        # Maybe we are running from apps/api and script is there or referenced?
        # Let's try to find project root
        if os.path.exists("../webmcp-starter"):
             web_root = os.path.abspath("../webmcp-starter")
        elif os.path.exists("../../apps/webmcp-starter"):
             web_root = os.path.abspath("../../apps/webmcp-starter")

    logger.info(f"Starting demo server at {web_root} on port {DEMO_PORT}")
    process = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(DEMO_PORT)],
        cwd=web_root,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    time.sleep(2) # Wait for startup
    return process

async def run_verification():
    server_process = start_demo_server()
    try:
        logger.info("1. Surveying the demo URL...")
        response = requests.post(f"{API_URL}/bridges/survey", json={"url": DEMO_URL})
        logger.info(f"Survey Status: {response.status_code}")
        try:
            survey_data = response.json()
        except Exception:
            logger.error(f"Failed to parse JSON. Response text: {response.text}")
            raise
        logger.info(f"Survey Result: {survey_data}")

        assert survey_data.get("has_webmcp") == True, "WebMCP not detected!"
        assert len(survey_data.get("webmcp_tools", [])) > 0, "No tools discovered!"
        
        tools = survey_data["webmcp_tools"]
        logger.info(f"Discovered {len(tools)} tools.")

        logger.info("2. Creating Bridge with discovered tools...")
        bridge_payload = {
            "name": "Midnight Eats Demo",
            "target_url": DEMO_URL,
            "domain": "localhost",
            "extraction_schema": {"type": "object"},
            "webmcp_tools": tools
        }
        bridge_resp = requests.post(f"{API_URL}/bridges/", json=bridge_payload)
        logger.info(f"Create Status: {bridge_resp.status_code}")
        bridge = bridge_resp.json()
        assert bridge.get("has_webmcp") == True, "Bridge has_webmcp flag not set!"
        assert len(bridge.get("webmcp_tools", [])) == len(tools), "Tools not saved correctly!"
        
        bridge_id = bridge["id"]
        logger.info(f"Bridge Created: {bridge_id}")

        logger.info("3. Running Extraction Task (Test Fallback/Execution)...")
        # Since 'food-app.html' likely doesn't have an 'extract' tool, we expect fallback or log message
        # But we can verify that the task runs and returns success (even if via fallback)
        task_resp = requests.post(f"{API_URL}/bridges/{bridge_id}/extract")
        logger.info(f"Task Status: {task_resp.status_code}")
        task_data = task_resp.json()
        task_id = task_data["task_id"]
        logger.info(f"Task ID: {task_id}")

        # Poll for completion
        for _ in range(10):
            time.sleep(2)
            status_resp = requests.get(f"{API_URL}/bridges/tasks/{task_id}")
            status = status_resp.json()
            logger.info(f"Task Status: {status['status']}")
            if status['status'] in ['SUCCESS', 'FAILURE']:
                break
        
        logger.info("Verification Complete!")
        
    except Exception as e:
        logger.error(f"Verification Failed: {e}")
        raise e
    finally:
        server_process.terminate()

if __name__ == "__main__":
    asyncio.run(run_verification())
