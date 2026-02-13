"""
API Bridge Platform - Main FastAPI Application
"""
from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("Starting API Bridge Platform...")
    from app.core.redis import get_redis, close_redis
    
    # Initialize Redis connection
    await get_redis()
    
    # Start Continuous Security Monitoring
    from app.core.watcher import start_background_watcher
    start_background_watcher("/Users/obafemi/bridge/apps")
    
    yield
    
    logger.info("Shutting down API Bridge Platform...")
    # Cleanup connections
    await close_redis()
    
    # Stop Security Monitoring
    from app.core.watcher import stop_background_watcher
    stop_background_watcher()


from app.routers import bridge, key, webhooks

app = FastAPI(
    title="API Bridge Platform",
    description="Auto-generate APIs for websites without existing APIs",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bridge.router, prefix="/api/v1")
app.include_router(key.router, prefix="/api/v1")
app.include_router(webhooks.router, prefix="/api/v1")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Bridge.dev",
        "version": "0.1.0"
    }


@app.get("/api/v1/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """Detailed health check"""
    from app.core.redis import get_redis
    import typing
    import subprocess
    
    health_status: typing.Dict[str, str] = {
        "status": "healthy",
        "database": "disconnected",
        "redis": "disconnected",
        "playwright": "not_found"
    }
    
    # Check DB
    try:
        from sqlalchemy import text
        await db.execute(text("SELECT 1"))
        health_status["database"] = "connected"
    except Exception as e:
        logger.error(f"DB Health Check Failed: {e}")
        health_status["status"] = "unhealthy"
        
    # Check Redis
    try:
        redis = await get_redis()
        if await redis.ping():
            health_status["redis"] = "connected"
    except Exception as e:
        logger.error(f"Redis Health Check Failed: {e}")
        health_status["status"] = "unhealthy"
        
    # Check Playwright
    try:
        # Check if playwright CLI is available or if browsers are installed
        result = subprocess.run(["npx", "playwright", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            health_status["playwright"] = "ready"
    except Exception:
        pass
        
    return health_status


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
