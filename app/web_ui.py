
import streamlit as st
import pandas as pd
from openai import OpenAI
from pinecone import Pinecone
from config import OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_ENV

client = OpenAI(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("church-fathers")

topics_df = pd.read_csv("../processed_chunks/master_topics.csv")
topic_list = topics_df["topic"].tolist()

st.title("📜 Church Fathers Semantic Search")
st.subheader("Ask a question and explore Patristic wisdom")

query = st.text_input("Your question:")
selected_topics = st.multiselect("Filter by topics:", options=topic_list)
TOP_K = 5

def search_fathers(query, topics=None):
    q_emb = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    ).data[0].embedding

    filter_dict = None
    if topics and len(topics) > 0:
        filter_dict = {"topics": {"$in": topics}}

    results = index.query(
        vector=q_emb,
        top_k=TOP_K,
        include_metadata=True,
        filter=filter_dict
    )
    return results.matches

if st.button("Search"):
    if not query:
        st.warning("Please enter a question.")
    else:
        matches = search_fathers(query, selected_topics if selected_topics else None)

        if not matches:
            st.info("No results found.")
        else:
            st.write(f"### Top {TOP_K} Results")
            for m in matches:
                md = m.metadata
                st.markdown(f"""
                **{md['father']}** — *{md['source']}*

                > {md['quote']}

                **Summary:** {md['summary']}  
                **Topics:** {md.get('topics', '')}  
                **Bible References:** {md.get('bible_refs', '')}
                """)
