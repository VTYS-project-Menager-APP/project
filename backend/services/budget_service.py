from database import SessionLocal
from models import Goal, Expense

def simulate_goal_achievement(goal_id: int, sacrifice_category: str):
    db = SessionLocal()
    try:
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if not goal:
            # Create a dummy goal if not exists for demo
            goal = Goal(title="Gaming PC", target_amount=30000, current_amount=0)
            
        # Analyze expenses
        # In real app: db.query(func.avg(Expense.amount)).filter(category==sacrifice_category)
        # Using mock assumption for now
        daily_waste = 60.0 # e.g. Cigarettes
        
        remaining_amount = goal.target_amount - goal.current_amount
        days_needed = remaining_amount / daily_waste
        
        return {
            "goal": goal.title,
            "remaining_amount": remaining_amount,
            "daily_sacrifice_from": sacrifice_category,
            "daily_saving": daily_waste,
            "days_to_goal": int(days_needed),
            "message": f"Eğer '{sacrifice_category}' harcamanı kisarsan, '{goal.title}' hedefine {int(days_needed)} gün içinde ulaşabilirsin!"
        }
        
    finally:
        db.close()
