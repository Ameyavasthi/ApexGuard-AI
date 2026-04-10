"""
start_server.py — Optimized Production Server Launcher
========================================================
Uses Uvicorn with multiple workers to isolate API handling from streaming load.
"""
import uvicorn
import multiprocessing

def get_workers():
    """Calculate optimal worker count based on CPU cores."""
    cpu_count = multiprocessing.cpu_count()
    # Use 2 workers minimum, max half of CPU cores to leave resources for YOLO
    return max(2, min(cpu_count // 2, 4))

if __name__ == "__main__":
    workers = 1  # Standardize for Windows
    print(f"Starting ApexGuard AI with {workers} worker(s)...")
    print(f"API endpoints will be isolated from streaming load")
    print(f"Performance mode: Optimized for real-time processing")
    
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8005,
        workers=1,                 # Single worker for Windows (Engine is decoupled in thread)
        loop="asyncio",            # Use asyncio event loop
        http="h11",                # Pure Python HTTP parser (more stable)
        reload=False,              # Disable reload for production stability
        access_log=False,          # Reduce logging overhead
        timeout_keep_alive=5,      # Short keep-alive for faster connection cycling
        limit_concurrency=20,      # Limit concurrent connections
        backlog=100,               # Connection queue size
    )
