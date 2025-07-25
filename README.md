# Church Fathers GPT

## Setup
1. Install requirements:
```bash
pip install -r requirements.txt
```
2. Add your API keys in config.py
3. Place PDFs into raw_docs/
4. Run chunker to process and generate CSV
5. Run embedder to upload to Pinecone
6. Run Streamlit UI:
```bash
streamlit run app/web_ui.py
```


## Optional: Using Local ChromaDB
- The docker-compose includes a ChromaDB container.
- By default, the app uses Pinecone.
- To use Chroma instead, edit `config.py` and set `VECTOR_DB = "chroma"`.
- Chroma will run locally on port 8000.


## Backing up Pinecone to Local ChromaDB
To create a local backup of your Pinecone index:
1. Run the sync script:
   ```bash
   python app/sync_pinecone_to_chroma.py
   ```
2. This will create a local persistent Chroma database in `processed_chunks/chroma_db`.
3. To use the local backup, edit `config.py` and set `VECTOR_DB = "chroma"`.


## Restoring from Chroma to Pinecone
To restore your local Chroma backup into Pinecone:
1. Ensure `processed_chunks/chroma_db` exists with your backup.
2. Run:
   ```bash
   python app/restore_chroma_to_pinecone.py
   ```
3. This will recreate your Pinecone index with all vectors and metadata.
