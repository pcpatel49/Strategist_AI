import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import User, BlacklistedToken

from jose import jwt
from auth.security import SECRET_KEY, ALGORITHM

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/strategist_ai")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_tokens():
    db = SessionLocal()
    tokens = db.query(BlacklistedToken).all()
    for t in tokens:
        try:
            payload = jwt.decode(t.token, SECRET_KEY, algorithms=[ALGORITHM])
            print(f"Blacklisted Token ID {t.id} - Belongs to: {payload.get('sub')}")
        except Exception as e:
            pass

check_tokens()
