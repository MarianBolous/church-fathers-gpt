
import chromadb
from pinecone import Pinecone, ServerlessSpec
from config import PINECONE_API_KEY, PINECONE_ENV

# Initialize Chroma
chroma_client = chromadb.PersistentClient(path="../processed_chunks/chroma_db")
collection = chroma_client.get_or_create_collection("church_fathers_backup")

# Initialize Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "church-fathers"

if index_name not in pc.list_indexes().names():
    pc.create_index(index_name, dimension=1536, metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region=PINECONE_ENV))

index = pc.Index(index_name)

print("🔄 Restoring vectors from Chroma to Pinecone...")
results = collection.get(include=["embeddings", "documents", "metadatas"])

for vid, emb, meta in zip(results["ids"], results["embeddings"], results["metadatas"]):
    index.upsert([
        (vid, emb, meta)
    ])

print("✅ Restore complete. All Chroma vectors have been uploaded to Pinecone.")
