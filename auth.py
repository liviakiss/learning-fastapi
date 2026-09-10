# auth.py — password hashing, JWT creation/verification, current-user dependency

from pwdlib import PasswordHash
import jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# --- Password hashing (pwdlib + Argon2 — current standard, not passlib) ---
password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)

# --- JWT creation (PyJWT — current standard, not python-jose) ---
SECRET_KEY = "dev-secret-change-this-later"  # move to an env variable for real deployment
ALGORITHM = "HS256"

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# --- Protecting routes: HTTPBearer, not OAuth2PasswordBearer ---
# (OAuth2PasswordBearer renders a mismatched form-login UI in /docs —
# HTTPBearer gives a single plain token field, matching our JSON /login)
security_scheme = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)) -> str:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")