import os
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database.models import BlacklistedToken
import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
# Default to 7 days
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24 * 7))

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "jti": uuid.uuid4().hex})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_verification_token(email: str):
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode = {"sub": email, "type": "verification", "exp": expire, "jti": uuid.uuid4().hex}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_password_reset_token(email: str):
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode = {"sub": email, "type": "reset", "exp": expire, "jti": uuid.uuid4().hex}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def is_token_blacklisted(db: Session, token: str):
    return db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first() is not None

def blacklist_token(db: Session, token: str):
    db_token = BlacklistedToken(token=token)
    db.add(db_token)
    db.commit()
