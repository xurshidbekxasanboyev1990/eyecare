#!/bin/bash
# ============================================================
# EyeCare Backend - Docker Entrypoint
# 1. Wait for DB
# 2. Run Alembic migrations
# 3. Start uvicorn
# ============================================================

set -euo pipefail

echo "🚀 EyeCare Backend starting..."

# ===== WAIT FOR POSTGRESQL =====
echo "⏳ Waiting for PostgreSQL..."
until python -c "
import asyncio, asyncpg, os, sys
async def check():
    url = os.environ['DATABASE_URL'].replace('postgresql+asyncpg://', 'postgresql://')
    # parse host/port/user/pass/db
    import re
    m = re.match(r'postgresql://([^:]+):([^@]+)@([^:/]+):?(\d+)?/(.+)', url)
    if not m:
        sys.exit(1)
    user, password, host, port, db = m.groups()
    port = int(port or 5432)
    try:
        conn = await asyncpg.connect(host=host, port=port, user=user, password=password, database=db)
        await conn.close()
        print('DB ready')
    except Exception as e:
        sys.exit(1)
asyncio.run(check())
" 2>/dev/null; do
    echo "   DB not ready, retrying in 2s..."
    sleep 2
done
echo "✅ PostgreSQL is ready"

# ===== RUN MIGRATIONS =====
echo "🔄 Running Alembic migrations..."
alembic upgrade head
echo "✅ Migrations complete"

# ===== START SERVER =====
WORKERS=${WORKERS:-4}
echo "⚡ Starting uvicorn with ${WORKERS} workers..."
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers "${WORKERS}" \
    --loop uvloop \
    --access-log \
    --log-level info
