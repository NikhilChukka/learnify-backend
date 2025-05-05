# app/core/security.py

import datetime
from jose import jwt
from app.core.config import SECRET_KEY
from passlib.hash import pbkdf2_sha256

ALGORITHM = "HS256"

def hash_password(password: str) -> str:
    hash = pbkdf2_sha256.hash(password)
    print("Hashed password from hash_password", hash)
    return hash

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pbkdf2_sha256.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: datetime.timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.now(datetime.timezone.utc) + expires_delta
    else:
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
