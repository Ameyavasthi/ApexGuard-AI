import requests
import time

print("Testing video stream availability...")
try:
    response = requests.get('http://localhost:8000/api/stream', stream=True, timeout=10)
    print(f"Stream response status: {response.status_code}")
    
    if response.status_code == 200:
        print("Stream is accessible! Reading first few chunks...")
        chunk_count = 0
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                chunk_count += 1
                print(f"Chunk {chunk_count}: {len(chunk)} bytes")
                if chunk_count >= 5:
                    print("Stream is working properly!")
                    break
        if chunk_count == 0:
            print("No chunks received - stream may be hanging")
    else:
        print(f"Stream error: {response.status_code}")
        
except Exception as e:
    print(f"Stream test failed: {e}")
