from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.sqlite import Base, engine
from app.reference_data import CATEGORIES, DELHI_PS, FIR_STAGES, FOUND_STAGES
from app.routers import auth, found_items, photos, stolen_reports

# Creates sampatti_setu.db and all tables on first run.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sampatti-Setu API",
    description="Delhi Police lost & found / FIR-NCR matching backend.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(found_items.router)
app.include_router(stolen_reports.router)
app.include_router(photos.router)


@app.get("/reference-data")
def reference_data():
    """Static lookup data the frontend needs for its dropdowns."""
    return {
        "delhi_ps": DELHI_PS,
        "categories": CATEGORIES,
        "found_stages": FOUND_STAGES,
        "fir_stages": FIR_STAGES,
    }


@app.get("/health")
def health():
    return {"status": "ok"}
