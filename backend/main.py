import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from gemini_client import ask_question, explain_topic, generate_task

BASE_DIR = Path(__file__).resolve().parent
SITE_DIR = (BASE_DIR / "..").resolve()
HTML_FILE = SITE_DIR / "js" / "Алиса School .html"
GAME_FILE = SITE_DIR / "js" / "tank-game.html"

load_dotenv(BASE_DIR / ".env")

app = FastAPI(title="ALISA SCHOOL API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _quota_status(err: Exception) -> int:
    s = str(err)
    if '429' in s or 'RESOURCE_EXHAUSTED' in s or 'quota' in s.lower():
        return 429
    return 500


class ExplainRequest(BaseModel):
    grade: str
    subject: str
    topic: str


class AskRequest(BaseModel):
    grade: str
    subject: str
    question: str
    topic: str = ""


class TaskRequest(BaseModel):
    subject: str
    level: str


@app.get("/")
async def serve_site():
    return FileResponse(str(HTML_FILE), media_type="text/html")


@app.get("/game")
async def serve_game():
    return FileResponse(str(GAME_FILE), media_type="text/html")


@app.get("/api/health")
async def health():
    key = os.getenv("GEMINI_API_KEY", "")
    return {
        "status": "ok",
        "gemini_configured": bool(key),
        "model": os.getenv("GEMINI_MODEL", "gemini-1.5-flash"),
    }


@app.post("/api/explain")
async def api_explain(req: ExplainRequest):
    try:
        text = explain_topic(req.grade, req.subject, req.topic)
        return {"ok": True, "explanation": text}
    except Exception as e:
        raise HTTPException(status_code=_quota_status(e), detail=str(e))


@app.post("/api/ask")
async def api_ask(req: AskRequest):
    try:
        text = ask_question(req.grade, req.subject, req.question, req.topic)
        return {"ok": True, "answer": text}
    except Exception as e:
        raise HTTPException(status_code=_quota_status(e), detail=str(e))


@app.post("/api/task")
async def api_task(req: TaskRequest):
    try:
        task = generate_task(req.subject, req.level)
        return {"ok": True, "task": task}
    except Exception as e:
        raise HTTPException(status_code=_quota_status(e), detail=str(e))


@app.post("/api/ask")
async def api_ask(req: AskRequest):
    try:
        text = ask_question(req.grade, req.subject, req.question, req.topic)
        return {"ok": True, "answer": text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/task")
async def api_task(req: TaskRequest):
    try:
        task = generate_task(req.subject, req.level)
        return {"ok": True, "task": task}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
