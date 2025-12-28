import random
import datetime
from sqlalchemy import text
from database import engine, SessionLocal, Base
from models import User, Expense, Goal, MarketData

def init_db():
    # Drop all tables first to ensure clean slate (OPTIONAL, good for dev)
    # Base.metadata.drop_all(bind=engine)
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Convert market_data to hypertable (TimescaleDB specific)
    # We use execute with raw SQL. We capture exception if it already exists.
    with engine.connect() as conn:
        try:
            conn.execute(text("SELECT create_hypertable('market_data', 'time', if_not_exists => TRUE);"))
            print("Converted market_data to hypertable.")
        except Exception as e:
            print(f"Hypertable creation info: {e}")
        conn.commit()

def seed_users(db):
    if db.query(User).first():
        print("Users already seeded.")
        return

    user = User(
        name="Mehmet",
        work_start_time="08:00",
        home_location="Kadikoy, Istanbul",
        work_location="Levent, Istanbul"
    )
    db.add(user)
    db.commit()
    print("User seeded.")

def seed_market_data(db):
    if db.query(MarketData).count() > 0:
        print("Market data already seeded.")
        return

    print("Seeding 10 years of market data... This might take a moment.")
    
    symbols = ["USDTRY", "XAUUSD"]
    start_date = datetime.datetime.utcnow() - datetime.timedelta(days=365*10)
    
    data_buffer = []
    
    # Mock data generation
    # Starting prices
    price = {"USDTRY": 3.0, "XAUUSD": 1200.0}
    
    for day in range(365 * 10):
        current_date = start_date + datetime.timedelta(days=day)
        
        for symbol in symbols:
            # Random daily fluctuation
            change_percent = random.uniform(-0.02, 0.025) # Slightly bullish trend
            price[symbol] = price[symbol] * (1 + change_percent)
            
            data_buffer.append(MarketData(
                time=current_date,
                symbol=symbol,
                price=round(price[symbol], 2),
                volume=random.randint(1000, 50000)
            ))
            
        # Bulk insert every 1000 days to save memory
        if len(data_buffer) > 5000:
            db.bulk_save_objects(data_buffer)
            db.commit()
            data_buffer = []

    if data_buffer:
        db.bulk_save_objects(data_buffer)
        db.commit()
        
    print("Market data seeded.")

if __name__ == "__main__":
    init_db()
    db = SessionLocal()
    seed_users(db)
    seed_market_data(db)
    db.close()
