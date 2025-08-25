#!/usr/bin/env python3
import psycopg2
import uuid

print("🔧 SIMULATION VECS.CREATE_CLIENT()")
print("="*40)

conn = psycopg2.connect(
    host="localhost",
    port=5433,
    database="postgres", 
    user="supabase_auth_admin",
    password="supabase_auth_password"
)
cur = conn.cursor()

# Simuler ce que vecs.create_client() fait probablement
print("📋 Tests des requêtes que vecs pourrait faire:")

tests = [
    ("Version PostgreSQL", "SELECT version();"),
    ("Extension vector", "SELECT * FROM pg_extension WHERE extname = 'vector';"),
    ("Schéma vecs", "SELECT * FROM pg_namespace WHERE nspname = 'vecs';"),
    ("Tables vecs", "SELECT * FROM pg_tables WHERE schemaname = 'vecs';"),
    ("Métadonnées vecs", "SELECT * FROM vecs.vecs_metadata;"),
    ("Collections vecs", "SELECT * FROM vecs.collections;"),
    ("Permissions sur vecs", "SELECT has_schema_privilege('vecs', 'USAGE');"),
    ("Test scalar_one() vide", "SELECT * FROM vecs.collections WHERE name = 'nonexistent';")
]

for test_name, query in tests:
    try:
        print(f"\n🧪 {test_name}:")
        cur.execute(query)
        
        if query.startswith("SELECT"):
            results = cur.fetchall()
            if results:
                print(f"  ✅ {len(results)} résultat(s)")
                for result in results[:2]:  # Limite à 2 résultats
                    print(f"    📄 {result}")
            else:
                print("  ❌ AUCUN RÉSULTAT (pourrait être le problème!)")
        else:
            print("  ✅ Requête exécutée")
            
    except Exception as e:
        print(f"  ❌ ERREUR: {e}")

# Test spécifique - reproduire scalar_one() qui échoue
print(f"\n🎯 TEST CRITIQUE - Reproduire scalar_one():")
print("   (Recherche la requête exacte qui cause 'No row was found')")

# Requêtes possibles que vecs.create_client() fait et qui pourraient échouer sur scalar_one()
critical_tests = [
    ("Recherche collection unique", "SELECT * FROM vecs.collections LIMIT 1;"),
    ("Recherche metadata version", "SELECT value FROM vecs.vecs_metadata WHERE key = 'version';"),
    ("Recherche metadata initialized", "SELECT value FROM vecs.vecs_metadata WHERE key = 'initialized';"),
    ("Test table vide collections", "SELECT COUNT(*) FROM vecs.collections;"),
    ("Schema par défaut", "SELECT current_schema();"),
]

for test_name, query in critical_tests:
    try:
        print(f"\n🔍 {test_name}:")
        cur.execute(query)
        
        # Essayer scalar_one() comme vecs le fait
        result = cur.fetchone()
        if result:
            print(f"  ✅ Résultat scalar_one(): {result}")
        else:
            print(f"  ❌ scalar_one() RETOURNE NONE - C'EST LE PROBLÈME!")
            
    except Exception as e:
        print(f"  ❌ ERREUR scalar_one(): {e}")

cur.close()
conn.close()

print(f"\n💡 CONCLUSION:")
print("   La requête qui retourne 'AUCUN RÉSULTAT' ou 'NONE' est celle qui cause l'erreur!")
