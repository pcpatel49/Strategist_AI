from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

def migrate_otp():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found in .env")
        return

    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            print("Adding 'otp' and 'otp_expires_at' columns to 'users' table...")
            # PostgreSQL syntax to add columns if they don't exist
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS otp VARCHAR(6)"))
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS otp_expires_at TIMESTAMP"))
            conn.commit()
            print("Successfully migrated database for OTP.")

    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate_otp()
