#!/bin/bash
# ============================================================
# EyeCare - Production Deploy Script
# ============================================================
# Ishlatish: ./deploy.sh [--ssl] [--migrate] [--fresh]
# Misol:     ./deploy.sh --ssl --migrate
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCKER_DIR="$(dirname "${SCRIPT_DIR}")"
PROJECT_DIR="$(dirname "${DOCKER_DIR}")"
COMPOSE_FILE="${DOCKER_DIR}/docker-compose.prod.yml"
ENV_FILE="${DOCKER_DIR}/.env.production"

# Colors
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
BLUE='\033[0;34m'; NC='\033[0m'; BOLD='\033[1m'

log()    { echo -e "${BLUE}[$(date '+%H:%M:%S')]${NC} $*"; }
ok()     { echo -e "${GREEN}✅ $*${NC}"; }
warn()   { echo -e "${YELLOW}⚠️  $*${NC}"; }
error()  { echo -e "${RED}❌ $*${NC}"; exit 1; }

# Args
DO_SSL=false
DO_MIGRATE=false
DO_FRESH=false
for arg in "$@"; do
  case $arg in
    --ssl)     DO_SSL=true ;;
    --migrate) DO_MIGRATE=true ;;
    --fresh)   DO_FRESH=true ;;
  esac
done

echo -e "${BOLD}╔══════════════════════════════════╗${NC}"
echo -e "${BOLD}║   EyeCare Production Deploy      ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════╝${NC}"

# ===== 1. CHECK REQUIREMENTS =====
log "Checking requirements..."
command -v docker  >/dev/null || error "Docker not found"
command -v node    >/dev/null || error "Node.js not found"
command -v git     >/dev/null || error "Git not found"
ok "All requirements met"

# ===== 2. CHECK ENV FILE =====
log "Checking .env.production..."
[[ -f "${ENV_FILE}" ]] || error ".env.production not found! Copy .env.production and fill in values."
source "${ENV_FILE}"
[[ "${SECRET_KEY}" == *"CHANGE_ME"* ]] && error "SECRET_KEY not changed in .env.production!"
[[ "${JWT_SECRET_KEY}" == *"CHANGE_ME"* ]] && error "JWT_SECRET_KEY not changed in .env.production!"
[[ "${POSTGRES_PASSWORD}" == *"CHANGE_ME"* ]] && error "POSTGRES_PASSWORD not changed in .env.production!"
ok ".env.production is valid"

# ===== 3. PULL LATEST CODE =====
log "Pulling latest code..."
cd "${PROJECT_DIR}"
git pull origin main
ok "Code updated"

# ===== 4. BUILD FRONTEND =====
log "Building frontend..."
cd "${PROJECT_DIR}/frontend"
npm ci --prefer-offline
npm run build
ok "Frontend built ($(du -sh dist | cut -f1))"

# ===== 5. SSL CERTIFICATE =====
if [[ "${DO_SSL}" == true ]]; then
  log "Setting up SSL certificate..."
  mkdir -p "${DOCKER_DIR}/ssl"

  if [[ ! -f "${DOCKER_DIR}/ssl/fullchain.pem" ]]; then
    log "Obtaining Let's Encrypt certificate for ${DOMAIN}..."
    docker run --rm \
      -v "${DOCKER_DIR}/ssl:/etc/letsencrypt" \
      -v "/var/www/certbot:/var/www/certbot" \
      -p 80:80 \
      certbot/certbot certonly \
        --standalone \
        --email "${ADMIN_EMAIL}" \
        --agree-tos \
        --no-eff-email \
        -d "${DOMAIN}" \
        -d "www.${DOMAIN}"

    # Copy to nginx ssl dir
    cp "${DOCKER_DIR}/ssl/live/${DOMAIN}/fullchain.pem" "${DOCKER_DIR}/ssl/fullchain.pem"
    cp "${DOCKER_DIR}/ssl/live/${DOMAIN}/privkey.pem"   "${DOCKER_DIR}/ssl/privkey.pem"
    ok "SSL certificate obtained"
  else
    ok "SSL certificate already exists"
  fi
fi

# ===== 6. FRESH INSTALL =====
if [[ "${DO_FRESH}" == true ]]; then
  warn "FRESH install — ALL DATA WILL BE DELETED!"
  read -p "Are you sure? (yes/no): " confirm
  [[ "${confirm}" == "yes" ]] || { log "Cancelled."; exit 0; }
  log "Stopping and removing all containers and volumes..."
  docker compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" down -v
  ok "Old containers removed"
fi

# ===== 7. BUILD & START CONTAINERS =====
log "Building Docker images..."
docker compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" build --no-cache api
ok "Docker image built"

log "Starting containers..."
docker compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" up -d
ok "Containers started"

# ===== 8. WAIT FOR API =====
log "Waiting for API to be ready..."
for i in {1..30}; do
  if docker compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" exec -T api \
      curl -sf http://localhost:8000/health > /dev/null 2>&1; then
    ok "API is ready"
    break
  fi
  [[ $i -eq 30 ]] && { error "API failed to start after 60s! Check logs: docker compose logs api"; }
  sleep 2
done

# ===== 9. DATABASE MIGRATIONS =====
if [[ "${DO_MIGRATE}" == true ]]; then
  log "Running database migrations..."
  docker compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" exec -T api \
    alembic upgrade head
  ok "Migrations applied"
fi

# ===== 10. VERIFY =====
log "Verifying deployment..."
docker compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" ps

HEALTH=$(docker compose -f "${COMPOSE_FILE}" --env-file "${ENV_FILE}" exec -T api \
  curl -sf http://localhost:8000/health | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['status'])" 2>/dev/null || echo "unknown")

echo ""
echo -e "${BOLD}╔══════════════════════════════════════╗${NC}"
echo -e "${BOLD}║      Deployment Summary              ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════╝${NC}"
ok "Deploy completed!"
echo ""
echo -e "  🌐 Frontend:   ${BLUE}https://${DOMAIN}${NC}"
echo -e "  ⚡ API Health: ${BLUE}https://${DOMAIN}/health${NC} → ${GREEN}${HEALTH}${NC}"
echo -e "  🔐 Admin:      ${BLUE}https://${DOMAIN}/admin${NC}"
echo ""
echo -e "  📋 Logs:   docker compose -f docker-compose.prod.yml logs -f"
echo -e "  📊 Status: docker compose -f docker-compose.prod.yml ps"
