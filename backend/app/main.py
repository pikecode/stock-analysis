from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.core.database import engine, Base
from app.api import auth, stocks, concepts, rankings, summaries, imports

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting up Stock Analysis API...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")
    yield
    # Shutdown
    logger.info("Shutting down Stock Analysis API...")


app = FastAPI(
    title="Stock Analysis API",
    description="股票概念分析系统 API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url="/api/redoc" if settings.DEBUG else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS.split(",") if settings.ALLOWED_HOSTS != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for load balancers and monitoring."""
    return {
        "status": "healthy",
        "version": "1.0.0",
    }


@app.get("/health/ready", tags=["Health"])
async def readiness_check():
    """Readiness check - verifies database and redis connectivity."""
    from app.core.database import SessionLocal

    health_status = {
        "status": "healthy",
        "checks": {
            "database": "unknown",
            "redis": "unknown",
        }
    }

    # Check database
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        health_status["checks"]["database"] = "healthy"
    except Exception as e:
        health_status["checks"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"

    # Check Redis
    try:
        import redis
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        health_status["checks"]["redis"] = "healthy"
    except Exception as e:
        health_status["checks"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"

    return health_status


# Include API routers
app.include_router(auth.router, prefix="/api/v1", tags=["Auth"])
app.include_router(stocks.router, prefix="/api/v1", tags=["Stocks"])
app.include_router(concepts.router, prefix="/api/v1", tags=["Concepts"])
app.include_router(rankings.router, prefix="/api/v1", tags=["Rankings"])
app.include_router(summaries.router, prefix="/api/v1", tags=["Summaries"])
app.include_router(imports.router, prefix="/api/v1", tags=["Imports"])


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Stock Analysis API",
        "version": "1.0.0",
        "docs": "/api/docs" if settings.DEBUG else "Disabled in production",
    }
