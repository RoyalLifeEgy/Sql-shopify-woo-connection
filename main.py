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


@app.get("/dashboard")
def get_dashboard_stats():
    """Get dashboard statistics"""
    from database import SessionLocal
    from models import BusinessProfile, PlatformConnection, DatabaseConnection, FieldMapping, SyncLog
    from sqlalchemy import func
    from datetime import datetime, timedelta

    db = SessionLocal()
    try:
        # Get today's date
        today = datetime.utcnow().date()

        stats = {
            "total_profiles": db.query(BusinessProfile).count(),
            "total_platform_connections": db.query(PlatformConnection).count(),
            "active_platform_connections": db.query(PlatformConnection).filter(
                PlatformConnection.is_active == True
            ).count(),
            "total_database_connections": db.query(DatabaseConnection).count(),
            "active_database_connections": db.query(DatabaseConnection).filter(
                DatabaseConnection.is_active == True
            ).count(),
            "total_mappings": db.query(FieldMapping).count(),
            "active_mappings": db.query(FieldMapping).filter(
                FieldMapping.is_active == True
            ).count(),
            "total_sync_logs": db.query(SyncLog).count(),
            "recent_syncs": db.query(SyncLog).filter(
                func.date(SyncLog.started_at) == today
            ).count()
        }
        return stats
    finally:
        db.close()


@app.get("/logs/recent")
def get_recent_logs(limit: int = 50):
    """Get recent sync logs"""
    from database import SessionLocal
    from models import SyncLog

    db = SessionLocal()
    try:
        logs = db.query(SyncLog).order_by(
            SyncLog.started_at.desc()
        ).limit(limit).all()

        return {
            "logs": [
                {
                    "id": log.id,
                    "field_mapping_id": log.field_mapping_id,
                    "sync_direction": log.sync_direction.value,
                    "started_at": log.started_at.isoformat(),
                    "completed_at": log.completed_at.isoformat() if log.completed_at else None,
                    "status": log.status,
                    "records_processed": log.records_processed,
                    "records_successful": log.records_successful,
                    "records_failed": log.records_failed,
                    "error_message": log.error_message
                }
                for log in logs
            ],
            "total": len(logs)
        }
    finally:
        db.close()


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
