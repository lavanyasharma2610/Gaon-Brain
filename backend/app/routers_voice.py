from fastapi import APIRouter
from pydantic import BaseModel
from app.voice import parse

router = APIRouter()

class ParseIn(BaseModel):
    text: str

@router.post("/voice/parse")
def voice_parse(inp: ParseIn):
    return parse(inp.text)
EOF