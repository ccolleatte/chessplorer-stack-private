#!/bin/bash

# Variables
BACKUP_DIR="/root/chessplorer/backups/n8n"
SOURCE_DIR="/root/chessplorer/n8n_data"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
ARCHIVE_NAME="n8n_backup_$TIMESTAMP.tar.gz"

# Créer le dossier de sauvegarde s'il n'existe pas
mkdir -p "$BACKUP_DIR"

# Sauvegarde
tar -czf "$BACKUP_DIR/$ARCHIVE_NAME" -C "$SOURCE_DIR" .

# Rotation : garder les 7 dernières sauvegardes
cd "$BACKUP_DIR"
ls -tp | grep -v '/$' | tail -n +8 | xargs -r rm --

echo "Backup completed: $ARCHIVE_NAME"
