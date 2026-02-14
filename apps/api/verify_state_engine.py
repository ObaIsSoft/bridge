
import requests
import time
import sys

API_URL = "http://localhost:8000/api/v1"
API_KEY = "ab_6u4fOliyqihF9sSdN9Y1V581zjYABwFWpz4cTD4kjpw"
BRIDGE_SLUG = "test-bridge"

def get_task_status(task_id):
    url = f"{API_URL}/bridges/tasks/{task_id}"
    for _ in range(20):
        print(f"Polling task {task_id}...", end="\r")
        try:
            resp = requests.get(url, headers={"X-API-Key": API_KEY})
            if resp.status_code == 200:
                data = resp.json()
                status = data.get("status")
                if status in ["SUCCESS", "FAILURE"]:
                    print(f"\nTask {task_id} finished with status: {status}")
                    return data
        except Exception as e:
            print(f"\nError polling task: {e}")
        time.sleep(1)
    return None

def main():
    print(f"Triggering Extraction 1 for {BRIDGE_SLUG}...")
    resp = requests.post(f"{API_URL}/bridges/{BRIDGE_SLUG}/extract", headers={"X-API-Key": API_KEY})
    if resp.status_code != 200:
        print(f"Failed to start extraction 1: {resp.text}")
        sys.exit(1)
    
    task_id_1 = resp.json()["task_id"]
    print(f"Started Task 1: {task_id_1}")
    
    result_1 = get_task_status(task_id_1)
    if not result_1 or result_1.get("status") != "SUCCESS":
        print("Task 1 failed or timed out.")
        sys.exit(1)
        
    print("Task 1 Result:", result_1.get("result"))

    print("\n--- Waiting 2 seconds ---\n")
    time.sleep(2)

    print(f"Triggering Extraction 2 (Duplicate Check) for {BRIDGE_SLUG}...")
    resp = requests.post(f"{API_URL}/bridges/{BRIDGE_SLUG}/extract", headers={"X-API-Key": API_KEY})
    if resp.status_code != 200:
        print(f"Failed to start extraction 2: {resp.text}")
        sys.exit(1)

    task_id_2 = resp.json()["task_id"]
    print(f"Started Task 2: {task_id_2}")
    
    result_2 = get_task_status(task_id_2)
    if not result_2:
        print("Task 2 timed out.")
        sys.exit(1)
        
    res_data = result_2.get("result", {})
    print("Task 2 Result:", res_data)
    
    if res_data.get("status") == "skipped" and res_data.get("reason") == "duplicate_data":
        print("\nSUCCESS: Deduplication confirmed!")
        sys.exit(0)
    else:
        print("\nFAILURE: Deduplication did not trigger.")
        sys.exit(1)

if __name__ == "__main__":
    main()
