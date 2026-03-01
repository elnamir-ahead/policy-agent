"""FastAPI app for local development - run with: uvicorn app:app --reload."""

import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse

from agent import chat


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(title="Procurement Policy Agent", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat")
def chat_endpoint(request: dict):
    """Chat with the procurement agent."""
    messages = request.get("messages", [])
    session_id = request.get("session_id") or str(uuid.uuid4())

    if not messages:
        raise HTTPException(status_code=400, detail="messages required")

    result = chat(messages, session_id)
    return result


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index():
    """Serve the chat UI (no npm required)."""
    html_path = Path(__file__).parent.parent / "frontend" / "standalone.html"
    if html_path.exists():
        return FileResponse(html_path)
    return HTMLResponse("<h1>Procurement Agent API</h1><p>Chat UI not found. Use POST /chat</p>")
