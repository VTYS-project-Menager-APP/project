# 🚀 Akıllı Ulaşım Alarmı - Hızlı Başlangıç

## 📦 Kurulum (5 Dakika)

### 1. Database Migration

```bash
cd "/Users/miran/Menager APP/backend"

# PostgreSQL migration'ı çalıştır
psql -U postgres -d menager_db -f migrations/001_smart_transport_alarm.sql
```

**Beklenen Çıktı:**
```
CREATE TABLE
ALTER TABLE
CREATE INDEX
...
```

### 2. Python Bağımlılıkları

```bash
# httpx kütüphanesini ekle (İBB API için gerekli)
pip install httpx
```

### 3. Test Et

```bash
# Test script'i çalıştır
python test_smart_transport.py
```

**Beklenen Çıktı:**
```
╔══════════════════════════════════════════════════════════╗
║          SMART TRANSPORT ALARM - TEST SUITE             ║
╚══════════════════════════════════════════════════════════╝

============================================================
TEST 1: İBB API Bağlantısı
============================================================
✅ İBB API bağlantısı başarılı!
...
```

## 🎮 Kullanım (İlk Alarm)

### 1. Uygulamayı Başlat

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

### 2. Tarayıcıda Aç

```
http://localhost:5173
```

### 3. İlk Alarmını Kur

1. **Dashboard'a git**
2. **"Akıllı Ulaşım Alarmları"** bölümüne in
3. **"YENİ ALARM"** butonuna tıkla
4. Formu doldur:

```
Alarm Adı: İşe Gidiş
Başlangıç: Kadıköy İskele
Hedef: Zincirlikuyu
Başlangıç Durak Kodu: 104803
Hedef Durak Kodu: 100455
[HATLARI BUL] -> Tıkla
Hatları Seç: 34, 34A, 34AS
Varış Saati: 09:00
Yürüme Süresi: 10 dakika
```

5. **"ALARMI OLUŞTUR"** butonuna tıkla
6. ✅ **Alarm oluşturuldu!**

### 4. Test Et

Alarmın tetiklenmesini test etmek için:

```
Varış Saati: [Şimdiden 15 dakika sonrası]
```

Örneğin şimdi saat **14:30** ise, varış saatini **14:45** yap.

Sistem:
- ⏱️ 30 saniyede bir kontrol eder
- 🚨 Uygun zamanda alarm çalar
- 📢 "HEMEN ÇIKMAN GEREK!" mesajı gösterir

## 🔍 API Test (Postman / cURL)

### Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpassword"
  }'
```

**Yanıt:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Alarm Oluştur

```bash
TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."  # Yukarıdaki token'ı buraya yapıştır

curl -X POST http://localhost:8000/api/v1/transport/smart/alarms \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "alarm_name": "İşe Gidiş",
    "origin_location": "Kadıköy",
    "destination_location": "Levent",
    "origin_durak_kodu": "104803",
    "destination_durak_kodu": "100455",
    "target_arrival_time": "09:00",
    "travel_time_to_stop": 10,
    "selected_hat_kodlari": ["34", "34A", "34AS"]
  }'
```

### Alarmları Listele

```bash
curl -X GET http://localhost:8000/api/v1/transport/smart/alarms \
  -H "Authorization: Bearer $TOKEN"
```

### Aktif Alarm Kontrolü

```bash
curl -X GET http://localhost:8000/api/v1/transport/smart/check-active \
  -H "Authorization: Bearer $TOKEN"
```

## 🎯 İBB Durak Kodları Bulma

### Yöntem 1: İETT Mobil Uygulaması

1. İETT uygulamasını indir
2. Durak ara
3. Durak detayına gir
4. **Durak Kodu** görünecek (örn: 104803)

### Yöntem 2: İETT Web Sitesi

```
https://www.iett.istanbul/tr/main/hatlar
```

1. Hat seç
2. Güzergahı gör
3. Durak kodlarını not et

### Yöntem 3: API ile Arama (Gelişmiş)

```bash
# Örnek durak kodu: 104803 (Kadıköy İskele)
curl https://api.ibb.gov.tr/iett/DurakDetay?durakKodu=104803
```

## 🐛 Sorun Giderme

### Problem 1: Migration hatası

**Hata:**
```
psql: FATAL: database "menager_db" does not exist
```

**Çözüm:**
```bash
# Database oluştur
createdb -U postgres menager_db

# Tekrar dene
psql -U postgres -d menager_db -f migrations/001_smart_transport_alarm.sql
```

### Problem 2: "httpx module not found"

**Çözüm:**
```bash
pip install httpx
```

### Problem 3: Alarm ses çalmıyor

**Çözüm:**
1. Tarayıcı ayarlarından ses iznini kontrol et
2. F12 -> Console'da hata var mı kontrol et
3. Tarayıcıyı yenile (Ctrl+Shift+R)

### Problem 4: İBB API yanıt vermiyor

**Çözüm:**
1. İnternet bağlantısını kontrol et
2. API'yi manuel test et:
   ```bash
   curl https://api.ibb.gov.tr/iett/FiloDurum/SeferGerceklesme?hatKodu=34
   ```
3. API geçici olarak kapalı olabilir, birkaç dakika sonra tekrar dene

## 📊 Test Senaryoları

### Senaryo 1: Hızlı Test (2 dakika)

```
1. Alarm oluştur
2. Varış saati: Şimdiden 5 dakika sonra
3. Bekle
4. ✅ Alarm çalmalı
```

### Senaryo 2: Gerçek Senaryo (Sabah)

```
1. Alarm oluştur
2. Varış saati: 09:00 (işe başlama saatin)
3. Hatlar: Kullandığın gerçek hatlar
4. Yürüme süresi: Gerçek yürüme süren
5. ✅ Sabah alarm seni uyandırmalı
```

### Senaryo 3: Çoklu Hat

```
1. Alarm oluştur
2. 3-4 farklı hat seç
3. Herhangi biri uygun zamanda kalkarsa alarm çalsın
4. ✅ Alternatif rotalar çalışmalı
```

## 📱 Mobil Test

Tarayıcıda **Responsive Mode**'a geç (F12 -> Toggle Device Toolbar):

```
iPhone 12 Pro: 390 x 844
Samsung Galaxy S21: 360 x 800
```

UI'ın düzgün görünmesi lazım:
- ✅ Alarm kartları 1 sütun
- ✅ Form alanları düzgün hizalı
- ✅ Butonlar tıklanabilir boyutta

## 🎉 Başarı Kriterleri

Eğer bunlar çalışıyorsa, sistem hazır:

- [ ] Backend başlıyor (port 8000)
- [ ] Frontend başlıyor (port 5173)
- [ ] Database migration başarılı
- [ ] Alarm oluşturulabiliyor
- [ ] Alarm listesi görünüyor
- [ ] Test alarm tetikleniyor (5 dk test)
- [ ] Ses çalıyor
- [ ] Bildirim ekranı gösteriliyor

## 🚀 Production'a Alma

### 1. Environment Variables

```bash
# .env dosyası oluştur
IBB_API_KEY=your_api_key_if_needed
ALARM_CHECK_INTERVAL=30  # saniye
```

### 2. Güvenlik

```python
# Rate limiting ekle
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@router.get("/alarms")
@limiter.limit("10/minute")
async def get_alarms():
    ...
```

### 3. Monitoring

```python
# Sentry ekle
import sentry_sdk

sentry_sdk.init(
    dsn="your-sentry-dsn",
    traces_sample_rate=1.0
)
```

## 📞 Destek

Sorun yaşarsan:

1. **Logları kontrol et:**
   ```bash
   # Backend logs
   tail -f backend/logs/app.log
   
   # Frontend console
   F12 -> Console
   ```

2. **Test script çalıştır:**
   ```bash
   python test_smart_transport.py
   ```

3. **GitHub Issue aç:**
   - Hata mesajını yapıştır
   - Test çıktısını ekle
   - Ekran görüntüsü ekle

---

**🎊 Başarılar! Artık akıllı ulaşım alarmın hazır!**

