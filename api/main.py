"""
api/main.py — Clean FastAPI Application Entry Point
====================================================
ALL ENDPOINTS ARE ASYNC — Non-blocking event loop
"""
import os
import csv
import logging
import asyncio
from contextlib import asynccontextmanager
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

import config
from core.state_manager import state
from api.stream import router as stream_router
from api.routes.events import router as events_router
from api.routes.snapshots import router as snapshots_router
from api.routes.recordings import router as recordings_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s")
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure local storage folders exist
    os.makedirs("snapshots", exist_ok=True)
    os.makedirs("recordings", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    # Database verification
    from api.database import init_db
    from core.engine   import engine
    init_db()
    state.seed_from_db()
    
    # ⚡ Start background detection engine thread ⚡
    engine.start()
    
    logger.info("ApexGuard AI server ready — http://localhost:8005")
    yield
    
    # 🔌 Cleanup engine
    engine.stop()

app = FastAPI(title="ApexGuard AI Dashboard", lifespan=lifespan)

# Mount local directories correctly
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/snapshots", StaticFiles(directory="snapshots"), name="snapshots")
app.mount("/video", StaticFiles(directory="recordings"), name="video")

# Attach all routers
app.include_router(stream_router)
app.include_router(events_router, prefix="/api")
app.include_router(snapshots_router, prefix="/api")
app.include_router(recordings_router, prefix="/api")

# --- PAGE ROUTES ---
@app.get("/")
def home_page():
    return FileResponse("static/index.html")

@app.get("/detect/{type}")
def detect_page(type: str):
    return FileResponse("static/detect.html")

@app.get("/logs")
def logs_page():
    return FileResponse("static/logs.html")

# --- CONTROL ROUTES (ASYNC - Non-blocking) ---
VALID_MODULES = {"animal", "fire", "weapon"}

@app.post("/api/start/{dtype}")
async def start_detection(dtype: str):
    """Async endpoint to start detection module."""
    if dtype in VALID_MODULES:
        state.active_modules[dtype] = True
        logger.info(f"Started detection for: {dtype}")
    return {"status": "success", "module": dtype}

@app.post("/api/stop/{dtype}")
async def stop_detection(dtype: str):
    """Async endpoint to stop detection module."""
    if dtype in VALID_MODULES:
        state.active_modules[dtype] = False
        logger.info(f"Stopped detection for: {dtype}")
    return {"status": "success", "module": dtype}

@app.get("/api/logs/data")
async def get_logs_csv():
    """Async endpoint to get logs - non-blocking file I/O."""
    log_file = getattr(config, 'EVENT_LOG_FILE', 'detection_logs.csv')
    logs = []
    
    def read_logs():
        if not os.path.exists(log_file):
            return []
        with open(log_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            rows = []
            for row in reader:
                # Normalize paths
                vp = row.get("Video Path", "N/A")
                sp = row.get("Snapshot Path", "")
                if vp and vp != "N/A":
                    row["Video Path"] = os.path.basename(vp)
                if sp and sp not in ("No Frame Provided", ""):
                    row["Snapshot Path"] = os.path.basename(sp)
                rows.append(row)
            return rows
    
    # Run file I/O in thread pool
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=1) as pool:
        logs = await loop.run_in_executor(pool, read_logs)
    
    return JSONResponse(logs[::-1])  # Newest first
