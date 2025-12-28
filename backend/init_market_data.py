"""
Data Initialization Script
Veritabanını sample data ile doldurup test etmeye hazır hale getirir
"""

import sys
import os

# Backend dizinini path'e ekle
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import engine, Base, SessionLocal
from models import (
    User, HistoricalEvent, MarketEventCorrelation, 
    CurrentMarketRate, CurrentEvent
)
from services.kaggle_service import insert_sample_data
import asyncio

def init_database():
    """
    Veritabanını oluştur ve tabloları ekle
    """
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully")


def seed_sample_data():
    """
    Örnek verileri ekle
    """
    print("\nSeeding sample historical events and correlations...")
    insert_sample_data()
    print("✓ Sample data seeded successfully")


def verify_data():
    """
    Eklenen verileri kontrol et
    """
    db = SessionLocal()
    
    try:
        print("\n" + "="*50)
        print("DATA VERIFICATION")
        print("="*50)
        
        # Historical events
        event_count = db.query(HistoricalEvent).count()
        print(f"\n📊 Historical Events: {event_count}")
        
        if event_count > 0:
            events = db.query(HistoricalEvent).limit(3).all()
            for event in events:
                print(f"  - {event.title} ({event.event_date.strftime('%Y-%m-%d')})")
        
        # Market correlations
        corr_count = db.query(MarketEventCorrelation).count()
        print(f"\n📈 Market Correlations: {corr_count}")
        
        if corr_count > 0:
            correlations = db.query(MarketEventCorrelation).limit(3).all()
            for corr in correlations:
                print(f"  - {corr.symbol}: {corr.percent_change:+.2f}%")
        
        # Current market rates
        rate_count = db.query(CurrentMarketRate).count()
        print(f"\n💰 Current Market Rates: {rate_count}")
        
        # Current events
        event_count = db.query(CurrentEvent).count()
        print(f"\n📰 Current Events: {event_count}")
        
        print("\n" + "="*50)
        print("✓ Database verification complete")
        print("="*50 + "\n")
        
    finally:
        db.close()


async def test_market_data():
    """
    Market data servisini test et
    """
    print("\nTesting market data service...")
    try:
        from services.finance_service import get_current_rates
        
        rates = await get_current_rates(['GOLD', 'USDTRY'])
        
        if rates:
            print("✓ Market data fetched successfully:")
            for rate in rates:
                print(f"  - {rate.name}: {rate.price:.2f} ({rate.daily_change_percent:+.2f}%)")
        else:
            print("⚠ No market data fetched (might be API rate limit or network issue)")
            
    except Exception as e:
        print(f"⚠ Market data test failed: {str(e)}")


def main():
    """
    Ana initialization fonksiyonu
    """
    print("\n" + "="*50)
    print("MARKET ANALYSIS - DATA INITIALIZATION")
    print("="*50 + "\n")
    
    # 1. Database oluştur
    init_database()
    
    # 2. Sample data ekle
    seed_sample_data()
    
    # 3. Verileri kontrol et
    verify_data()
    
    # 4. Market data test
    print("Testing real-time market data fetch...")
    asyncio.run(test_market_data())
    
    print("\n" + "="*50)
    print("✅ INITIALIZATION COMPLETE!")
    print("="*50)
    print("\nNext steps:")
    print("1. Set NEWS_API_KEY in .env file")
    print("2. Run: uvicorn main:app --reload")
    print("3. Access API: http://localhost:8000/api/v1/market-analysis/full-analysis")
    print("4. Frontend: npm run dev\n")


if __name__ == "__main__":
    main()
