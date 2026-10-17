from fastapi import APIRouter
from pydantic import BaseModel

from app.voice import parse

router = APIRouter()
sessions = {}

class ParseIn(BaseModel):
    text: str

class ConfirmIn(BaseModel):
    session_id: str
    answer: str

@router.post("/voice/parse")
def voice_parse(inp: ParseIn):
    r = parse(inp.text)
    sid = f"s{len(sessions)+1}"
    sessions[sid] = r
    if r["missing"]:
        return {"session_id": sid, "status": "need_field", "field": r["missing"][0], "parsed": r}
    return {"session_id": sid, "status": "confirm", "parsed": r}

@router.post("/voice/confirm")
def voice_confirm(inp: ConfirmIn):
    sess = sessions.get(inp.session_id)
    if not sess:
        return {"status": "not_found"}
    if inp.answer.lower() in ("haan","yes","ha","haanji"):
        # compute total in code
        if sess["intent"]=="record_sale" and sess["qty_kg"] and sess.get("rate"):
            sess["total"] = sess["qty_kg"]*sess["rate"]
        return {"status": "saved", "data": sess}
    if inp.answer.lower() in ("nahi","no","na"):
        return {"status": "cancelled"}
    return {"status": "ask", "message": "haan ya nahi?"}
