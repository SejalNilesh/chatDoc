"""
DocMind AI configuration constants.
"""

FAISS_STORE_DIR = "faiss_store"          # root folder for persisted indexes
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
GROQ_MODEL      = "openai/gpt-oss-120b"

# Chunking settings (Improvement #5 — RecursiveCharacterTextSplitter)
CHUNK_SIZE    = 1000   # ~250 tokens; good balance of context vs precision
CHUNK_OVERLAP = 200    # 20% overlap preserves cross-boundary meaning

# Custom RAG system prompt (Improvement #8)
SYSTEM_PROMPT = """You are a helpful AI assistant. Answer questions based ONLY on the
provided context documents. If the answer cannot be found in the context, respond with:
"I couldn't find that information in the provided documents."
Be concise, accurate, and always ground your answer in the source material."""
