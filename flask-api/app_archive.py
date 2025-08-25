from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import os
import logging
import json
from datetime import datetime
import uuid

from ressources import ressource_bp

# Initialisation
app = Flask(__name__)
CORS(app)
app.register_blueprint(ressource_bp, url_prefix="/ressources")

# --------------------
# Logger
# --------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --------------------
# Contexte global pour les templates Jinja2
# --------------------
@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# --------------------
# Connexion DB
# --------------------
def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME", "chessdb"),
        user=os.getenv("DB_USER", "chessplorer"),
        password=os.getenv("DB_PASS", "securepass"),
        host=os.getenv("DB_HOST", "postgres"),
        port=os.getenv("DB_PORT", 5432)
    )

# --------------------
# ROUTES VIDÉOS (prefixées)
# --------------------

@app.route("/videos-home")
def videos_home():
    return render_template("videos/home.html")

@app.route('/auteurs')
def list_auteurs():
    page = int(request.args.get('page', 1))
    limit = 50
    offset = (page - 1) * limit

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM auteurs ORDER BY nom LIMIT %s OFFSET %s", (limit, offset))
    auteurs = cur.fetchall()
    cur.execute("SELECT COUNT(*) FROM auteurs")
    total = cur.fetchone()[0]
    cur.close()
    conn.close()

    return render_template('videos/auteurs.html', auteurs=auteurs, page=page, total=total, limit=limit)

@app.route('/auteur/<uuid:id>', methods=['GET', 'POST'])
def edit_auteur(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    if request.method == 'POST':
        nom = request.form['nom']
        score_moyen = float(request.form['score_moyen'])
        cur.execute("UPDATE auteurs SET nom = %s, score_moyen = %s WHERE id = %s", (nom, score_moyen, str(id)))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('list_auteurs'))

    cur.execute("SELECT * FROM auteurs WHERE id = %s", (str(id),))
    auteur = cur.fetchone()
    cur.close()
    conn.close()

    return render_template('videos/edit_auteur.html', auteur=auteur)

@app.route('/videos')
def list_videos():
    source_id = request.args.get('source_id')

    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if source_id:
        cur.execute("""
            SELECT v.id, v.titre, v.score_utilite, v.youtube_id, a.nom AS auteur_nom
            FROM videos v
            LEFT JOIN auteurs a ON v.auteur_id = a.id
            WHERE v.source_id = %s
            ORDER BY v.timestamp_import DESC
        """, (str(source_id),))
    else:
        cur.execute("""
            SELECT v.id, v.titre, v.score_utilite, v.youtube_id, a.nom AS auteur_nom
            FROM videos v
            LEFT JOIN auteurs a ON v.auteur_id = a.id
            ORDER BY v.timestamp_import DESC
        """)

    videos = cur.fetchall()
    cur.execute("SELECT * FROM sources_import ORDER BY nom")
    sources = cur.fetchall()
    cur.close()
    conn.close()

    return render_template('videos/videos.html', videos=videos, sources=sources, selected_source=source_id)

@app.route('/video/<uuid:id>')
def zoom_video(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    cur.execute("""
        SELECT v.*, a.nom AS auteur_nom, s.nom AS source_nom
        FROM videos v
        LEFT JOIN auteurs a ON v.auteur_id = a.id
        LEFT JOIN sources_import s ON v.source_id = s.id
        WHERE v.id = %s
    """, (str(id),))
    video = cur.fetchone()

    similar = video['similar_videos'] if video and video['similar_videos'] else []
    cur.close()
    conn.close()

    return render_template('videos/zoom_video.html', video=video, similar=similar)

# --------------------
# ROUTES EXISTANTES (questions, ressources, admin)
# --------------------
# ... (tout ton historique inchangé ici)
# Voir message précédent pour éviter le doublon.

# --------------------
# PAGE D’ACCUEIL CHESSPLORER
# --------------------
@app.route("/")
def home():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
