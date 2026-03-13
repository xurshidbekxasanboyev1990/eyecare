# EyeCare - Ko'z Salomatligi Platformasi

Ko'z tekshiruvi va sog'liqni saqlash platformasi.

## Strukturasi

```
eyecare/
├── backend/          # FastAPI backend
│   ├── app/          # API, bot, models, services
│   ├── alembic/      # DB migratsiyalar
│   └── requirements.txt
├── frontend/         # Vue 3 PWA
│   ├── src/          # Components, views, stores
│   └── vite.config.js
├── Dockerfile        # Multi-stage build
├── nginx.conf        # Nginx config
├── supervisord.conf  # Process manager
└── entrypoint.sh     # Container startup
```

## Texnologiyalar

| Frontend | Backend |
|----------|---------|
| Vue 3 | FastAPI |
| Vite | SQLAlchemy |
| Pinia | PostgreSQL |
| TailwindCSS | Aiogram |
| PWA | Alembic |

## Deploy

[DEPLOY.md](DEPLOY.md) ga qarang.
