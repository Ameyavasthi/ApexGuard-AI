import asyncio
from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse
from core.state_manager import state

router = APIRouter()

@router.get("/events")
async def get_events(limit: int = Query(20, ge=1, le=100),
               offset: int = Query(0, ge=0),
               event_type: str = Query(None)):

    api_state = state.get_api_state()
    events = api_state["events"]

    if event_type:
        events = [e for e in events if e.get("event_type") == event_type]

    return JSONResponse({
        "total": api_state["stats"]["total"],
        "offset": offset,
        "limit": limit,
        "events": events[offset:offset+limit]
    })

@router.get("/stats")
async def get_stats():

    api_state = state.get_api_state()
    return JSONResponse(api_state["stats"])

@router.get("/health")
async def get_health():

    return JSONResponse(state.get_api_state()["performance"])
