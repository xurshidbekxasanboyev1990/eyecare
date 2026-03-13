# EyeCare Backend

Ko'z salomatligi tekshirish platformasi uchun backend API.

## Texnologiyalar

- **FastAPI** - Web framework
- **PostgreSQL** - Ma'lumotlar bazasi
- **Redis** - Kesh va sessiyalar
- **SQLAlchemy 2.0** - Async ORM
- **Aiogram** - Telegram Bot
- **Docker** - Konteynerizatsiya

## O'rnatish

### 1. Virtual environment yaratish

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 2. Dependencies o'rnatish

```bash
pip install -r requirements.txt
```

### 3. Environment variables

`.env.example` dan `.env` fayl yarating va to'ldiring:

```bash
cp .env.example .env
```

### 4. Ma'lumotlar bazasini yaratish

```bash
# PostgreSQL da database yaratish
createdb eyecare

# Migratsiyalarni ishga tushirish
alembic upgrade head
```

### 5. Ishga tushirish

```bash
# Development
uvicorn app.main:app --reload

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Docker bilan ishga tushirish

### Development

```bash
docker-compose --profile development up -d
```

### Production

```bash
docker-compose --profile production up -d
```

## API Documentation

Ishga tushgandan keyin:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py        # Authentication
│   │   │   ├── users.py       # User management
│   │   │   ├── tests.py       # Test sessions
│   │   │   ├── doctors.py     # Doctors
│   │   │   └── admin.py       # Admin panel
│   │   └── deps.py            # Dependencies
│   │
│   ├── bot/
│   │   ├── handlers.py        # Telegram bot handlers
│   │   └── keyboards.py       # Inline keyboards
│   │
│   ├── core/
│   │   ├── config.py          # Settings
│   │   ├── database.py        # DB connection
│   │   ├── security.py        # JWT & hashing
│   │   └── redis.py           # Redis manager
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── test.py
│   │   ├── doctor.py
│   │   ├── telegram.py
│   │   └── notification.py
│   │
│   ├── schemas/
│   │   ├── user.py
│   │   ├── test.py
│   │   ├── doctor.py
│   │   └── common.py
│   │
│   ├── services/
│   │   ├── test_service.py
│   │   ├── diagnosis_service.py
│   │   ├── notification_service.py
│   │   └── sms_service.py
│   │
│   └── main.py               # Entry point
│
├── alembic/                   # Migrations
├── nginx/                     # Nginx config
├── uploads/                   # Uploaded files
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env.example
```

## Telegram Bot

Bot `/start` komandasi bilan boshlanadi va quyidagi funksiyalarni taqdim etadi:

1. **Ko'z tekshiruvi** - 5 ta kasallik bo'yicha skrining
2. **Testlar** - Web App orqali 10 xil test
3. **Shifokorlar** - Shifokorlar ro'yxati va uchrashuv
4. **Tarix** - Oldingi test natijalari

### Skrining kasalliklari

- Katarakta
- Miopiya
- Glaukoma
- Xorioretinit
- To'r parda distrofiyasi

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | - |
| `REDIS_URL` | Redis connection string | - |
| `SECRET_KEY` | JWT secret key | - |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token | - |
| `TELEGRAM_WEBAPP_URL` | Web App URL | - |
| `DEBUG` | Debug mode | false |

## License

MIT License
