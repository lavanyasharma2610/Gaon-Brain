import os
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import select

from app.db import get_session, init_db
from app.models import Village
from app.routers_bazaar import router as bazaar_router
from app.routers_bhav import router as bhav_router
from app.routers_glut import router as glut_router
from app.routers_logbook import router as logbook_router
from app.routers_radar import router as radar_router
from app.routers_sanjha import router as sanjha_router
from app.routers_shock import router as shock_router
from app.routers_sim import router as sim_router
from app.routers_suraksha import router as suraksha_router
from app.routers_voice import router as voice_router

app = FastAPI(title="Gaon Brain (गाँव ब्रेन)")

# Enable CORS for localhost development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Mount API Router under /api
api_router = APIRouter(prefix="/api")

@api_router.get("/health")
def api_health():
    return {
        "status": "ok",
        "app": "Gaon Brain (गाँव ब्रेन)",
        "version": "1.0.0",
        "label": "Sample data / सिमुलेशन"
    }

api_router.include_router(voice_router)
api_router.include_router(bhav_router)
api_router.include_router(logbook_router)
api_router.include_router(glut_router)
api_router.include_router(sim_router)
api_router.include_router(shock_router)
api_router.include_router(sanjha_router)
api_router.include_router(radar_router)
api_router.include_router(bazaar_router)
api_router.include_router(suraksha_router)

app.include_router(api_router)

# Also mount routes at root for backwards compatibility with tests and direct calls
app.include_router(voice_router)
app.include_router(bhav_router)
app.include_router(logbook_router)
app.include_router(glut_router)
app.include_router(sim_router)
app.include_router(shock_router)
app.include_router(sanjha_router)
app.include_router(radar_router)
app.include_router(bazaar_router)
app.include_router(suraksha_router)

@app.get("/health")
def root_health():
    return {"status": "ok"}

# 2. Auto-seed database on startup if empty
@app.on_event("startup")
def startup():
    init_db()
    db = get_session()
    try:
        village_count = len(db.exec(select(Village)).all())
        if village_count == 0:
            print("Database is empty. Auto-seeding initial demo data...")
            from app.seed import seed
            seed()
    except Exception as e:
        print(f"Startup check error: {e}")
    finally:
        db.close()

# 3. Serve Built Frontend at "/" with SPA Fallback
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CANDIDATE_DIST_DIRS = [
    os.path.join(os.path.dirname(BASE_DIR), "frontend", "dist"),
    os.path.join(BASE_DIR, "dist"),
    os.path.join(BASE_DIR, "frontend", "dist"),
    "/app/frontend/dist",
    "/app/dist"
]

FRONTEND_DIST = None
for d in CANDIDATE_DIST_DIRS:
    if os.path.exists(d) and os.path.isfile(os.path.join(d, "index.html")):
        FRONTEND_DIST = d
        break

if FRONTEND_DIST:
    assets_dir = os.path.join(FRONTEND_DIST, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    def serve_spa(full_path: str):
        # Exclude API, OpenAPI docs, and static routes
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("openapi.json"):
            return {"error": "Not Found"}
        
        file_path = os.path.join(FRONTEND_DIST, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
            
        index_file = os.path.join(FRONTEND_DIST, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
            
        return {"status": "ok", "message": "Gaon Brain API running."}
