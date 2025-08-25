from flask import Blueprint, render_template, request, redirect, url_for, flash
from db import get_db_connection  # on importe depuis db.py
import psycopg2.extras

ressource_bp = Blueprint('ressource_bp', __name__, template_folder='templates')


@ressource_bp.route('/')
def ressource_list():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM ressource ORDER BY id DESC")
    ressources = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('ressource_list.html', ressources=ressources)


@ressource_bp.route('/ressource/new', methods=['GET', 'POST'])
def create_ressource():
    if request.method == 'POST':
        data = request.form
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO ressource (
                titre, type_ressource, url, format, auteur, editeur, langue,
                annee_publication, elo_min, elo_max, duree_etude,
                categorie_tactique, validee
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get("titre"),
            data.get("type_ressource"),
            data.get("url"),
            data.get("format"),
            data.get("auteur"),
            data.get("editeur"),
            data.get("langue"),
            data.get("annee_publication"),
            data.get("elo_min"),
            data.get("elo_max"),
            data.get("duree_etude"),
            data.get("categorie_tactique"),
            'validee' in data
        ))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('ressource_bp.ressource_list'))

    return render_template('ressource_form.html', ressource=None)


@ressource_bp.route('/ressource/<int:id>/edit', methods=['GET', 'POST'])
def edit_ressource(id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    if request.method == 'POST':
        data = request.form
        cur.execute("""
            UPDATE ressource SET
                titre = %s,
                type_ressource = %s,
                url = %s,
                format = %s,
                auteur = %s,
                editeur = %s,
                langue = %s,
                annee_publication = %s,
                elo_min = %s,
                elo_max = %s,
                duree_etude = %s,
                categorie_tactique = %s,
                validee = %s
            WHERE id = %s
        """, (
            data.get("titre"),
            data.get("type_ressource"),
            data.get("url"),
            data.get("format"),
            data.get("auteur"),
            data.get("editeur"),
            data.get("langue"),
            data.get("annee_publication"),
            data.get("elo_min"),
            data.get("elo_max"),
            data.get("duree_etude"),
            data.get("categorie_tactique"),
            'validee' in data,
            id
        ))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('ressource_bp.ressource_list'))

    cur.execute("SELECT * FROM ressource WHERE id = %s", (id,))
    ressource = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('ressource_form.html', ressource=ressource)


@ressource_bp.route('/ressources/delete', methods=['POST'])
def delete_ressources():
    ids = request.form.getlist('delete_ids')
    if ids:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM ressource WHERE id = ANY(%s)", (ids,))
        conn.commit()
        cur.close()
        conn.close()
    return redirect(url_for('ressource_bp.ressource_list'))
