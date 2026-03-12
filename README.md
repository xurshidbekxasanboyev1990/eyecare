# 👁️ EyeCare - Ko'z Salomatligi Platformasi

Professional ko'z tekshiruvi va sog'liqni saqlash platformasi.

## 📁 Loyiha Strukturasi

```
eyecare/
├── backend/                 # 🐍 Python FastAPI Backend
│   ├── app/                 # Asosiy dastur kodi
│   │   ├── api/             # API routes
│   │   ├── bot/             # Telegram bot
│   │   ├── core/            # Konfiguratsiya, DB, Security
│   │   ├── models/          # SQLAlchemy modellari
│   │   ├── schemas/         # Pydantic schemalar
│   │   └── services/        # Biznes logika
│   ├── docs/                # API dokumentatsiyalari
│   ├── alembic/             # Database migratsiyalar
│   └── requirements.txt     # Python paketlar
│
├── frontend/                # 🖼️ Vue.js PWA Frontend
│   ├── src/
│   │   ├── components/      # Vue komponentlar
│   │   ├── views/           # Sahifalar
│   │   ├── stores/          # Pinia stores
│   │   ├── router/          # Vue Router
│   │   └── assets/          # Rasmlar, CSS
│   ├── public/              # Statik fayllar
│   ├── package.json         # NPM paketlar
│   └── vite.config.js       # Vite konfiguratsiya
│
├── docker/                  # 🐳 Docker konfiguratsiyalar
│   ├── backend.Dockerfile   # Backend image
│   ├── frontend.Dockerfile  # Frontend image
│   ├── docker-compose.yml   # Barcha servislar
│   ├── nginx/               # Nginx configs
│   └── .env.example         # Environment namunasi
│
└── extracted_images/        # Loyiha rasmlari
```

## 🚀 Ishga Tushirish

### Frontend (Vue.js PWA)

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

### Backend (FastAPI)

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API: http://localhost:8000
Docs: http://localhost:8000/docs

### Docker bilan

```bash
# Barcha servislar
docker-compose -f docker/docker-compose.yml up -d

# Development (pgadmin, redis-commander bilan)
docker-compose -f docker/docker-compose.yml --profile development up -d

# Production (nginx, certbot bilan)
docker-compose -f docker/docker-compose.yml --profile production up -d
```

## 📱 Xususiyatlar

### Frontend (PWA)
- ✅ 10 ta ko'z testi
- ✅ Kamera orqali masofa aniqlash
- ✅ PDF natija generatsiyasi
- ✅ Offline qo'llab-quvvatlash
- ✅ Admin panel

### Backend (API)
- ✅ JWT autentifikatsiya
- ✅ Telegram bot integratsiya
- ✅ Mobile app API
- ✅ Shifokorlar bazasi
- ✅ Uchrashuvlar tizimi
- ✅ Push bildirishnomalar

## 🔗 API Dokumentatsiya

- [Mobile API](backend/docs/MOBILE_API_DOCUMENTATION.md)
- [Backend Specification](backend/docs/BACKEND_SPECIFICATION.md)

## 👥 Texnologiyalar

| Frontend | Backend |
|----------|---------|
| Vue 3 | FastAPI |
| Vite | SQLAlchemy |
| Pinia | PostgreSQL |
| TailwindCSS | Redis |
| PWA | Aiogram |

## 📞 Aloqa

- Telegram: @eyecare_support
- Email: support@eyecare.uz
