
from fastapi import APIRouter, Depends
from services import etkinlik_service

router = APIRouter(
    prefix="/etkinlik",
    tags=["etkinlik"]
)

@router.get("/events")
async def read_events(limit: int = 10):
    return await etkinlik_service.get_events(limit=limit)
