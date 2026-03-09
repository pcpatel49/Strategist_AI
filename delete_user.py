import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Ensure we import the models so SQLAlchemy knows about them
from database.models import User, Student

def delete_user(email):
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found in .env")
        return

    try:
        engine = create_engine(db_url)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        session = SessionLocal()

        # Find user by email
        user = session.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"User with email '{email}' not found.")
            session.close()
            return

        # Delete the user. Because we have cascade="all, delete-orphan" on the relationships
        # in models.py, this will correctly delete the Student, Courses, Activities, etc.
        session.delete(user)
        session.commit()
        
        print(f"Successfully deleted user and all associated data for: {email}")

    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python delete_user.py <email>")
    else:
        delete_user(sys.argv[1])
