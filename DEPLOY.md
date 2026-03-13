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

```bash
cp .env.example .env
```

`.env` faylni to'ldiring (DATABASE_URL, SECRET_KEY, JWT_SECRET_KEY, TELEGRAM_BOT_TOKEN).

## Ishga tushirish

```bash
docker compose up -d --build
```

## Tekshirish

```bash
curl http://localhost:8092/health
curl http://localhost:8092/api/v1/health
```

## Yangilash

```bash
git pull
docker compose up -d --build
```

## Loglar

```bash
docker logs -f eyecare_kuaf
```
