import os
from supabase import create_client

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
print(supabase.auth.get_user())  # ou une requête simple table
