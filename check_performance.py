import requests
import json

try:
    response = requests.get('http://localhost:8000/api/performance/stats', timeout=3)
    if response.status_code == 200:
        stats = response.json()
        print("Current Performance Stats:")
        print(json.dumps(stats, indent=2))
    else:
        print(f"Error: {response.status_code}")
except Exception as e:
    print(f"Failed to get performance stats: {e}")
