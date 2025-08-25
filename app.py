from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for
import psycopg2
import psycopg2.extras
import uuid

app = Flask(__name__)

# --------------------
# Contexte pour les templates Jinja
# --------------------

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

# --------------------
# Configuration DB
# --------------------

def get_db_connection():
    conn = psycopg2.connect(
        host='postgres',
        database='chessdb',
        user='chessplorer',
        password='securepass'
    )
    return conn

# --------------------
# Routes
# --------------------

@app.route('/')
def home():
    return redirect(url_for('list_videos'))

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

    return render_template('auteurs.html', auteurs=auteurs, page=page, total=total, limit=limit)

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

    return render_template('edit_auteur.html', auteur=auteur)

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

    return render_template('videos.html', videos=videos, sources=sources, selected_source=source_id)

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

    return render_template('zoom_video.html', video=video, similar=similar)

# --------------------
# Main
# --------------------

app.config['DEBUG'] = True

