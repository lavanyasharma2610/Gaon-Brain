from fastapi import FastAPI

from app.db import init_db
from app.routers_bazaar import router as bazaar_router
from app.routers_bhav import router as bhav_router
from app.routers_glut import router as glut_router
from app.routers_logbook import router as logbook_router
from app.routers_radar import router as radar_router
from app.routers_sanjha import router as sanjha_router
from app.routers_shock import router as shock_router
from app.routers_suraksha import router as suraksha_router
from app.routers_voice import router as voice_router

app = FastAPI(title="Gaon Brain")

@app.on_event("startup")
def startup():
    init_db()

app.include_router(voice_router)
app.include_router(bhav_router)
app.include_router(logbook_router)
app.include_router(glut_router)
app.include_router(shock_router)
app.include_router(sanjha_router)
app.include_router(radar_router)
app.include_router(bazaar_router)
app.include_router(suraksha_router)

@app.get("/health")
def health():
    return {"status": "ok"}
