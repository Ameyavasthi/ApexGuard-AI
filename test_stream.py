import requests
import time

print("Testing video stream endpoint...")
try:
    response = requests.get('http://localhost:8000/api/stream', stream=True, timeout=5)
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        print("Stream is accessible!")
        # Read a few chunks to verify it's sending data
        chunk_count = 0
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                chunk_count += 1
                print(f"Received chunk {chunk_count}: {len(chunk)} bytes")
                if chunk_count >= 3:  # Just test a few chunks
                    break
    else:
        print(f"Error: {response.status_code}")
        
except requests.exceptions.RequestException as e:
    print(f"Request failed: {e}")
except Exception as e:
    print(f"Error: {e}")
