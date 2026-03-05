import os
import sqlalchemy
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

def init_db():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("DATABASE_URL not found in .env")
        return

    # Extract database name and base URL
    # Format: postgresql://user:pass@host:port/db_name
    base_url, db_name = db_url.rsplit('/', 1)
    
    print(f"Checking for database: {db_name}...")
    
    # Connect to the default 'postgres' database to create the new one
    postgres_url = f"{base_url}/postgres"
    try:
        engine = create_engine(postgres_url, isolation_level="AUTOCOMMIT")
        with engine.connect() as conn:
            # Check if exists
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'"))
            if not result.fetchone():
                print(f"Creating database {db_name}...")
                conn.execute(text(f"CREATE DATABASE {db_name}"))
                print("Database created successfuly.")
            else:
                print(f"Database {db_name} already exists.")
        
        # Now run migrations or create tables
        print("\nInitializing tables...")
        from database.database import engine as app_engine, Base
        from database.models import User, Student # Ensure models are loaded
        
        Base.metadata.create_all(bind=app_engine)
        print("Success: Database tables initialized.")
        
    except Exception as e:
        print(f"ERROR: {e}")
        print("\nManual fix needed:")
        print(f"1. Open your PostgreSQL terminal (psql or pgAdmin).")
        print(f"2. Run: CREATE DATABASE {db_name};")

if __name__ == "__main__":
    init_db()
