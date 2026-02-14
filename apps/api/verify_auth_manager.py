
import requests
import time
import sys
import json

API_URL = "http://localhost:8000/api/v1"
API_KEY = "ab_6u4fOliyqihF9sSdN9Y1V581zjYABwFWpz4cTD4kjpw"

def cleanup_bridge(slug):
    try:
        requests.delete(f"{API_URL}/bridges/{slug}", headers={"X-API-Key": API_KEY})
    except:
        pass

def main():
    slug = "auth-test-bridge"
    cleanup_bridge(slug)
    
    print(f"Creating Bridge {slug}...")
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    payload = {
        "name": "Auth Test Bridge",
        "slug": slug,
        "domain": "httpbin.org",
        "target_url": "https://httpbin.org/cookies/set/session_check/persisted_value",
        "extraction_schema": {"type": "object", "properties": {"status": {"type": "string"}}},
        "mode": "schema"
    }
    
    resp = requests.post(f"{API_URL}/bridges/", json=payload, headers=headers)
    if resp.status_code not in [200, 201]:
        print(f"Failed to create bridge: {resp.text}")
        sys.exit(1)
        
    print("Triggering Extraction to capture cookie...")
    resp = requests.post(f"{API_URL}/bridges/{slug}/extract", headers=headers)
    if resp.status_code != 200:
        print(f"Failed to trigger extraction: {resp.text}")
        sys.exit(1)
        
    task_id = resp.json()["task_id"]
    
    # Poll for completion
    for _ in range(20):
        print(f"Polling task {task_id}...", end="\r")
        task_resp = requests.get(f"{API_URL}/bridges/tasks/{task_id}", headers=headers)
        if task_resp.status_code == 200:
            status = task_resp.json().get("status")
            if status == "SUCCESS":
                print(f"\nTask matched! Checking session data...")
                break
            elif status == "FAILURE":
                print(f"\nTask failed: {task_resp.json().get('error')}")
                sys.exit(1)
        time.sleep(1)
        
    # Check Bridge Session Data
    resp = requests.get(f"{API_URL}/bridges/{slug}", headers=headers)
    bridge_data = resp.json()
    
    session_data = bridge_data.get("session_data")
    print("\nSession Data:", json.dumps(session_data, indent=2))
    
    if not session_data or "cookies" not in session_data:
        print("FAILURE: No session data captured.")
        sys.exit(1)
        
    cookies = session_data["cookies"]
    found = False
    for c in cookies:
        if c.get("name") == "session_check" and c.get("value") == "persisted_value":
            found = True
            break
            
    if found:
        print("\nSUCCESS: Session cookie captured and persisted!")
        sys.exit(0)
    else:
        print("\nFAILURE: Expected cookie 'session_check' not found in session data.")
        sys.exit(1)

if __name__ == "__main__":
    main()
