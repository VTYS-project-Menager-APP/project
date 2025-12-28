"""
Kaggle Dataset Service - EGPBD (Event-Based Gold Price Benchmark Dataset)
Bu servis Kaggle'dan veri setini yükler ve database'e kaydeder.
"""

import kagglehub
import pandas as pd
from database import SessionLocal
from models import HistoricalEvent, MarketEventCorrelation
import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_kaggle_dataset():
    """
    Kaggle EGPBD dataset'ini yükler ve database'e kaydeder.
    Dataset: waelaletaiwi/egpbd-an-event-based-gold-price-benchmark-dataset
    """
    try:
        logger.info("Kaggle dataset indiriliyor...")
        
        # Dataset yolunu al
        path = kagglehub.dataset_download("waelaletaiwi/egpbd-an-event-based-gold-price-benchmark-dataset")
        file_path = f"{path}/Gold Dataset (Integrated).xlsx"
        
        logger.info(f"Dataset indirildi: {file_path}")
        
        # Excel'i oku (Openpyxl gerekebilir)
        df = pd.read_excel(file_path)
        
        logger.info(f"Dataset yüklendi. Toplam {len(df)} kayıt bulundu.")
        logger.info(f"Sütunlar: {df.columns.tolist()}")
        
        return df
        
    except Exception as e:
        logger.error(f"Kaggle dataset yüklenirken hata: {str(e)}")
        return None


def parse_and_store_dataset(df: pd.DataFrame):
    """
    Pandas DataFrame'i parse edip database'e kaydeder.
    """
    if df is None or df.empty:
        logger.error("DataFrame boş, işlem yapılamıyor.")
        return 0
    
    db = SessionLocal()
    stored_count = 0
    
    try:
        for idx, row in df.iterrows():
            try:
                # Başlık için en anlamlı veriyi bulalım
                title_candidates = [
                    row.get('Economic Data'), 
                    row.get('Politics'),
                    row.get('Job report'),
                    row.get('OPEC'),
                    row.get('oil')
                ]
                
                title = "Piyasa Gelişmesi"
                for cand in title_candidates:
                    if pd.notna(cand) and str(cand).strip() not in ["", "0", "0.0", "nan", "None"]:
                        title = str(cand).strip()
                        break
                
                desc_parts = []
                for col in ['oil', 'OPEC', 'Inflation', 'Job report']:
                    val = row.get(col)
                    if pd.notna(val) and str(val).strip() != "":
                        desc_parts.append(f"{col}: {val}")
                
                description = ", ".join(desc_parts) if desc_parts else "Normal piyasa seyri"
                event_date = parse_date(row.get('Date', datetime.datetime.now()))
                
                event = HistoricalEvent(
                    title=title,
                    description=description,
                    event_date=event_date,
                    category="ekonomik",
                    impact_score=5.0,
                    source="kaggle_egpbd"
                )
                
                db.add(event)
                db.flush()
                
                # Correlation verisini ekle
                price_before = row.get('Gold Price')
                price_after = row.get('Next week gold price')
                
                if pd.notna(price_before) and pd.notna(price_after) and price_before > 0:
                    correlation = MarketEventCorrelation(
                        event_id=event.id,
                        symbol="GOLD",
                        price_before=float(price_before),
                        price_after=float(price_after),
                        percent_change=calculate_percent_change(price_before, price_after),
                        correlation_strength=0.8,
                        days_after=7
                    )
                    db.add(correlation)
                
                stored_count += 1
                
                if stored_count % 500 == 0:
                    logger.info(f"{stored_count} kayıt işlendi...")
                    db.commit()
                
            except Exception as e:
                logger.warning(f"Satır {idx} işlenirken hata: {str(e)}")
                continue
        
        db.commit()
        logger.info(f"Toplam {stored_count} kayıt database'e kaydedildi.")
        
    except Exception as e:
        logger.error(f"Database kayıt hatası: {str(e)}")
        db.rollback()
    finally:
        db.close()
    
    return stored_count


def parse_date(date_value):
    """Farklı tarih formatlarını parse et"""
    if isinstance(date_value, datetime.datetime):
        return date_value
    if isinstance(date_value, str):
        try:
            return pd.to_datetime(date_value)
        except:
            pass
    return datetime.datetime.now()


def calculate_percent_change(before, after):
    """Yüzde değişim hesapla"""
    try:
        before = float(before)
        after = float(after)
        if before == 0:
            return 0
        return ((after - before) / before) * 100
    except:
        return 0.0


if __name__ == "__main__":
    df = load_kaggle_dataset()
    if df is not None:
        stored = parse_and_store_dataset(df)
        print(f"Bitti: {stored} kayıt.")
