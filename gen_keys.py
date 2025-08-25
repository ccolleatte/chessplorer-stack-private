import time
import os
import jwt  # PyJWT

# ⚠️ Assure-toi que ce secret est encodé en base64url, sans '=' padding !
JWT_SECRET = os.getenv("JWT_SECRET") or "ton_secret_base64url_sans_padding"
if "=" in JWT_SECRET:
    raise ValueError("Le JWT_SECRET contient un caractère '=': assure-toi qu'il est en base64url sans padding")

def create_token(role: str, exp_seconds: int = 10 * 365 * 24 * 3600):
    """Génère un JWT HS256 conforme avec les claims attendus par Supabase."""
    payload = {
        "iss": "supabase",
        "role": role,
        "exp": int(time.time()) + exp_seconds,
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    # jwt.encode retourne déjà une string continue header.payload.signature
    return token

if __name__ == "__main__":
    anon = create_token("anon")
    service = create_token("service_role")
    print("ANON_KEY =", anon)
    print("SERVICE_ROLE_KEY =", service)
