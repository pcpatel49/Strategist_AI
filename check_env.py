import os
from dotenv import load_dotenv

def check_env():
    load_dotenv()
    required_keys = [
        "OPENAI_API_KEY",
        "PINECONE_API_KEY",
        "MEM0_API_KEY",
        "DATABASE_URL"
    ]
    
    missing = []
    placeholders = []
    
    for key in required_keys:
        val = os.getenv(key)
        if not val:
            missing.append(key)
        elif "your-" in val or "user:password" in val:
            placeholders.append(key)
            
    if missing or placeholders:
        print("\n--- ENVIRONMENT CHECK FAILED ---")
        if missing:
            print(f"MISSING KEYS: {', '.join(missing)}")
        if placeholders:
            print(f"PLACEHOLDERS FOUND (Needs replacement): {', '.join(placeholders)}")
        print("\nPlease update your .env file before running any AI features.")
        return False
    
    print("\n--- ENVIRONMENT CHECK PASSED ---")
    return True

if __name__ == "__main__":
    check_env()
