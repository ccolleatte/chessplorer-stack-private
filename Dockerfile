FROM python:3.11-slim

WORKDIR /app
COPY . /app

# Installation explicite avec contrôle d'erreur
RUN pip install --no-cache-dir flask flask-cors psycopg2-binary && \
    python -c "import flask"

EXPOSE 5000

CMD ["python", "app.py"]
