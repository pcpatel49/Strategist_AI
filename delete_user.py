import sys
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

def delete_user(email):
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

            user_id = user[0]
            
            # Delete from students first (foreign key constraint)
            # Note: If CASCADE is set on DB level, deleting user is enough. 
            # But let's be explicit for safety.
            conn.execute(text(f"DELETE FROM students WHERE student_id = '{user_id}'"))
            conn.execute(text(f"DELETE FROM users WHERE id = '{user_id}'"))
            
            conn.commit()
            print(f"Successfully deleted user and student profile for: {email}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python delete_user.py <email>")
    else:
        delete_user(sys.argv[1])
