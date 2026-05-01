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

    os.makedirs(config.SNAPSHOTS_DIR, exist_ok=True)
    os.makedirs(config.RECORDINGS_DIR, exist_ok=True)
    os.makedirs(config.FRONTEND_DIR, exist_ok=True)

    from api.database import init_db
    from core.engine   import engine
    init_db()
    state.seed_from_db()

    engine.start()

    logger.info("ApexGuard AI server ready — http://localhost:8005")
    yield

    engine.stop()

app = FastAPI(title="ApexGuard AI Dashboard", lifespan=lifespan)

app.mount("/static",     StaticFiles(directory=config.FRONTEND_DIR),   name="static")
app.mount("/snapshots",  StaticFiles(directory=config.SNAPSHOTS_DIR),  name="snapshots")
app.mount("/video",      StaticFiles(directory=config.RECORDINGS_DIR), name="video")

app.include_router(stream_router)
app.include_router(events_router, prefix="/api")
app.include_router(snapshots_router, prefix="/api")
app.include_router(recordings_router, prefix="/api")

@app.get("/")
def home_page():
    return FileResponse(os.path.join(config.FRONTEND_DIR, "index.html"))

@app.get("/detect/{type}")
def detect_page(type: str):
    return FileResponse(os.path.join(config.FRONTEND_DIR, "detect.html"))

@app.get("/logs")
def logs_page():
    return FileResponse(os.path.join(config.FRONTEND_DIR, "logs.html"))

VALID_MODULES = {"animal", "fire", "weapon"}

@app.post("/api/start/{dtype}")
async def start_detection(dtype: str):

    if dtype in VALID_MODULES:
        state.active_modules[dtype] = True
        logger.info(f"Started detection for: {dtype}")
    return {"status": "success", "module": dtype}

@app.post("/api/stop/{dtype}")
async def stop_detection(dtype: str):

    if dtype in VALID_MODULES:
        state.active_modules[dtype] = False
        logger.info(f"Stopped detection for: {dtype}")
    return {"status": "success", "module": dtype}

@app.get("/api/logs/data")
async def get_logs_csv():

    log_file = getattr(config, 'EVENT_LOG_FILE', 'detection_logs.csv')
    logs = []

    def read_logs():
        if not os.path.exists(log_file):
            return []
        with open(log_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            rows = []
            for row in reader:

                vp = row.get("Video Path", "N/A")
                sp = row.get("Snapshot Path", "")
                if vp and vp != "N/A":
                    row["Video Path"] = os.path.basename(vp)
                if sp and sp not in ("No Frame Provided", ""):
                    row["Snapshot Path"] = os.path.basename(sp)
                rows.append(row)
            return rows

    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor(max_workers=1) as pool:
        logs = await loop.run_in_executor(pool, read_logs)

    return JSONResponse(logs[::-1])
