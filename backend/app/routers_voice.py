from fastapi import APIRouter
from pydantic import BaseModel
from app.voice import parse

router = APIRouter()

class ParseIn(BaseModel):
    text: str

class ConfirmIn(BaseModel):
    session_id: str
    answer: str

sessions = {}

@router.post("/voice/parse")
def voice_parse(inp: ParseIn):
    r = parse(inp.text)
    sid = "s1"
    sessions[sid] = r
    return {"session_id": sid, "parsed": r}

@router.post("/voice/confirm")
def voice_confirm(inp: ConfirmIn):
    if inp.answer.lower() in ("haan","yes","ha"):
        return {"status": "saved", "data": sessions.get(inp.session_id)}
    return {"status": "cancelled"}
EOF