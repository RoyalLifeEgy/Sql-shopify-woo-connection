"""
Main FastAPI Application
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from config import get_settings
from database import init_db
from api import auth, profiles, connections, mappings
from services.scheduler import sync_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting SQL E-commerce Connector application...")
    init_db()
    logger.info("Database initialized")

    # Reschedule all active sync jobs
    sync_scheduler.reschedule_all_jobs()
    logger.info("Sync scheduler initialized")

    yield

    # Shutdown
    logger.info("Shutting down application...")
    sync_scheduler.shutdown()
    logger.info("Sync scheduler stopped")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="A powerful application to sync data between SQL databases and e-commerce platforms (Shopify/WooCommerce)",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(profiles.router)
app.include_router(connections.router)
app.include_router(mappings.router)


@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "description": "SQL to E-commerce Platform Connector"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.get("/scheduler/status")
def scheduler_status():
    """Get scheduler status"""
    try:
        jobs = sync_scheduler.get_scheduled_jobs()
        return {
            "status": "running",
            "scheduled_jobs": jobs
        }
    except Exception as e:
        logger.error(f"Error getting scheduler status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get scheduler status")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug
    )
