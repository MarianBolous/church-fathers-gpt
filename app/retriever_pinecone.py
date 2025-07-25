
from openai import OpenAI
from pinecone import Pinecone
from config import OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_ENV

client = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("church-fathers")

def search_fathers(query, top_k=5):
    q_emb = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    ).data[0].embedding

    results = index.query(
        vector=q_emb,
        top_k=top_k,
        include_metadata=True
    )

    return results.matches

def format_answer(query, matches):
    context = "\n\n".join([
        f"Quote: {m.metadata['quote']}\nFather: {m.metadata['father']}\nSource: {m.metadata['source']}\nSummary: {m.metadata['summary']}\nBible: {m.metadata.get('bible_refs','')}"
        for m in matches
    ])

    prompt = f"""
You are an Orthodox theological assistant. The user asked: "{query}"
Below are 5 Church Fathers quotes with summaries and Bible references. Present them clearly and pastorally.

{context}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": "You are an Orthodox theological assistant."},
                  {"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    while True:
        user_q = input("\nAsk about the Fathers (or type 'exit'): ")
        if user_q.lower() == "exit":
            break

        matches = search_fathers(user_q, top_k=5)
        answer = format_answer(user_q, matches)

        print("\n💬 Answer:")
        print(answer)

        print("\n🔍 Raw Matches:")
        for m in matches:
            print(f"- {m.metadata['father']}: {m.metadata['quote']} ({m.metadata['source']})")
