# VTYS Project - Menager APP 🚀

Menager APP, kullanıcıların günlük finansal yönetimlerini (giderler ve hedefler), piyasa analizlerini ve ulaşım planlamalarını tek bir platform üzerinden yönetmelerini sağlayan kapsamlı bir Veri Tabanı Yönetim Sistemleri (VTYS) projesidir.

## 🌟 Temel Özellikler

- **Finansal Yönetim**: Gelir/gider takibi ve finansal hedef belirleme.
- **Akıllı Piyasa Analizi**: Altın ve Döviz kurlarının takibi, tarihsel olaylarla korelasyon analizi ve gelecek tahminleri.
- **Haber Entegrasyonu**: NewsAPI üzerinden güncel ekonomi haberlerinin takibi ve piyasa üzerindeki etkilerinin analizi.
- **Ulaşım Rehberi**: Otobüs hatları, kalkış saatleri ve durağa varış süresine göre dinamik alarm sistemi.
- **Kullanıcı Paneli**: Kişiselleştirilmiş dashboard ve gerçek zamanlı bildirimler.

## 🛠 Teknoloji Yığını

### Backend
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Veritabanı**: [PostgreSQL](https://www.postgresql.org/) (TimescaleDB eklentisi ile zaman serisi verileri için optimize edilmiştir)
- **ORM**: [SQLAlchemy](https://www.sqlalchemy.org/)
- **Görev Zamanlayıcı**: [APScheduler](https://apscheduler.readthedocs.io/) (Piyasa verilerini periyodik çekmek için)

### Frontend
- **Framework**: [React](https://reactjs.org/) (Vite ile)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **State Management**: React Hooks & Context API
- **İkonlar**: Lucide React

### DevOps & Diğer
- **Konteynerleştirme**: Docker & Docker Compose
- **API'ler**: Yahoo Finance (Piyasa verileri), NewsAPI (Haberler), Etkinlik.io (Etkinlikler)

## 🚀 Proje Kurulumu ve Çalıştırma

Projenin yerelinizde çalışması için Docker Desktop'ın kurulu olması önerilir.

1. **Depoyu Klonlayın**:
   ```bash
   git clone https://github.com/vtys-project-menager-app/Menager-APP.git
   cd Menager-APP
   ```

2. **Ortam Değişkenlerini Ayarlayın**:
   `.env.example` dosyasını `.env` olarak kopyalayın ve gerekli API anahtarlarını girin.

3. **Docker ile Başlatın**:
   ```bash
   docker-compose up --build
   ```

4. **Erişim**:
   - Frontend: `http://localhost:5173`
   - Backend API: `http://localhost:8000`
   - API Dokümantasyonu (Swagger): `http://localhost:8000/docs`

## 📊 Veritabanı Yapısı

Proje, ilişkisel veritabanı modelini (RDBMS) temel alır. Ana tablolarımız:
- `users`: Kullanıcı bilgileri.
- `expenses` & `goals`: Finansal veriler.
- `market_data`: Zaman serisi piyasa verileri.
- `historical_events`: Geçmiş ekonomik/politik olaylar.
- `transport_routes`: Ulaşım verileri.

---
© 2025 VTYS Project Team
