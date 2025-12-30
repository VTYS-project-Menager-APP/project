"""
Test script for Smart Transport Alarm System
Run this script to verify the implementation
"""

import asyncio
import sys
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add parent directory to path
sys.path.append('.')

from database import SessionLocal, engine
from models import Base, User, UserTransportAlarm, AlarmSelectedRoute
from services.smart_transport_service import get_smart_transport_service
from services.ibb_transport_service import get_ibb_service


async def test_ibb_api():
    """Test İBB API connection"""
    print("=" * 60)
    print("TEST 1: İBB API Bağlantısı")
    print("=" * 60)
    
    ibb_service = get_ibb_service()
    
    # Test sefer gerçekleşme
    print("\n📡 Testing sefer gerçekleşme API...")
    sefer_data = await ibb_service.get_sefer_gerceklesme("34")
    
    if sefer_data:
        print("✅ İBB API bağlantısı başarılı!")
        print(f"   Veri alındı: {type(sefer_data)}")
    else:
        print("⚠️  İBB API yanıt vermedi (normal olabilir, test ortamı)")
    
    await ibb_service.close()
    print()


def test_database_schema():
    """Test database schema"""
    print("=" * 60)
    print("TEST 2: Veritabanı Şeması")
    print("=" * 60)
    
    try:
        # Create tables if not exist
        Base.metadata.create_all(bind=engine)
        print("✅ Veritabanı tabloları oluşturuldu/kontrol edildi")
        
        # Check tables
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        required_tables = ['user_transport_alarms', 'alarm_selected_routes']
        for table in required_tables:
            if table in tables:
                print(f"✅ Tablo bulundu: {table}")
            else:
                print(f"❌ Tablo bulunamadı: {table}")
        
        print()
    except Exception as e:
        print(f"❌ Veritabanı hatası: {e}")
        print()


async def test_smart_alarm_creation():
    """Test smart alarm creation"""
    print("=" * 60)
    print("TEST 3: Akıllı Alarm Oluşturma")
    print("=" * 60)
    
    db = SessionLocal()
    smart_service = get_smart_transport_service()
    
    try:
        # Get or create test user
        test_user = db.query(User).filter(User.email == "test@example.com").first()
        
        if not test_user:
            print("⚠️  Test kullanıcısı bulunamadı, oluşturuluyor...")
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            test_user = User(
                name="Test User",
                email="test@example.com",
                hashed_password=pwd_context.hash("testpassword"),
                work_start_time="09:00"
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            print(f"✅ Test kullanıcısı oluşturuldu (ID: {test_user.id})")
        else:
            print(f"✅ Test kullanıcısı bulundu (ID: {test_user.id})")
        
        # Create test alarm
        target_time = (datetime.now() + timedelta(hours=2)).strftime("%H:%M")
        
        print("\n📝 Test alarmı oluşturuluyor...")
        alarm = await smart_service.create_smart_alarm(
            db=db,
            user_id=test_user.id,
            alarm_name="Test İşe Gidiş",
            origin_location="Kadıköy",
            destination_location="Levent",
            target_arrival_time=target_time,
            travel_time_to_stop=10,
            selected_hat_kodlari=["34", "34A", "500T"],
            origin_durak_kodu="TEST001",
            destination_durak_kodu="TEST002"
        )
        
        print(f"✅ Alarm oluşturuldu!")
        print(f"   ID: {alarm.id}")
        print(f"   Ad: {alarm.alarm_name}")
        print(f"   Hedef Saat: {alarm.target_arrival_time}")
        
        # Check selected routes
        routes = db.query(AlarmSelectedRoute).filter(
            AlarmSelectedRoute.alarm_id == alarm.id
        ).all()
        
        print(f"   Seçili Hatlar: {[r.hat_kodu for r in routes]}")
        print()
        
        return alarm.id
        
    except Exception as e:
        print(f"❌ Alarm oluşturma hatası: {e}")
        import traceback
        traceback.print_exc()
        print()
        return None
    finally:
        db.close()


async def test_alarm_check(alarm_id):
    """Test alarm check functionality"""
    print("=" * 60)
    print("TEST 4: Alarm Kontrol Mekanizması")
    print("=" * 60)
    
    if not alarm_id:
        print("⚠️  Alarm ID bulunamadı, bu test atlanıyor")
        print()
        return
    
    db = SessionLocal()
    smart_service = get_smart_transport_service()
    
    try:
        alarm = db.query(UserTransportAlarm).filter(
            UserTransportAlarm.id == alarm_id
        ).first()
        
        if not alarm:
            print(f"❌ Alarm bulunamadı (ID: {alarm_id})")
            return
        
        print(f"🔍 Alarm kontrol ediliyor (ID: {alarm_id})...")
        
        should_trigger, trigger_data = await smart_service.check_alarm_should_trigger(
            db=db,
            alarm=alarm,
            current_time=datetime.now()
        )
        
        if should_trigger:
            print("✅ Alarm TETİKLENDİ!")
            print(f"   Mesaj: {trigger_data.get('message')}")
            print(f"   Hat: {trigger_data.get('hat_kodu')}")
        else:
            print("✅ Alarm kontrol edildi (henüz tetiklenmedi)")
            print(f"   Hedef Saat: {alarm.target_arrival_time}")
            print(f"   Durum: Bekleniyor")
        
        print()
        
    except Exception as e:
        print(f"❌ Alarm kontrol hatası: {e}")
        import traceback
        traceback.print_exc()
        print()
    finally:
        db.close()


async def test_user_alarms_status():
    """Test getting user alarms status"""
    print("=" * 60)
    print("TEST 5: Kullanıcı Alarmları Durumu")
    print("=" * 60)
    
    db = SessionLocal()
    smart_service = get_smart_transport_service()
    
    try:
        # Get test user
        test_user = db.query(User).filter(User.email == "test@example.com").first()
        
        if not test_user:
            print("⚠️  Test kullanıcısı bulunamadı")
            return
        
        print(f"👤 Kullanıcı: {test_user.name} (ID: {test_user.id})")
        
        alarms_status = await smart_service.get_user_active_alarms_status(
            db=db,
            user_id=test_user.id
        )
        
        print(f"\n📊 Toplam {len(alarms_status)} alarm bulundu")
        
        for alarm in alarms_status:
            print(f"\n   Alarm: {alarm['alarm_name']}")
            print(f"   Durum: {alarm['status']}")
            print(f"   Mesaj: {alarm['message']}")
            print(f"   Hatlar: {', '.join([r['hat_kodu'] for r in alarm['routes']])}")
        
        print()
        
    except Exception as e:
        print(f"❌ Durum kontrolü hatası: {e}")
        import traceback
        traceback.print_exc()
        print()
    finally:
        db.close()


def test_cleanup():
    """Clean up test data"""
    print("=" * 60)
    print("TEST 6: Temizlik (Opsiyonel)")
    print("=" * 60)
    
    response = input("Test verilerini silmek ister misiniz? (y/N): ").strip().lower()
    
    if response == 'y':
        db = SessionLocal()
        try:
            # Delete test alarms
            test_user = db.query(User).filter(User.email == "test@example.com").first()
            
            if test_user:
                deleted_alarms = db.query(UserTransportAlarm).filter(
                    UserTransportAlarm.user_id == test_user.id
                ).delete()
                
                db.commit()
                print(f"✅ {deleted_alarms} test alarmı silindi")
            
            print("✅ Temizlik tamamlandı")
        except Exception as e:
            print(f"❌ Temizlik hatası: {e}")
        finally:
            db.close()
    else:
        print("⏭️  Temizlik atlandı")
    
    print()


async def main():
    """Main test runner"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 10 + "SMART TRANSPORT ALARM - TEST SUITE" + " " * 13 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    # Run tests
    await test_ibb_api()
    test_database_schema()
    alarm_id = await test_smart_alarm_creation()
    await test_alarm_check(alarm_id)
    await test_user_alarms_status()
    test_cleanup()
    
    # Summary
    print("=" * 60)
    print("TEST ÖZET")
    print("=" * 60)
    print("✅ Tüm testler tamamlandı!")
    print()
    print("Sonraki Adımlar:")
    print("1. Frontend'i başlat: cd frontend && npm run dev")
    print("2. Backend'i başlat: cd backend && uvicorn main:app --reload")
    print("3. http://localhost:5173 adresine git")
    print("4. Login ol ve Dashboard'a git")
    print("5. 'YENİ ALARM' butonuna tıkla ve test et")
    print()
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())

