#!/bin/bash
# ============================================================
# EyeCare - PostgreSQL Backup Script
# ============================================================
# Cron uchun: 0 2 * * * /opt/eyecare/docker/scripts/backup.sh
# ============================================================

set -euo pipefail

# Config
BACKUP_DIR="/backups"
DB_HOST="db"
DB_USER="${POSTGRES_USER:-eyecare_prod}"
DB_NAME="${POSTGRES_DB:-eyecare_production}"
KEEP_DAYS=7
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/eyecare_${DATE}.dump"

echo "📦 Starting backup: ${BACKUP_FILE}"

# Create backup directory
mkdir -p "${BACKUP_DIR}"

# Create backup
pg_dump \
  -h "${DB_HOST}" \
  -U "${DB_USER}" \
  -d "${DB_NAME}" \
  --format=custom \
  --compress=9 \
  --file="${BACKUP_FILE}"

# Check backup size
BACKUP_SIZE=$(du -sh "${BACKUP_FILE}" | cut -f1)
echo "✅ Backup created: ${BACKUP_FILE} (${BACKUP_SIZE})"

# Delete old backups
DELETED=$(find "${BACKUP_DIR}" -name "eyecare_*.dump" -mtime +${KEEP_DAYS} -delete -print | wc -l)
echo "🗑️  Deleted ${DELETED} old backups (older than ${KEEP_DAYS} days)"

# List current backups
echo "📋 Current backups:"
ls -lh "${BACKUP_DIR}"/eyecare_*.dump 2>/dev/null || echo "  (none)"

echo "✅ Backup completed successfully"
