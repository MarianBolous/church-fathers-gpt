
import pandas as pd
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from config import OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_ENV

client = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)

index_name = "church-fathers"
if index_name not in pc.list_indexes().names():
    pc.create_index(index_name, dimension=1536, metric="cosine",
                    spec=ServerlessSpec(cloud="aws", region=PINECONE_ENV))

index = pc.Index(index_name)
df = pd.read_csv("../processed_chunks/chunks_with_bible.csv")

for i, row in df.iterrows():
    emb = client.embeddings.create(
        model="text-embedding-3-small",
        input=row["quote"]
    ).data[0].embedding

    index.upsert([
        (str(i), emb, {
            "quote": row["quote"],
            "father": row["father"],
            "source": row["source"],
            "summary": row["summary"],
            "topics": ";".join(row["topics"]) if isinstance(row["topics"], list) else row["topics"],
            "bible_refs": ";".join(row["bible_refs"]) if isinstance(row["bible_refs"], list) else row["bible_refs"]
        })
    ])

print("✅ Uploaded all chunks to Pinecone.")
