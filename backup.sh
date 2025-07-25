#!/bin/bash
echo "🔄 Backing up Pinecone to Chroma..."
python app/sync_pinecone_to_chroma.py
echo "✅ Backup complete. Local ChromaDB saved in processed_chunks/chroma_db"
