import asyncio
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import User, BlacklistedToken
from database.database import get_db

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/strategist_ai")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def check_db():
    db = SessionLocal()
    users = db.query(User).all()
    print(f"Total Users: {len(users)}")
    for user in users:
        print(f"User: {user.email}, is_verified: {user.is_verified}")

    tokens = db.query(BlacklistedToken).all()
    print(f"\nTotal Blacklisted Tokens: {len(tokens)}")
    for t in tokens[-5:]:
        print(f"Token (preview): {t.token[:20]}..., blacklisted on: {t.blacklisted_on}")

if __name__ == "__main__":
    check_db()
