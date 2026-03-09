from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import User, Student
from database.database import get_db
import os
from dotenv import load_dotenv

def force_delete_all_users():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        users = session.query(User).all()
        for u in users:
            print(f"Deleting user {u.email}")
            session.delete(u)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    force_delete_all_users()
