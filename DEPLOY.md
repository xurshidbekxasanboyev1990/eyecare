# Deploy

## Talab

- Docker, Docker Compose
- PostgreSQL (tashqi, `president` network'da `pgsql` konteyner)

## DB yaratish

```sql
CREATE USER eyecare WITH PASSWORD 'eyecare123';
CREATE DATABASE eyecare OWNER eyecare;
```

## .env sozlash

Asosiy papkadagi `.env` faylga qo'shish:

```
EYECARE_PORT=8092
EYECARE_DB_USER=eyecare
EYECARE_DB_PASSWORD=eyecare123
EYECARE_DB_NAME=eyecare
EYECARE_SECRET_KEY=<32+ belgili kalit>
EYECARE_JWT_SECRET_KEY=<32+ belgili kalit>
EYECARE_WORKERS=2
EYECARE_APP_URL=https://eye.kuaf.uz
EYECARE_BOT_TOKEN=<telegram bot token>
EYECARE_ADMIN_USER=admin
EYECARE_ADMIN_PASSWORD=<parol>
EYECARE_ADMIN_EMAIL=admin@eyecare.uz
```

## Ishga tushirish

```bash
docker compose up -d --build eyecare_kuaf
```

## Tekshirish

```bash
curl http://localhost:8092/health
curl http://localhost:8092/api/v1/health
```

## Yangilash

```bash
git pull
docker compose up -d --build eyecare_kuaf
```

## Loglar

```bash
docker logs -f eyecare_kuaf
```
