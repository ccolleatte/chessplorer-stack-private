import os
from supabase import create_client

def main():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    supabase = create_client(url, key)

    # 1. Création du compte utilisateur
    response = supabase.auth.sign_up({
        "email": "test@example.com",
        "password": "secret123"
    })
    print("SIGN UP response:", response.user, response.error)

if __name__ == "__main__":
    main()
