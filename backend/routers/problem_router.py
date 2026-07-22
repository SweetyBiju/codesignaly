from fastapi import APIRouter, HTTPException
from services.leetcode_service import get_problem_data

router = APIRouter(prefix="/problem", tags=["Problem"])

@router.get("/{slug}")
async def get_problem(slug: str):
    try:
        data = await get_problem_data(slug)
        return data
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
