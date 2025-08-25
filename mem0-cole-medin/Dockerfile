FROM python:3.11-slim

WORKDIR /app

# Installer dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Installer dépendances Python
COPY requirements.txt .
RUN pip install -r requirements.txt

# Ajouter psycopg2 pour setup vecs
RUN pip install psycopg2-binary

# Copier code
COPY . .

# Rendre script exécutable
RUN chmod +x start_safe.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Démarrage sécurisé
CMD ["./start_safe.sh"]
