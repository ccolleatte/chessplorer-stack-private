FROM python:3.12-slim

# Répertoire de travail
WORKDIR /app

# Dépendances système
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Copie ciblée des fichiers nécessaires
COPY requirements.txt .
COPY main.py .
COPY wait-for-qdrant.sh .
COPY alembic.ini .
COPY app ./app
COPY alembic ./alembic

# Installation des dépendances Python
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir openai



# Rendre exécutable
RUN chmod +x wait-for-qdrant.sh

# Entrée du conteneur
ENTRYPOINT ["./wait-for-qdrant.sh"]

# Commande de lancement FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
