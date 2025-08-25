#!/bin/bash
set -e

echo "🚀 Démarrage Cole Medin avec vérification sécurisée..."

# Initialiser vecs de façon sécurisée
python setup_vecs_safe.py

if [ $? -eq 0 ]; then
    echo "✅ Vecs initialisé - Démarrage Streamlit..."
    streamlit run iterations/v3-streamlit-supabase-mem0.py --server.port 8501 --server.address 0.0.0.0
else
    echo "❌ Échec initialisation vecs - Arrêt"
    exit 1
fi
