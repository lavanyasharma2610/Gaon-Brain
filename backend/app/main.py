from fastapi import FastAPI
from app.db import init_db
from app.routers_voice import router as voice_router
from app.routers_bhav import router as bhav_router

app = FastAPI(title="Gaon Brain")

@app.on_event("startup")
def startup():
    init_db()

app.include_router(voice_router)
app.include_router(bhav_router)

@app.get("/health")
def health():
    return {"status": "ok"}
EOF