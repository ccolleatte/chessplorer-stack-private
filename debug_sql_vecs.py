#!/usr/bin/env python3
import psycopg2
import logging

print("🔍 DEBUG SQL - Quelle requête échoue ?")
print("="*45)

# Activer logs SQL
logging.basicConfig(level=logging.DEBUG)

# Connexion avec logs activés
conn = psycopg2.connect(
    host="localhost",
    port=5433,
    database="postgres", 
    user="supabase_auth_admin",
    password="supabase_auth_password"
)

# Activer les logs de requêtes dans PostgreSQL
cur = conn.cursor()
cur.execute("SET log_statement = 'all';")
cur.execute("SET log_min_duration_statement = 0;")
conn.commit()

print("📋 Logs PostgreSQL activés")

# Maintenant tester vecs avec logs
print("🧪 Test vecs avec logs SQL...")
try:
    import vecs
    connection_string = "postgresql://supabase_auth_admin:supabase_auth_password@localhost:5433/postgres"
    
    # Cette ligne va loguer TOUTES les requêtes SQL
    client = vecs.create_client(connection_string)
    print("✅ Success!")
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    print("📋 Vérifiez les logs PostgreSQL pour voir la requête qui échoue")

cur.close()
conn.close()
