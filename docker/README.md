# 🐳 EyeCare Docker

Bitta buyruq bilan hammasi ishga tushadi!

## 🚀 Ishga Tushirish

```bash
# 1. Frontend build qilish
cd frontend
npm install
npm run build

# 2. Docker ishga tushirish
cd ../docker
docker-compose up -d
```

**Tayyor!** 
- Frontend: http://localhost
- API: http://localhost/api/
- API Docs: http://localhost/docs

## 📁 Struktura

```
docker/
├── docker-compose.yml      # Barcha servislar
├── backend.Dockerfile      # Backend image
├── nginx/
│   └── nginx.conf          # Nginx (frontend + API proxy)
├── ssl/                    # SSL sertifikatlar (optional)
└── .env.example            # Environment namunasi
```

## 📋 Servislar

| Servis | Port | Tavsif |
|--------|------|--------|
| `nginx` | 80 | Frontend + API Proxy |
| `api` | 8000 | FastAPI Backend |
| `db` | 5432 | PostgreSQL |
| `redis` | 6379 | Redis Cache |

## 🔧 Buyruqlar

```bash
# Ishga tushirish
docker-compose up -d

# To'xtatish
docker-compose down

# Loglarni ko'rish
docker-compose logs -f

# API loglar
docker-compose logs -f api

# Qayta build
docker-compose up -d --build

# Bazani migration
docker-compose exec api alembic upgrade head
```

## ⚙️ Environment

`.env` fayl yarating:

```bash
SECRET_KEY=your-secret-key
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_WEBAPP_URL=https://eyecare.uz
```
