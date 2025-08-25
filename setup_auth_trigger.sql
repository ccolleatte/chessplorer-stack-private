cat > setup_auth_trigger.sql << 'EOF'
-- Supprime l'ancienne fonction si elle existe
DROP FUNCTION IF EXISTS public.handle_new_user() CASCADE;

-- Crée la fonction handle_new_user()
CREATE FUNCTION public.handle_new_user()
RETURNS trigger
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = ''
AS $$
BEGIN
  INSERT INTO public.profiles (id)
    VALUES (NEW.id);
  RETURN NEW;
END;
$$;

-- Supprime trigger existant, puis crée le trigger de signup
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
AFTER INSERT ON auth.users
FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();
EOF

docker exec -i chessplorer-supabase-db psql -U supabase_auth_admin -d postgres < setup_auth_trigger.sql
