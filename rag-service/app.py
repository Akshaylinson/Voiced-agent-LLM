from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import chromadb
from sentence_transformers import SentenceTransformer
import sqlite3
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RAG Service")

class Query(BaseModel):
    query: str

VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "/data/vectordb")
DB_PATH = os.getenv("DB_PATH", "/data/knowledge.db")

embedding_model = None
chroma_client = None
collection = None

@app.on_event("startup")
async def initialize():
    global embedding_model, chroma_client, collection
    
    logger.info("Loading embedding model")
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    logger.info("Initializing ChromaDB")
    os.makedirs(VECTOR_DB_PATH, exist_ok=True)
    chroma_client = chromadb.PersistentClient(path=VECTOR_DB_PATH)
    
    try:
        collection = chroma_client.get_collection("knowledge_base")
        logger.info(f"Loaded existing collection with {collection.count()} documents")
    except:
        collection = chroma_client.create_collection("knowledge_base")
        logger.info("Created new collection")
        # Add sample documents
        sample_docs = [
            "Python is a high-level programming language known for its simplicity and readability.",
            "Docker is a platform for developing, shipping, and running applications in containers.",
            "Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
            "FastAPI is a modern web framework for building APIs with Python based on type hints."
        ]
        collection.add(
            documents=sample_docs,
            ids=[f"doc_{i}" for i in range(len(sample_docs))]
        )
        logger.info("Added sample documents")
    
    # Initialize SQLite DB
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY,
            question TEXT,
            answer TEXT
        )
    """)
    
    # Add sample data if empty
    cursor.execute("SELECT COUNT(*) FROM knowledge")
    if cursor.fetchone()[0] == 0:
        sample_data = [
            ("What is Docker?", "Docker is a containerization platform that packages applications and dependencies."),
            ("What is RAG?", "RAG stands for Retrieval-Augmented Generation, combining retrieval with LLM generation."),
            ("What is FastAPI?", "FastAPI is a modern Python web framework for building APIs quickly.")
        ]
        cursor.executemany("INSERT INTO knowledge (question, answer) VALUES (?, ?)", sample_data)
        conn.commit()
        logger.info("Added sample knowledge to SQLite")
    
    conn.close()

@app.post("/retrieve")
async def retrieve(query: Query):
    try:
        # Vector search
        results = collection.query(
            query_texts=[query.query],
            n_results=2
        )
        
        vector_context = results['documents'][0] if results['documents'] else []
        
        # Structured DB search
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT answer FROM knowledge WHERE question LIKE ? LIMIT 2",
            (f"%{query.query}%",)
        )
        db_results = cursor.fetchall()
        conn.close()
        
        db_context = [row[0] for row in db_results]
        
        # Combine contexts
        combined_context = vector_context + db_context
        context_text = "\n".join(combined_context) if combined_context else "No relevant context found."
        
        logger.info(f"Retrieved {len(combined_context)} context items")
        
        return {"context": context_text}
    
    except Exception as e:
        logger.error(f"Retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy", "collection_count": collection.count() if collection else 0}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
