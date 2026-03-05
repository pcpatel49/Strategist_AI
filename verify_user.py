import sys
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

def verify_user(email):
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found in .env")
        return

    try:
        engine = create_engine(db_url)
        with engine.connect() as conn:
            # Check if user exists
            result = conn.execute(text(f"SELECT id FROM users WHERE email = '{email}'"))
            user = result.fetchone()
            
            if not user:
                print(f"User with email '{email}' not found.")
                return

            # Set is_verified to True
            conn.execute(text(f"UPDATE users SET is_verified = TRUE WHERE email = '{email}'"))
            conn.commit()
            print(f"Successfully verified user: {email}")
            print("You can now log in at http://localhost:5173/login")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python verify_user.py <email>")
    else:
        verify_user(sys.argv[1])
