import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost/strategist_ai")
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(text("SELECT id, email, is_verified FROM users")).fetchall()
    print(f"Total Users currently in DB: {len(result)}")
    for row in result:
        print(row)
