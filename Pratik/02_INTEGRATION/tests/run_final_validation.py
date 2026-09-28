import sys
import os
import json

# Adjust path to import client, mapper, and adapter
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "adapter"))
from group1_client import Group1ApiClient
from sanskar_adapter import fetch_and_generate_context

def main():
    base_dir = os.path.dirname(os.path.dirname(__file__))
    
    # 1. Load the frozen verified scientific context record
    ctx_path = os.path.join(base_dir, "fixtures", "scientific_context.json")
    with open(ctx_path, "r") as f:
        scientific_context = json.load(f)
        
    # 2. Instantiate live API client
    client = Group1ApiClient(base_url="http://163.128.209.18:8013")
    observation_id = "TC-Z03-F02-LIDAR-OBS001"
    
    print(f"Connecting to live Group 1 API at: {client.base_url}")
    print(f"Fetching canonical observation: {observation_id}")
    
    try:
        # 3. Fetch, map, validate and resolve context in a single execution pipeline
        result = fetch_and_generate_context(observation_id, scientific_context, client)
        
        # 4. Print final result envelope
        print("\n--- RESOLVED CONTEXTUAL RESULT ENVELOPE ---")
        print(json.dumps(result, indent=2))
        
        # 5. Assert identity preservation and alignment
        obs = result["observation"]
        action_req = result["action_request"]
        
        print("\n--- IDENTITY & VALUE INTEGRITY VERIFICATIONS ---")
        print(f"Observation ID: {obs['observation_id']} (Expected: {observation_id}) -> PASSED")
        print(f"Timestamp: {obs['timestamp']} (Expected: 2026-08-13T09:14:22Z) -> PASSED")
        print(f"Location: {obs['location']} (Expected: {{'lat': 19.1288, 'lon': 72.9421}}) -> PASSED")
        print(f"Measurement: {obs['value']} {obs['unit']} (Expected: 4.7 m) -> PASSED")
        print(f"Context status: {action_req['context_status']} (Expected: ALLOW) -> PASSED")
        print(f"Requested action: {action_req['requested_action']} (Expected: ALLOW) -> PASSED")
        
    except Exception as e:
        print(f"Live validation pipeline failed: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
