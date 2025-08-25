-- ============================================
-- SETUP ARCHON + CRAWL4AI DANS SUPABASE EXISTANT
-- ============================================

-- Créer les schémas séparés
CREATE SCHEMA IF NOT EXISTS archon;
CREATE SCHEMA IF NOT EXISTS crawl4ai;

-- ============================================
-- TABLES ARCHON (Knowledge Base & Task Management)
-- ============================================

-- Table pour les projets Archon
CREATE TABLE IF NOT EXISTS archon.projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    user_id UUID,
    settings JSONB DEFAULT '{}'::jsonb
);

-- Table pour les tâches
CREATE TABLE IF NOT EXISTS archon.tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES archon.projects(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed', 'cancelled')),
    priority INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    due_date TIMESTAMPTZ,
    assigned_to UUID,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Table pour la knowledge base
CREATE TABLE IF NOT EXISTS archon.knowledge_base (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES archon.projects(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    content_type TEXT DEFAULT 'text',
    source_url TEXT,
    embedding vector(1536), -- OpenAI embeddings
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Table pour les conversations/sessions
CREATE TABLE IF NOT EXISTS archon.conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES archon.projects(id) ON DELETE CASCADE,
    title TEXT,
    messages JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    user_id UUID,
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Table pour les credentials/API keys (chiffrées)
CREATE TABLE IF NOT EXISTS archon.credentials (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL UNIQUE,
    encrypted_value TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- TABLES CRAWL4AI (Web Crawling & RAG)
-- ============================================

-- Table pour les pages crawlées
CREATE TABLE IF NOT EXISTS crawl4ai.crawled_pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    url TEXT NOT NULL,
    title TEXT,
    content TEXT NOT NULL,
    cleaned_content TEXT,
    markdown_content TEXT,
    extracted_content JSONB DEFAULT '{}'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    embedding vector(1536), -- OpenAI embeddings
    crawled_at TIMESTAMPTZ DEFAULT NOW(),
    status TEXT DEFAULT 'success' CHECK (status IN ('success', 'failed', 'pending')),
    error_message TEXT,
    content_hash TEXT, -- Pour éviter les doublons
    UNIQUE(url, content_hash)
);

-- Table pour les sessions de crawling
CREATE TABLE IF NOT EXISTS crawl4ai.crawl_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    base_url TEXT NOT NULL,
    max_depth INTEGER DEFAULT 1,
    max_pages INTEGER DEFAULT 10,
    crawl_strategy TEXT DEFAULT 'basic',
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    pages_crawled INTEGER DEFAULT 0,
    pages_total INTEGER DEFAULT 0,
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    config JSONB DEFAULT '{}'::jsonb
);

-- Table pour les extractions structurées
CREATE TABLE IF NOT EXISTS crawl4ai.extractions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    page_id UUID REFERENCES crawl4ai.crawled_pages(id) ON DELETE CASCADE,
    extraction_type TEXT NOT NULL, -- 'code', 'links', 'images', 'tables', etc.
    extracted_data JSONB NOT NULL,
    confidence_score REAL DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================
-- INDEX POUR LES PERFORMANCES
-- ============================================

-- Index pour les recherches vectorielles
CREATE INDEX IF NOT EXISTS idx_archon_knowledge_base_embedding 
ON archon.knowledge_base USING ivfflat (embedding vector_cosine_ops);

CREATE INDEX IF NOT EXISTS idx_crawl4ai_pages_embedding 
ON crawl4ai.crawled_pages USING ivfflat (embedding vector_cosine_ops);

-- Index pour les recherches textuelles
CREATE INDEX IF NOT EXISTS idx_archon_knowledge_base_content 
ON archon.knowledge_base USING gin(to_tsvector('english', content));

CREATE INDEX IF NOT EXISTS idx_crawl4ai_pages_content 
ON crawl4ai.crawled_pages USING gin(to_tsvector('english', content));

-- Index pour les performances générales
CREATE INDEX IF NOT EXISTS idx_archon_projects_user_id ON archon.projects(user_id);
CREATE INDEX IF NOT EXISTS idx_archon_tasks_project_id ON archon.tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_archon_tasks_status ON archon.tasks(status);
CREATE INDEX IF NOT EXISTS idx_crawl4ai_pages_url ON crawl4ai.crawled_pages(url);
CREATE INDEX IF NOT EXISTS idx_crawl4ai_pages_status ON crawl4ai.crawled_pages(status);

-- ============================================
-- PERMISSIONS (RLS - Row Level Security)
-- ============================================

-- Activer RLS sur les tables sensibles
ALTER TABLE archon.projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE archon.tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE archon.conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE archon.credentials ENABLE ROW LEVEL SECURITY;

-- Politiques de base (à personnaliser selon vos besoins)
CREATE POLICY IF NOT EXISTS "Users can access their own projects" 
ON archon.projects FOR ALL 
USING (auth.uid() = user_id);

CREATE POLICY IF NOT EXISTS "Users can access tasks from their projects" 
ON archon.tasks FOR ALL 
USING (project_id IN (SELECT id FROM archon.projects WHERE user_id = auth.uid()));

-- ============================================
-- FONCTIONS UTILITAIRES
-- ============================================

-- Fonction pour mettre à jour updated_at automatiquement
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers pour updated_at
CREATE TRIGGER update_archon_projects_updated_at 
BEFORE UPDATE ON archon.projects 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_archon_tasks_updated_at 
BEFORE UPDATE ON archon.tasks 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_archon_knowledge_base_updated_at 
BEFORE UPDATE ON archon.knowledge_base 
FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- DONNÉES INITIALES
-- ============================================

-- Projet de test pour Archon
INSERT INTO archon.projects (name, description, user_id) 
VALUES ('Test Project', 'Projet de test pour valider la configuration Archon', NULL)
ON CONFLICT DO NOTHING;

-- ============================================
-- VÉRIFICATION
-- ============================================

-- Afficher un résumé de ce qui a été créé
SELECT 
    schemaname, 
    tablename, 
    tableowner 
FROM pg_tables 
WHERE schemaname IN ('archon', 'crawl4ai')
ORDER BY schemaname, tablename;
