#!/bin/bash
set -euo pipefail

until python -c "
import asyncio, asyncpg, os, sys, re
async def check():
    url = os.environ.get('DATABASE_URL', '').replace('postgresql+asyncpg://', 'postgresql://')
    m = re.match(r'postgresql://([^:]+):([^@]+)@([^:/]+):?(\d+)?/(.+)', url)
    if not m:
        sys.exit(1)
    user, password, host, port, db = m.groups()
    port = int(port or 5432)
    try:
        conn = await asyncpg.connect(host=host, port=port, user=user, password=password, database=db)
        await conn.close()
    except:
        sys.exit(1)
asyncio.run(check())
" 2>/dev/null; do
    sleep 2
done

cd /app
alembic upgrade head || true

export WORKERS=${WORKERS:-2}
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/eyecare.conf
