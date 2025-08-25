import os
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client

def main():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    client = create_client(url, key)

    resp = client.auth.sign_up({
    "email": "unique489@test.com",
    "password": "secret123"
    })
    print("SIGN UP response.user:", resp.user)
    print("SIGN UP response.error:", resp.error)

if __name__ == "__main__":
    main()
