import re
import jwt

with open('keys/ed22519.pem', 'rb') as f:
   PRIVATE_KEY = f.read()
with open('keys/ed25519_public.pem', 'rb') as f:
   PUBLIC_KEY = f.read()

def validate_username(username):
    if re.match(r'^[a-zA-Z0-9_]+$', username):  # Autorise uniquement lettres, chiffres, et _
        return username
    else:
        raise ValueError("Nom d'utilisateur invalide")

def bake_cookie(username, admin):
    username = validate_username(username)
    if type(admin) != bool:
        return None
    encoded = jwt.encode({'username': username, 'admin': admin}, PRIVATE_KEY, algorithm='EdDSA')
    return encoded

def authorise(token):
    try:
        decoded = jwt.decode(token, PUBLIC_KEY, algorithms=['EdDSA'])
    except Exception as e:
        return {"error": str(e)}

    response = {}

    if "admin" in decoded and decoded["admin"]:
        response{"admin": decoded["admin"]}
    if "username" in decoded:
        response{"username": decoded["username"]}
    else:
        return None
    return resposne