✅ Voici la version 100% Markdown brut, prête à coller telle quelle dans MAINTENANCE.md
markdown
Copier
Modifier
# 🛠 Maintenance & Mises à jour – Chessplorer (Side Project)

Ce projet est auto-hébergé et maintenu de façon défensive. L’objectif est de rester **fonctionnel, sécurisé et à jour sans y passer trop de temps**.

---

## 🔐 Règles générales

- Toutes les versions des services sont **figées dans le `docker-compose.yml`** (`n8n`, `PostgreSQL`, `Caddy`, `Nextcloud`, etc.)
- Aucune mise à jour automatique ne s’exécute (`:latest` non utilisé).
- La veille manuelle est **évitable**, sauf en cas d’annonce publique de faille critique (CVE).

---

## 🗓 Plan de maintenance recommandé

| Fréquence        | Action                                                                          |
|------------------|---------------------------------------------------------------------------------|
| **Quotidien**    | Sauvegarde automatique de `n8n_data` (`backup_n8n.sh`)                         |
| **Hebdomadaire** | Export des workflows `n8n` en JSON (via `n8n export`)                          |
| **Tous les 2 mois** | Session manuelle de mise à jour contrôlée                                     |

---

## 🔁 Procédure de mise à jour (bimensuelle)

1. **Sauvegarder les workflows n8n**

   ```bash
   docker exec chessplorer-n8n n8n export:workflow --all --output=/home/node/.n8n/exported_workflows.json
Sauvegarder les volumes

bash
Copier
Modifier
bash ./scripts/backup_n8n.sh
Tirer les dernières images

bash
Copier
Modifier
docker compose pull
Redémarrer les services

bash
Copier
Modifier
docker compose up -d
Tester les interfaces

https://n8n.chessplorer.com

https://nextcloud.chessplorer.com (ou autre)

Vérifier les logs : docker logs -f chessplorer-n8n

🔔 Surveillance sécurité (low effort)
Abonnement GitHub recommandé :
https://github.com/n8n-io/n8n/releases → Watch > "Releases only"

Check manuel de version :

bash
Copier
Modifier
docker run --rm n8nio/n8n:latest --version
📦 Export automatisé des workflows (optionnel)
Intégrable dans ton script backup_n8n.sh :

bash
Copier
Modifier
docker exec chessplorer-n8n n8n export:workflow --all --output=/home/node/.n8n/exported_workflows.json
Ce fichier est ensuite sauvegardé avec le dossier n8n_data.

📌 Historique des versions
À mettre à jour manuellement à chaque session de maintenance.

Service	Version actuelle	Dernière mise à jour
n8n	1.91.3	YYYY-MM-DD
Postgres	15	YYYY-MM-DD
Caddy	2.7.6	YYYY-MM-DD
Nextcloud	27-apache	YYYY-MM-DD

Fichier généré avec ChatGPT le 22 juin 2025.

yaml
Copier
Modifier

---

Souhaites-tu que je te le place directement sur ton VPS avec un `echo > ~/chessplorer/MAINTENANCE.md` si tu me confirmes le chemin ?







Humanize 346 words
