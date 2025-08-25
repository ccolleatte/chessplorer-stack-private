#!/usr/bin/env python3
import psycopg2
import sys

print("🔍 INSPECTION TABLES VECS")
print("="*40)

# Connexion PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port=5433,
    database="postgres", 
    user="supabase_auth_admin",
    password="supabase_auth_password"
)
cur = conn.cursor()

# 1. Contenu table vecs.collections
print("\n📋 CONTENU vecs.collections:")
cur.execute("SELECT * FROM vecs.collections;")
collections = cur.fetchall()
if collections:
    for col in collections:
        print(f"  ✅ {col}")
else:
    print("  ❌ Table vecs.collections VIDE")

# 2. Contenu table vecs.vecs_metadata
print("\n📋 CONTENU vecs.vecs_metadata:")
cur.execute("SELECT * FROM vecs.vecs_metadata;")
metadata = cur.fetchall()
if metadata:
    for meta in metadata:
        print(f"  ✅ {meta}")
else:
    print("  ❌ Table vecs.vecs_metadata VIDE")

# 3. Structure des tables
print("\n🏗️ STRUCTURE vecs.collections:")
cur.execute("""
    SELECT column_name, data_type, is_nullable 
    FROM information_schema.columns 
    WHERE table_schema = 'vecs' AND table_name = 'collections'
    ORDER BY ordinal_position;
""")
for col_info in cur.fetchall():
    print(f"  📝 {col_info[0]} ({col_info[1]}) - Nullable: {col_info[2]}")

print("\n🏗️ STRUCTURE vecs.vecs_metadata:")
cur.execute("""
    SELECT column_name, data_type, is_nullable 
    FROM information_schema.columns 
    WHERE table_schema = 'vecs' AND table_name = 'vecs_metadata'
    ORDER BY ordinal_position;
""")
for col_info in cur.fetchall():
    print(f"  📝 {col_info[0]} ({col_info[1]}) - Nullable: {col_info[2]}")

# 4. SOLUTION - Nettoyer et réinitialiser
print("\n🧹 SOLUTION - RÉINITIALISATION VECS:")
try:
    print("  🗑️ Suppression tables vecs existantes...")
    cur.execute("DROP TABLE IF EXISTS vecs.collections CASCADE;")
    cur.execute("DROP TABLE IF EXISTS vecs.vecs_metadata CASCADE;")
    conn.commit()
    print("  ✅ Tables vecs supprimées")
    
    # Test vecs après nettoyage
    print("  🧪 Test vecs après nettoyage...")
    import vecs
    connection_string = "postgresql://supabase_auth_admin:supabase_auth_password@localhost:5433/postgres"
    client = vecs.create_client(connection_string)
    print("  ✅ Client vecs créé avec succès!")
    
    # Test collection
    collection = client.create_collection(name="test_final", dimension=1536)
    print("  ✅ Collection test créée!")
    
    # Nettoyer
    client.delete_collection("test_final")
    print("  ✅ Collection test supprimée!")
    
    print("\n🎉 VECS RÉINITIALISÉ ET FONCTIONNEL!")
    
except Exception as e:
    print(f"  ❌ Erreur réinitialisation: {e}")

cur.close()
conn.close()
