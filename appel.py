#!/usr/bin/env python3

import os
from supabase import create_client, Client
from dotenv import load_dotenv

# 🔍 Charge le fichier .env (si tu l'utilises)
load_dotenv()  # Nécessite "pip install python-dotenv"

# Récupère les variables essentielles
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("❌ SUPABASE_URL ou SUPABASE_KEY n’est pas défini")

# Initialise le client Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 1️⃣ Test d’authentification : renvoie None si pas de session active
user = supabase.auth.get_user()
print("auth.get_user() →", user)

# 2️⃣ Test de lecture sur table "users" (remplace par ta table)
resp = supabase.table("users").select("*").limit(1).execute()
print("response.data →", resp.data)
print("response.error →", resp.error)
