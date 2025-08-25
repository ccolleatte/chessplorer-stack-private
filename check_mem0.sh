#!/bin/bash

set -e

echo "==[ Étape 1 : Conteneur mem0-api actif ]=="
docker ps --format '{{.Names}}' | grep mem0-api || { echo "❌ Conteneur mem0-api non trouvé"; exit 1; }
echo "✅ mem0-api en fonctionnement"

echo "==[ Étape 2 : Accès aux routes FastAPI ]=="
curl -s http://localhost:8000/docs | grep -q "openapi" && echo "✅ Routes FastAPI accessibles" || { echo "❌ L'API ne répond pas sur localhost:8000"; exit 1; }

echo "==[ Étape 3 : Vérification des variables Docker Compose ]=="
grep -E 'POSTGRES_DB|POSTGRES_USER|POSTGRES_PASSWORD' docker-compose.yml

echo "==[ Étape 4 : Connexion à la base chessdb ]=="
POSTGRES_CONTAINER=$(docker ps --format '{{.Names}}' | grep postgres)
[[ -z "$POSTGRES_CONTAINER" ]] && { echo "❌ Conteneur postgres introuvable"; exit 1; }

docker exec -i "$POSTGRES_CONTAINER" psql -U chessplorer -d chessdb <<'EOF'
\dt
EOF

echo "==[ Étape 5 : Vérification de la table users ]=="
docker exec -i "$POSTGRES_CONTAINER" psql -U chessplorer -d chessdb <<'EOF'
SELECT user_id, name FROM users;
EOF || {
  echo "❌ Table 'users' absente ou vide"
  echo "==> Tentative de création d’un utilisateur 'default_user'"

  docker exec -i "$POSTGRES_CONTAINER" psql -U chessplorer -d chessdb <<'EOF'
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
INSERT INTO users (id, user_id, name, created_at, updated_at)
VALUES (
  gen_random_uuid(),
  'default_user',
  'Default User',
  now(),
  now()
);
EOF
}

echo "==[ Étape 6 : Test de création de mémoire ]=="
curl -X POST http://localhost:8000/api/v1/memories/ \
  -H "Content-Type: application/json" \
  -d '{"user_id": "default_user", "text": "Mémoire ajoutée par script"}'

echo "✅ Test terminé"
