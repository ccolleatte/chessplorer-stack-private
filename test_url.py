import os
from supabase import create_client

url = "https://supabase.chessplorer.com"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJvbGUiOiJzZXJ2aWNlX3JvbGUiLCJleHAiOjE2ODIyNjk4MDgsImlhdCI6MTY2MzI2MDY5MDI0fQ.ibiHe8dHPOP71qkOELRbazZVBur-urZo6-S6S6ucwRo"  # injectée via env ou hardcodée

supabase = create_client(url, key)
print(supabase.auth.get_user())  # renvoie None ou un utilisateur s'il y en a un
