from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Index, TIMESTAMP, Text, Boolean, Date, Enum
from sqlalchemy.orm import relationship
from database import Base
import datetime
import enum

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    work_start_time = Column(String)  # Format: "HH:MM"
    home_location = Column(String)
    work_location = Column(String)

    expenses = relationship("Expense", back_populates="user")
    goals = relationship("Goal", back_populates="user")
    clothing_items = relationship("ClothingItem", back_populates="user")

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    amount = Column(Float)
    category = Column(String)
    date = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="expenses")

class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String)
    target_amount = Column(Float)
    current_amount = Column(Float, default=0.0)
    deadline = Column(DateTime)

    user = relationship("User", back_populates="goals")

class MarketData(Base):
    __tablename__ = "market_data"
    
    time = Column(TIMESTAMP(timezone=True), primary_key=True, nullable=False)
    symbol = Column(String, primary_key=True, nullable=False)
    price = Column(Float, nullable=False)
    volume = Column(Integer, nullable=True)

class HistoricalEvent(Base):
    """Geçmiş önemli olaylar (ekonomik, politik, sosyal)"""
    __tablename__ = "historical_events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    event_date = Column(DateTime, nullable=False, index=True)
    category = Column(String, index=True)  # ekonomik, politik, doğal_afet vb.
    impact_score = Column(Float, default=5.0)  # 1-10 arası
    source = Column(String, default="kaggle")  # Veri kaynağı
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    correlations = relationship("MarketEventCorrelation", back_populates="event")

class MarketEventCorrelation(Base):
    """Olay-piyasa ilişkileri"""
    __tablename__ = "market_event_correlations"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("historical_events.id"), nullable=False)
    symbol = Column(String, nullable=False, index=True)  # GOLD, USD/TRY vb.
    price_before = Column(Float, nullable=False)  # Olay öncesi fiyat
    price_after = Column(Float, nullable=False)  # Olay sonrası fiyat (7 gün sonra)
    percent_change = Column(Float, nullable=False)  # Yüzde değişim
    correlation_strength = Column(Float, default=0.5)  # 0-1 arası ilişki gücü
    days_after = Column(Integer, default=7)  # Kaç gün sonraki fiyat
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    event = relationship("HistoricalEvent", back_populates="correlations")

class CurrentMarketRate(Base):
    """Güncel piyasa kurları - cache için"""
    __tablename__ = "current_market_rates"
    
    symbol = Column(String, primary_key=True)  # GOLD, USDTRY vb.
    name = Column(String, nullable=False)  # "Altın (Ons)", "Dolar/TL" vb.
    price = Column(Float, nullable=False)
    last_updated = Column(DateTime, default=datetime.datetime.utcnow)
    daily_change = Column(Float, default=0.0)  # Günlük değişim
    daily_change_percent = Column(Float, default=0.0)  # Günlük değişim yüzdesi
    previous_close = Column(Float, nullable=True)  # Önceki kapanış

class CurrentEvent(Base):
    """Güncel haberler/olaylar"""
    __tablename__ = "current_events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    published_at = Column(DateTime, nullable=False, index=True)
    category = Column(String, index=True)  # ekonomi, finans, piyasa vb.
    source = Column(String, default="newsapi")
    url = Column(String, nullable=True)
    predicted_impact = Column(Float, default=0.0)  # 0-10 arası tahmin edilen etki
    analyzed = Column(Integer, default=0)  # 0: henüz analiz edilmedi, 1: analiz edildi
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class UpcomingEvent(Base):
    """Gelecekte beklenen önemli olaylar ve AI tavsiyeleri"""
    __tablename__ = "upcoming_events"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    event_date = Column(DateTime, nullable=False, index=True)
    category = Column(String, index=True)
    impact_prediction = Column(String, nullable=True) # "Yüksek Yükseliş Beklentisi"
    ai_advice = Column(Text, nullable=True) # "Daha önceki seçimlerde altın %5 yükselmişti..."
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class TransportRoute(Base):
    """Otobüs hatları ve güzergahları"""
    __tablename__ = "transport_routes"
    
    id = Column(Integer, primary_key=True, index=True)
    route_number = Column(String, nullable=False, index=True)  # "34", "500T" vb.
    route_name = Column(String, nullable=False)  # "Kadıköy - Beylikdüzü"
    departure_location = Column(String, nullable=False)  # "Kadıköy"
    arrival_location = Column(String, nullable=False)  # "Beylikdüzü"
    departure_times = Column(Text, nullable=False)  # JSON array: ["07:00", "07:30", "08:00"]
    active_days = Column(Text, default='[0,1,2,3,4,5,6]')  # 0=Pazartesi, 6=Pazar
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    alarms = relationship("UserTransportAlarm", back_populates="route")

class UserTransportAlarm(Base):
    """Kullanıcı ulaşım alarmları - Akıllı alarm sistemi"""
    __tablename__ = "user_transport_alarms"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    origin_location = Column(String, nullable=True)
    destination_location = Column(String, nullable=True)
    origin_durak_kodu = Column(String, nullable=True)
    destination_durak_kodu = Column(String, nullable=True)
    
    target_arrival_time = Column(String, nullable=True)
    travel_time_to_stop = Column(Integer, nullable=False, default=10)
    
    alarm_enabled = Column(Integer, default=1)
    notification_minutes_before = Column(Integer, default=5)
    
    route_id = Column(Integer, ForeignKey("transport_routes.id"), nullable=True)
    
    alarm_name = Column(String, nullable=True)
    last_triggered = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    user = relationship("User", backref="transport_alarms")
    route = relationship("TransportRoute", back_populates="alarms")
    selected_routes = relationship("AlarmSelectedRoute", back_populates="alarm", cascade="all, delete-orphan")

class AlarmSelectedRoute(Base):
    """Alarm için seçilen otobüs hatları - Birden fazla hat destekleme"""
    __tablename__ = "alarm_selected_routes"
    
    id = Column(Integer, primary_key=True, index=True)
    alarm_id = Column(Integer, ForeignKey("user_transport_alarms.id"), nullable=False)
    hat_kodu = Column(String, nullable=False)
    hat_adi = Column(String, nullable=True)
    tahmini_sure = Column(Integer, nullable=True)
    priority = Column(Integer, default=0)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    alarm = relationship("UserTransportAlarm", back_populates="selected_routes")

class MarketSummary(Base):
    """Piyasa özeti - her saat başı AI tarafından oluşturulan genel bakış"""
    __tablename__ = "market_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    summary_text = Column(Text, nullable=False)
    market_snapshot = Column(Text, nullable=True)
    upcoming_events_snapshot = Column(Text, nullable=True)
    news_snapshot = Column(Text, nullable=True)
    advice_text = Column(Text, nullable=True)
    overall_sentiment = Column(String, default="Neutral")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# --- Sanzo Wada Smart Style Engine Models ---

class PaletteType(str, enum.Enum):
    TWO_COLOR = "2-color"
    THREE_COLOR = "3-color"
    FOUR_COLOR = "4-color"

class ClothingCategory(str, enum.Enum):
    TOP = "Top"
    BOTTOM = "Bottom"
    OUTERWEAR = "Outerwear"
    SHOES = "Shoes"
    ACCESSORY = "Accessory"

class SanzoWadaPalette(Base):
    """Sanzo Wada'nın sözlüğündeki 348 renk kombinasyonu."""
    __tablename__ = "sanzo_wada_palettes"

    id = Column(Integer, primary_key=True, index=True)
    combination_id = Column(Integer, unique=True, index=True) # Repo'daki ID
    combination_type = Column(String) # Enum as string for simplicity in DB, or use Enum type
    colors = Column(Text) # JSON list of hex codes
    name = Column(String, nullable=True)

class ClothingItem(Base):
    """Kullanıcının kişisel gardırobu."""
    __tablename__ = "clothing_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    category = Column(String) # Enum as string
    sub_category = Column(String) # Denim Jacket, T-shirt
    primary_color_hex = Column(String)
    material = Column(String, nullable=True)
    is_favorite = Column(Boolean, default=False)
    last_worn = Column(DateTime, nullable=True)
    image_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="clothing_items")

class UserOutfitLog(Base):
    """Geçmişte giyilen kombinlerin kaydı."""
    __tablename__ = "user_outfit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id")) # Missing in user spec but needed
    date = Column(Date, default=datetime.date.today)
    items = Column(Text) # JSON list of clothing_item_ids
    palette_id = Column(Integer, ForeignKey("sanzo_wada_palettes.id"))

    palette = relationship("SanzoWadaPalette")
