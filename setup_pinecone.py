import os
import time
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

if not PINECONE_API_KEY:
    print("Error: PINECONE_API_KEY not found in .env")
    exit(1)

pc = Pinecone(api_key=PINECONE_API_KEY)

indexes_to_create = [
    {"name": "university-data", "dimension": 1536},
    {"name": "student-documents", "dimension": 1536}
]

existing_indexes = [idx.name for idx in pc.list_indexes()]

for idx_info in indexes_to_create:
    name = idx_info["name"]
    dim = idx_info["dimension"]
    
    if name not in existing_indexes:
        print(f"Creating index: {name}...")
        pc.create_index(
            name=name,
            dimension=dim,
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        print(f"Index {name} created successfully.")
    else:
        print(f"Index {name} already exists.")

print("\nPinecone setup complete.")
