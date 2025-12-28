from fastapi import APIRouter
from services import transit_service, finance_service, budget_service

router = APIRouter()

@router.get("/transit/alarm-recommendation")
async def get_alarm(user_id: int = 1):
    return transit_service.recommend_alarm(user_id)

@router.get("/finance/correlation")
async def get_correlation(asset1: str = "USDTRY", asset2: str = "XAUUSD"):
    return finance_service.analyze_correlation(asset1, asset2)

@router.get("/budget/simulation")
async def get_simulation(goal_id: int = 1, sacrifice: str = "Cigarettes"):
    return budget_service.simulate_goal_achievement(goal_id, sacrifice)
