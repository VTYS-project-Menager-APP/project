# 🚌 Akıllı Ulaşım Alarm Sistemi

## 📋 Özellik Özeti

Bu özellik, kullanıcıların İstanbul'daki otobüs hatlarını takip edip, iş yerine zamanında varmak için otomatik alarm kurmasını sağlar. **İBB (İstanbul Büyükşehir Belediyesi) İETT API** entegrasyonu ile gerçek zamanlı otobüs takibi yapılır.

### 🎯 Temel Özellikler

1. **Akıllı Alarm Oluşturma**
   - Kullanıcı hedef varış saatini girer (örn: 09:00)
   - Başlangıç ve hedef konumlarını seçer
   - Birden fazla otobüs hattı seçebilir
   - Sistem otomatik olarak uygun zamanda alarm çalar

2. **Çoklu Hat Desteği**
   - Bir alarm için birden fazla otobüs hattı seçilebilir
   - Seçilen hatlardan herhangi biri uygun zamanda kalkıyorsa alarm tetiklenir
   - Alternatif rotalar için güvenlik sağlar

3. **Gerçek Zamanlı Takip**
   - İBB API'si ile canlı otobüs takibi
   - Sefer gerçekleşme bilgileri
   - Durak bazlı hat arama

4. **Sesli Alarm**
   - Alarm tetiklendiğinde ses çalar
   - Tam ekran bildirim gösterir
   - "Şimdi çıkarsan X saatinde varırsın" mesajı

## 🏗️ Teknik Mimari

### Backend Yapısı

```
backend/
├── services/
│   ├── ibb_transport_service.py       # İBB API entegrasyonu
│   └── smart_transport_service.py     # Akıllı alarm mantığı
├── routers/
│   └── smart_transport.py             # API endpoints
├── models.py                          # Veritabanı modelleri
└── migrations/
    └── 001_smart_transport_alarm.sql  # Migration script
```

### Frontend Yapısı

```
frontend/src/
├── components/
│   ├── SmartTransportContainer.jsx    # Ana alarm yönetim ekranı
│   └── AlarmSound.jsx                 # Sesli alarm bildirimi
└── pages/
    └── Dashboard.jsx                  # Güncellenmiş dashboard
```

## 🗄️ Veritabanı Şeması

### `user_transport_alarms` (Güncellenmiş)

```sql
- id: Primary Key
- user_id: Foreign Key -> users
- alarm_name: VARCHAR (örn: "İşe Gidiş")
- origin_location: VARCHAR (başlangıç adresi)
- destination_location: VARCHAR (hedef adres)
- origin_durak_kodu: VARCHAR (İBB durak kodu)
- destination_durak_kodu: VARCHAR (İBB durak kodu)
- target_arrival_time: VARCHAR (HH:MM formatında)
- travel_time_to_stop: INTEGER (durağa yürüme süresi, dakika)
- alarm_enabled: INTEGER (0/1)
- notification_minutes_before: INTEGER
- last_triggered: TIMESTAMP
```

### `alarm_selected_routes` (Yeni)

```sql
- id: Primary Key
- alarm_id: Foreign Key -> user_transport_alarms
- hat_kodu: VARCHAR (otobüs hat numarası)
- hat_adi: VARCHAR (hat adı)
- tahmini_sure: INTEGER (tahmini yolculuk süresi)
- priority: INTEGER (öncelik sırası)
- is_active: INTEGER (0/1)
```

## 🔌 API Endpoints

### Akıllı Alarm İşlemleri

#### 1. Yeni Alarm Oluştur
```http
POST /api/v1/transport/smart/alarms
Authorization: Bearer <token>

Request Body:
{
  "alarm_name": "İşe Gidiş",
  "origin_location": "Kadıköy",
  "destination_location": "Levent",
  "origin_durak_kodu": "KYK101",
  "destination_durak_kodu": "LVT205",
  "target_arrival_time": "09:00",
  "travel_time_to_stop": 10,
  "selected_hat_kodlari": ["34", "34A", "500T"]
}

Response:
{
  "id": 1,
  "alarm_name": "İşe Gidiş",
  "message": "'İşe Gidiş' alarmı başarıyla oluşturuldu!"
}
```

#### 2. Alarmları Listele
```http
GET /api/v1/transport/smart/alarms
Authorization: Bearer <token>

Response:
[
  {
    "alarm_id": 1,
    "alarm_name": "İşe Gidiş",
    "origin": "Kadıköy",
    "destination": "Levent",
    "target_arrival_time": "09:00",
    "travel_time_to_stop": 10,
    "routes": [
      {"hat_kodu": "34", "hat_adi": "34", "priority": 0},
      {"hat_kodu": "34A", "hat_adi": "34A", "priority": 1}
    ],
    "status": "waiting",
    "message": "✅ 09:00 için hazır. 2 saat 15 dakika sonra.",
    "should_trigger": false,
    "alarm_enabled": true
  }
]
```

#### 3. Aktif Alarm Kontrolü
```http
GET /api/v1/transport/smart/check-active
Authorization: Bearer <token>

Response:
{
  "total_alarms": 2,
  "triggered_alarms": [
    {
      "alarm_id": 1,
      "alarm_name": "İşe Gidiş",
      "hat_kodu": "34",
      "message": "🚨 HEMEN ÇIKMAN GEREK! 34 hattına binersen 09:00'da iş yerindesin!",
      "target_arrival": "09:00"
    }
  ],
  "has_active_trigger": true
}
```

#### 4. Hat Arama
```http
POST /api/v1/transport/smart/routes/search
Authorization: Bearer <token>

Request Body:
{
  "origin_durak_kodu": "KYK101",
  "destination_durak_kodu": "LVT205"
}

Response:
{
  "origin_durak": "KYK101",
  "destination_durak": "LVT205",
  "routes": [
    {"hat_kodu": "34", "hat_adi": "34"},
    {"hat_kodu": "34A", "hat_adi": "34A"},
    {"hat_kodu": "500T", "hat_adi": "500T"}
  ]
}
```

## 🚀 Kurulum ve Çalıştırma

### 1. Database Migration

```bash
cd backend
psql -U postgres -d menager_db -f migrations/001_smart_transport_alarm.sql
```

### 2. Backend Başlatma

```bash
cd backend
pip install httpx  # Yeni bağımlılık
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Başlatma

```bash
cd frontend
npm install
npm run dev
```

### 4. Test

API dokümantasyonuna erişim:
```
http://localhost:8000/docs
```

## 🧪 Test Senaryoları

### Senaryo 1: Basit Alarm Oluşturma

1. Dashboard'a giriş yap
2. "YENİ ALARM" butonuna tıkla
3. Formu doldur:
   - Alarm Adı: "İşe Gidiş"
   - Başlangıç: "Kadıköy"
   - Hedef: "Levent"
   - Durak Kodları: "KYK101", "LVT205"
4. "HATLARI BUL" butonuna tıkla
5. Bulunan hatlardan 2-3 tanesini seç
6. Varış saati: "09:00"
7. Yürüme süresi: "10 dakika"
8. "ALARMI OLUŞTUR" butonuna tıkla
9. ✅ Alarm başarıyla oluşturulmalı

### Senaryo 2: Alarm Tetikleme Testi

1. Bir alarm oluştur (hedef saat: şimdiden 30 dakika sonra)
2. Sistem 30 saniyede bir kontrol eder
3. Alarm zamanı geldiğinde:
   - ✅ Sesli alarm çalar
   - ✅ Tam ekran bildirim gösterilir
   - ✅ "HEMEN ÇIKMAN GEREK!" mesajı görünür
4. "ALARMI KAPAT" butonuna tıklayarak kapatılabilir

### Senaryo 3: Çoklu Hat Testi

1. Alarm oluştur
2. 3 farklı hat seç (34, 34A, 500T)
3. Herhangi bir hat uygun zamanda kalkarsa alarm tetiklenmeli
4. ✅ Alternatif rotalar çalışmalı

## 🔧 Konfigürasyon

### İBB API Ayarları

`backend/services/ibb_transport_service.py` dosyasında:

```python
IBB_BASE_URL = "https://api.ibb.gov.tr"
IETT_FILO_DURUM_URL = f"{IBB_BASE_URL}/iett/FiloDurum"
```

### Alarm Kontrol Sıklığı

Frontend'de `SmartTransportContainer.jsx`:

```javascript
// 30 saniyede bir kontrol
const interval = setInterval(checkActiveAlarms, 30000);
```

Daha sık kontrol için:
```javascript
// 10 saniyede bir kontrol
const interval = setInterval(checkActiveAlarms, 10000);
```

## 📱 Kullanım Akışı

### Kullanıcı Perspektifi

1. **Sabah Alarm Kurma**
   ```
   Kullanıcı: "İşe 09:00'da olmalıyım"
   Sistem: "Hangi otobüs hatlarını kullanıyorsun?"
   Kullanıcı: "34, 34A veya 500T"
   Sistem: "Durağa yürüme süren kaç dakika?"
   Kullanıcı: "10 dakika"
   Sistem: ✅ "Alarm kuruldu! 08:15'te uyarıcam."
   ```

2. **Alarm Tetiklenme**
   ```
   Sistem (08:15): 🚨 "HEMEN ÇIK!"
   Kullanıcı: Alarm sesini duyar
   Ekran: "34 hattına binersen 09:00'da iş yerinde olursun!"
   Kullanıcı: Hemen çıkar
   ```

3. **Alternatif Hat Senaryosu**
   ```
   Sistem: "34 hattı kalktı ama 34A 5 dakika sonra kalkıyor"
   Alarm: Yine tetiklenir
   Mesaj: "5 dakika içinde çıkarsan 34A'ya yetişirsin!"
   ```

## 🛠️ Troubleshooting

### Problem: Alarm tetiklenmiyor

**Çözüm:**
1. Alarmın `alarm_enabled = 1` olduğunu kontrol et
2. Hedef varış saatinin gelecekte olduğunu kontrol et
3. Backend loglarını kontrol et:
   ```bash
   tail -f backend/logs/app.log
   ```

### Problem: İBB API hatası

**Çözüm:**
1. İnternet bağlantısını kontrol et
2. İBB API'sinin çalıştığını test et:
   ```bash
   curl https://api.ibb.gov.tr/iett/FiloDurum/SeferGerceklesme?hatKodu=34
   ```
3. API key gerekiyorsa ekle (şu an gerekmiyor)

### Problem: Ses çalmıyor

**Çözüm:**
1. Tarayıcı ses izinlerini kontrol et
2. Tarayıcı konsolunda hata var mı kontrol et
3. Audio element'i manuel test et:
   ```javascript
   const audio = new Audio('alarm-sound.wav');
   audio.play();
   ```

## 🔮 Gelecek Geliştirmeler

### Versiyon 2.0 İçin Planlar

1. **Gerçek Zamanlı Otobüs Konumu**
   - Otobüsün canlı konumunu göster
   - "X dakika sonra durakta" bilgisi

2. **Akıllı Gecikme Tahmini**
   - Hava durumuna göre gecikme tahmini
   - Trafik yoğunluğu analizi

3. **Haftalık Raporlar**
   - "Bu hafta 5 defa zamanında vardın"
   - "Ortalama yolculuk süren: 35 dakika"

4. **Grup Alarmları**
   - Arkadaşlarınla aynı otobüse bin
   - "Ali de aynı hatta, beraber gidin"

5. **Ses Seçenekleri**
   - Farklı alarm sesleri
   - Kendi sesini kaydet

## 📚 Kaynaklar

- [İBB API Dokümantasyonu](https://api.ibb.gov.tr)
- [FastAPI Dokümantasyonu](https://fastapi.tiangolo.com/)
- [React Hooks Guide](https://react.dev/reference/react)

## 👥 Katkıda Bulunanlar

- Backend API: Python + FastAPI
- Frontend UI: React + TailwindCSS
- Database: PostgreSQL
- Real-time API: İBB İETT API

## 📄 Lisans

Bu proje Menager APP'in bir parçasıdır.

---

**Önemli Not:** Bu özellik İBB'nin açık API'sini kullanır. API kullanım koşullarına uygun olarak kullanılmalıdır. Yüksek trafikli uygulamalarda rate limiting uygulanması önerilir.

