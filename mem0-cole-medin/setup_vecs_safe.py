import os, time, psycopg2
URL=os.getenv("DATABASE_URL","postgresql://supabase_auth_admin:securepass@chessplorer-supabase-db:5432/postgres?sslmode=disable")
def wait(max_attempts=30):
    for i in range(max_attempts):
        try:
            psycopg2.connect(URL, connect_timeout=2).close()
            print("✅ PostgreSQL prêt"); return True
        except psycopg2.OperationalError as e:
            print(f"⏳ Attente PostgreSQL... ({i+1}/{max_attempts}) - {e}"); time.sleep(2)
    print("❌ Timeout PostgreSQL"); return False
def ensure():
    if not wait(): return False
    conn=psycopg2.connect(URL); cur=conn.cursor()
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
    cur.execute("CREATE SCHEMA IF NOT EXISTS vecs;")
    cur.execute("CREATE TABLE IF NOT EXISTS vecs._meta (key TEXT PRIMARY KEY, value TEXT);")
    cur.execute("CREATE TABLE IF NOT EXISTS vecs.collections (name TEXT PRIMARY KEY, dimension INTEGER NOT NULL, is_index_enabled BOOLEAN NOT NULL DEFAULT FALSE, created_at TIMESTAMPTZ DEFAULT NOW());")
    cur.execute("CREATE TABLE IF NOT EXISTS vecs.memories (id BIGSERIAL PRIMARY KEY, vec vector(1536), metadata JSONB);")
    cur.execute("CREATE INDEX IF NOT EXISTS memories_vec_idx ON vecs.memories USING hnsw (vec vector_cosine_ops);")
    cur.execute("INSERT INTO vecs._meta (key,value) VALUES ('version','0.4.5'),('created_at',NOW()::TEXT) ON CONFLICT (key) DO NOTHING;")
    cur.execute("INSERT INTO vecs.collections (name,dimension) VALUES ('memories',1536) ON CONFLICT (name) DO NOTHING;")
    conn.commit(); cur.close(); conn.close()
    print("✅ Tables vecs OK"); return True
if __name__=='__main__':
    if not ensure(): print("❌ Échec initialisation vecs"); exit(1)
    print("🎉 Vecs initialisé avec succès")
