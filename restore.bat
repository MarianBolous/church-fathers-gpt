@echo off
echo 🔄 Restoring Chroma backup to Pinecone...
python app\restore_chroma_to_pinecone.py
echo ✅ Restore complete. Pinecone index updated.
pause
