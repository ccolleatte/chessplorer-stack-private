#!/bin/bash

# =============================================================================
# SCRIPT DE VÉRIFICATION SANTÉ - STACK CHESSPLORER (avec auto-réparation du schéma auth)
# =============================================================================

echo "🚀 CHESSPLORER - Test de disponibilité des services"
echo "=================================================="
echo ""

# Couleurs pour affichage
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

TOTAL_SERVICES=0
HEALTHY_SERVICES=0
FAILED_SERVICES=0

# Fonctions existantes inchangées
test_service() {
    local service_name=$1
    local test_command=$2
    local description=$4
    TOTAL_SERVICES=$((TOTAL_SERVICES + 1))
    echo -n "🔍 Testing ${service_name}: ${description}... "
    if eval "$test_command" &>/dev/null; then
        echo -e "${GREEN}✅ OK${NC}"
        HEALTHY_SERVICES=$((HEALTHY_SERVICES + 1))
    else
        echo -e "${RED}❌ FAILED${NC}"
        FAILED_SERVICES=$((FAILED_SERVICES + 1))
    fi
}

test_http() {
    local name=$1 url=$2 expected_code=${3:-200}
    test_service "$name" "curl -s -o /dev/null -w '%{http_code}' $url | grep -q $expected_code" "HTTP $expected_code"
}

test_container() {
    local name=$1 container_name=$2
    test_service "$name" "docker ps --filter name=$container_name --filter status=running | grep -q $container_name" "Container running"
}

test_database() {
    local name=$1 container=$2 db_command=$3
    test_service "$name" "docker exec $container $db_command" "Database connectivity"
}

# → Nouvelle fonction : auto‑réparation du schéma auth
repair_auth_schema() {
  echo -n "🛠 Vérification du schéma auth dans Supabase... "
  if docker exec chessplorer-supabase-db psql -U supabase_auth_admin -d postgres \
       -tAc "SELECT EXISTS(SELECT 1 FROM information_schema.schemata WHERE schema_name='auth')" | grep -q t; then
    echo -e "${GREEN}✅ exists${NC}"
  else
    echo -n "${YELLOW}Missing, creating…${NC} "
    docker exec chessplorer-supabase-db psql -U supabase_auth_admin -d postgres \
      -c "CREATE SCHEMA auth;" &>/dev/null
    if [ $? -eq 0 ]; then
      echo -e "${GREEN}✔️ Schema created${NC}"
    else
      echo -e "${RED}❌ Schema creation failed${NC}"
      FAILED_SERVICES=$((FAILED_SERVICES + 1))
    fi
    TOTAL_SERVICES=$((TOTAL_SERVICES + 1))
  fi
}

echo "📊 TESTS DES CONTENEURS"
echo "======================"
test_container "PostgreSQL Principal" "chessplorer-postgres"
test_container "PostgreSQL Supabase" "chessplorer-supabase-db"
test_container "N8N Automation" "chessplorer-n8n"
test_container "Flowise AI" "chessplorer-flowise"
test_container "Qdrant Vector DB" "chessplorer-qdrant"
test_container "Mem0 Streamlit" "chessplorer-mem0-streamlit"
test_container "Flask API" "chessplorer-flask-api"
test_container "Videos UI" "chessplorer-videos-ui"
test_container "Nextcloud" "chessplorer-nextcloud"
test_container "Uptime Kuma" "chessplorer-uptime"
test_container "Supabase Auth" "chessplorer-supabase-auth"

# → Appel automatique à la réparation du schéma auth
repair_auth_schema

test_container "Supabase Studio" "chessplorer-supabase-studio"
test_container "Supabase Meta" "chessplorer-supabase-meta"
test_container "Supabase REST" "chessplorer-supabase-rest"
test_container "Caddy Proxy" "caddy"

echo ""
echo "🌐 TESTS DES SERVICES WEB"
echo "========================"
test_http "N8N Interface" "https://n8n.chessplorer.com"
test_http "Supabase Studio" "https://supabase.chessplorer.com" "307"
test_http "Mem0 Streamlit" "https://mem0.chessplorer.com" "200"
test_http "Flask API" "https://api.chessplorer.com" "401"
test_http "Flowise Local" "http://localhost:3000"
test_http "Videos Interface" "http://localhost:5050" "302"
test_http "Nextcloud" "http://localhost:8080"
test_http "Uptime Kuma" "http://localhost:3001" "302"
test_http "Supabase Studio Local" "http://localhost:54321" "307"

echo ""
echo "🗄️ TESTS DES BASES DE DONNÉES"
echo "============================="
test_database "PostgreSQL Chessplorer" "chessplorer-postgres" "pg_isready -U chessplorer -d chessdb"
test_database "PostgreSQL Supabase" "chessplorer-supabase-db" "pg_isready -U supabase_auth_admin -d postgres"

echo ""
echo "🔌 TESTS DE CONNECTIVITÉ INTERNE"
echo "==============================="
test_service "N8N → PostgreSQL" "docker exec chessplorer-n8n nc -zv chessplorer-postgres 5432"
test_service "Mem0 → Qdrant" "docker exec chessplorer-mem0-streamlit timeout 2 bash -c '</dev/tcp/chessplorer-qdrant/6333'"
test_service "Mem0 → PostgreSQL" "docker exec chessplorer-mem0-streamlit timeout 2 bash -c '</dev/tcp/chessplorer-postgres/5432'"

echo ""
echo "💾 TESTS DES VOLUMES"
echo "==================="
test_service "Volume PostgreSQL" "docker volume inspect chessplorer_pgdata" "exists"
test_service "Volume Qdrant" "docker volume inspect chessplorer_qdrant_data" "exists"
test_service "Volume Caddy" "docker volume inspect chessplorer_caddy_data" "exists"

echo ""
echo "🔍 TESTS FONCTIONNELS"
echo "===================="
test_service "N8N Database Tables" "docker exec chessplorer-postgres psql -U chessplorer -d chessdb -c '\dt' | grep -q execution_entity"
test_service "Chessplorer Tables" "docker exec chessplorer-postgres psql -U chessplorer -d chessdb -c '\dt' | grep -q ressource"

echo ""
echo "📊 RÉSUMÉ FINAL"
echo "==============="
if [ $TOTAL_SERVICES -gt 0 ]; then
    HEALTH_PERCENTAGE=$((HEALTHY_SERVICES * 100 / TOTAL_SERVICES))
else
    HEALTH_PERCENTAGE=0
fi
echo "Total des services testés: $TOTAL_SERVICES"
echo -e "Services OK: ${GREEN}$HEALTHY_SERVICES${NC}"
echo -e "Services en échec: ${RED}$FAILED_SERVICES${NC}"
echo -e "Taux de disponibilité: ${BLUE}$HEALTH_PERCENTAGE%${NC}"
echo ""
if [ $FAILED_SERVICES -eq 0 ]; then
    echo -e "${GREEN}🎉 TOUS LES SERVICES SONT OPÉRATIONNELS !${NC}"
    exit 0
elif [ $HEALTH_PERCENTAGE -ge 80 ]; then
    echo -e "${YELLOW}⚠️ SYSTÈME MAJORITAIREMENT OPÉRATIONNEL${NC}"
    exit 1
else
    echo -e "${RED}🚨 PROBLÈMES CRITIQUES DÉTECTÉS${NC}"
    exit 2
fi
