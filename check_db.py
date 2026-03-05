from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

def check_db():
    load_dotenv()
    url = os.getenv("DATABASE_URL")
    if not url:
        print("DATABASE_URL not found in .env")
        return
    
    print(f"Connecting to: {url.split('@')[-1]}") # Print host/db without credentials
    try:
        engine = create_engine(url)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("SUCCESS: Database connection established.")
    except Exception as e:
        print(f"FAILURE: Could not connect to database.\nError: {e}")

if __name__ == "__main__":
    check_db()
