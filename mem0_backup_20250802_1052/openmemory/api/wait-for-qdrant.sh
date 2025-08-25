#!/bin/sh
set -e

echo "⏳ Attente de la disponibilité de Qdrant..."

until curl -s -f "${QDRANT_HOST:-http://qdrant:6333}/collections" > /dev/null; do
  echo "🟡 Qdrant non prêt. Nouvelle tentative dans 2s..."
  sleep 2
done

echo "✅ Qdrant est prêt. Lancement de l’application."
exec "$@"
