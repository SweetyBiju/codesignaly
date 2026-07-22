from fastapi import APIRouter, HTTPException
from services.analytics_service import get_mastery_scores, get_weakspots, get_stats

router = APIRouter(tags=["Analytics"])

@router.get("/mastery")
async def mastery_endpoint():
    try:
        return get_mastery_scores()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/weakspots")
async def weakspots_endpoint():
    try:
        return get_weakspots()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/stats")
async def stats_endpoint():
    try:
        return get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
