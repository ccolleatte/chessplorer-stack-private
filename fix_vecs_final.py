#!/usr/bin/env python3
import psycopg2
import sys

print("🧹 NETTOYAGE COMPLET SCHÉMA VECS")
print("="*45)

# Connexion PostgreSQL
conn = psycopg2.connect(
    host="localhost",
    port=5433,
    database="postgres", 
    user="supabase_auth_admin",
    password="supabase_auth_password"
)
cur = conn.cursor()

# 1. Supprimer COMPLÈTEMENT le schéma vecs
print("🗑️ Suppression complète du schéma vecs...")
try:
    cur.execute("DROP SCHEMA IF EXISTS vecs CASCADE;")
    conn.commit()
    print("  ✅ Schéma vecs supprimé complètement")
except Exception as e:
    print(f"  ❌ Erreur suppression: {e}")

# 2. Vérifier que tout est supprimé
print("\n🔍 Vérification suppression...")
cur.execute("SELECT nspname FROM pg_namespace WHERE nspname = 'vecs';")
if cur.fetchall():
    print("  ❌ Schéma vecs encore présent!")
else:
    print("  ✅ Schéma vecs complètement supprimé")

# 3. Test vecs - va recréer le schéma proprement
print("\n🧪 Test vecs - Récréation propre du schéma...")
try:
    import vecs
    connection_string = "postgresql://supabase_auth_admin:supabase_auth_password@localhost:5433/postgres"
    
    print("  🔧 Création client vecs...")
    client = vecs.create_client(connection_string)
    print("  ✅ CLIENT VECS CRÉÉ AVEC SUCCÈS!")
    
    # Test création collection
    print("  🧪 Test création collection...")
    collection = client.create_collection(name="test_success", dimension=1536)
    print("  ✅ Collection test créée!")
    
    # Nettoyer
    client.delete_collection("test_success")
    print("  ✅ Collection test supprimée!")
    
    print("\n🎉 VECS COMPLÈTEMENT FONCTIONNEL!")
    
except Exception as e:
    print(f"  ❌ Erreur vecs: {e}")

# 4. Vérification finale des tables créées
print("\n📋 Vérification tables créées:")
cur.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'vecs';")
tables = cur.fetchall()
for table in tables:
    print(f"  ✅ vecs.{table[0]}")

cur.close()
conn.close()

print("\n🎯 RÉSUMÉ:")
print("  Si vous voyez 'VECS COMPLÈTEMENT FONCTIONNEL!' ci-dessus,")
print("  alors Mem0 devrait maintenant fonctionner!")
