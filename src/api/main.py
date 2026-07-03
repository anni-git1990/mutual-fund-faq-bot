import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.api.chat import router as chat_router

app = FastAPI(
    title="Mutual Fund FAQ Assistant API",
    description="FastAPI backend for facts-only RAG Mutual Fund FAQ Bot using Groq and ChromaDB.",
    version="1.0.0"
)

# Configure CORS to allow frontend web interface access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include chat API routes
app.include_router(chat_router, prefix="/api")

# Serve UI static files (style.css, app.js, images, etc.)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve the index.html home page
@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

# Health endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "active_collection": os.environ.get("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5"),
        "timestamp": os.environ.get("HOST", "127.0.0.1")
    }

if __name__ == "__main__":
    import uvicorn
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host=host, port=port)
