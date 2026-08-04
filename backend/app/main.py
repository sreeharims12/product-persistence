"""
main.py — FastAPI application entry point.

Lifecycle:
  startup  → create all DB tables, start APScheduler, load active monitoring jobs
  shutdown → gracefully stop the scheduler
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app.models import User, MonitoringRequest, ProductSnapshot, PriceHistory, Notification  # noqa: F401
from app.database import Base
from app.routers import auth, products, monitoring, notifications
from app.scheduler.jobs import scheduler, load_active_jobs

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────────────────
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    logger.info("Starting APScheduler...")
    scheduler.start()

    logger.info("Loading active monitoring jobs from database...")
    load_active_jobs()

    logger.info("Application ready ✓")
    yield

    # ── Shutdown ─────────────────────────────────────────────────────────────
    logger.info("Shutting down scheduler...")
    scheduler.shutdown(wait=False)


app = FastAPI(
    title="Product Monitor API",
    description="Persistent product price & stock monitoring across multiple stores",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router,          prefix="/api/auth",          tags=["Auth"])
app.include_router(products.router,      prefix="/api/products",      tags=["Products"])
app.include_router(monitoring.router,    prefix="/api/monitoring",    tags=["Monitoring"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])


@app.get("/", tags=["Health"])
def health():
    return {
        "status": "ok",
        "service": "Product Monitor API",
        "version": "1.0.0",
        "scheduler_running": scheduler.running,
    }
