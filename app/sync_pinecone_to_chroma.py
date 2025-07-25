
import chromadb
from pinecone import Pinecone
from config import PINECONE_API_KEY, PINECONE_ENV

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("church-fathers")

chroma_client = chromadb.PersistentClient(path="../processed_chunks/chroma_db")
collection = chroma_client.get_or_create_collection("church_fathers_backup")

BATCH_SIZE = 100
print("🔄 Syncing data from Pinecone to Chroma...")

stats = index.describe_index_stats()
total_vectors = stats['total_vector_count']
print(f"Total vectors: {total_vectors}")

# Assuming sequential numeric IDs
ids = [str(i) for i in range(total_vectors)]

for start in range(0, total_vectors, BATCH_SIZE):
    end = min(start + BATCH_SIZE, total_vectors)
    print(f"Fetching vectors {start} to {end}...")
    results = index.fetch(ids[start:end])

    for vid, vec in results.vectors.items():
        meta = vec.metadata
        collection.add(
            ids=[vid],
            embeddings=[vec.values],
            documents=[meta.get("quote", "")],
            metadatas=[meta]
        )

print("✅ Sync complete. All Pinecone vectors saved to local Chroma.")
print("📂 Local Chroma DB path: processed_chunks/chroma_db")
