
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from api.state          import startup
from api.routes         import hotspots, forecast, causal, chat
from api.models         import HealthResponse
from api.state          import get_state


@asynccontextmanager
async def lifespan(app: FastAPI):
    csv_path = os.getenv("CSV_PATH", "data/BWA_final.csv")
    await startup(csv_path)
    yield
    print("[shutdown] Pranix API shutting down")


# ── App instantiation ──────────────────────────────────────────────────────────
app = FastAPI(
    title      = "Pranix",
    description= (
        "Hyperlocal pollution hotspot detection, 24hr AQI forecasting, "
        "and causal intervention ranking for Delhi municipal teams."
    ),
    version    = "1.0.0",
    lifespan   = lifespan,
    docs_url   = "/docs",
    redoc_url  = "/redoc"
)



app.add_middleware(
    CORSMiddleware,
    allow_origins    = ["*"],
    allow_credentials= True,
    allow_methods    = ["*"],
    allow_headers    = ["*"],
)

app.include_router(hotspots.router, prefix="/api")
app.include_router(forecast.router, prefix="/api")
app.include_router(causal.router,   prefix="/api")
app.include_router(chat.router,     prefix="/api")


@app.get("/health", response_model=HealthResponse, tags=["Meta"])
async def health():
    state = get_state()
    return HealthResponse(
        status       = "ok",
        city         = state.city,
        models_loaded= state.models_loaded,
        rows_loaded  = state.rows_loaded
    )


@app.get("/", tags=["Meta"])
async def root():
 
    return {
        "api"    : "CleanAir & Clear Streets",
        "version": "1.0.0",
        "docs"   : "/docs",
        "health" : "/health"
    }