"""
Admin Control Panel Application

A simple FastAPI app to view and control all connections and the main application.
"""
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
import httpx
import logging

from config import get_settings
from database import get_db, init_db
from models import (
    BusinessProfile, PlatformConnection, DatabaseConnection,
    FieldMapping, SyncLog, ConnectionStatus
)
from api.dependencies import get_current_user
from schemas import UserLogin, Token

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="E-commerce Connector Admin Panel",
    version="1.0.0",
    description="Admin control panel for managing SQL E-commerce Connector"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_db()
    logger.info("Admin panel started")


@app.get("/", response_class=HTMLResponse)
def admin_dashboard():
    """Admin dashboard home page"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>E-commerce Connector Admin Panel</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                color: #333;
                border-bottom: 3px solid #4CAF50;
                padding-bottom: 10px;
            }
            .card {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 20px;
                margin: 15px 0;
                background-color: #fafafa;
            }
            .button {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                text-decoration: none;
                border-radius: 5px;
                display: inline-block;
                margin: 5px;
                border: none;
                cursor: pointer;
            }
            .button:hover {
                background-color: #45a049;
            }
            .button-danger {
                background-color: #f44336;
            }
            .button-danger:hover {
                background-color: #da190b;
            }
            .nav {
                background-color: #333;
                padding: 15px;
                margin: -30px -30px 20px -30px;
                border-radius: 8px 8px 0 0;
            }
            .nav a {
                color: white;
                text-decoration: none;
                padding: 10px 15px;
                display: inline-block;
            }
            .nav a:hover {
                background-color: #555;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="nav">
                <a href="/">Home</a>
                <a href="/dashboard">Dashboard</a>
                <a href="/connections">Connections</a>
                <a href="/mappings">Mappings</a>
                <a href="/logs">Logs</a>
                <a href="/docs">API Docs</a>
            </div>

            <h1>E-commerce Connector Admin Panel</h1>

            <div class="card">
                <h2>Welcome to the Admin Control Panel</h2>
                <p>Manage all your SQL to E-commerce platform connections from this dashboard.</p>
            </div>

            <div class="card">
                <h3>Quick Actions</h3>
                <a href="/dashboard" class="button">View Dashboard</a>
                <a href="/connections" class="button">Manage Connections</a>
                <a href="/mappings" class="button">Manage Mappings</a>
                <a href="/system/status" class="button">System Status</a>
            </div>

            <div class="card">
                <h3>Features</h3>
                <ul>
                    <li>View all business profiles and their connections</li>
                    <li>Monitor sync operations and logs</li>
                    <li>Enable/disable connections and mappings</li>
                    <li>View system health and status</li>
                    <li>Control the main application</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@app.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db)):
    """Get dashboard statistics"""
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
        "recent_syncs": db.query(SyncLog).order_by(
            SyncLog.started_at.desc()
        ).limit(10).count()
    }
    return stats


@app.get("/connections/summary")
def get_connections_summary(db: Session = Depends(get_db)):
    """Get summary of all connections"""
    profiles = db.query(BusinessProfile).all()

    summary = []
    for profile in profiles:
        platform_conns = db.query(PlatformConnection).filter(
            PlatformConnection.business_profile_id == profile.id
        ).all()

        db_conns = db.query(DatabaseConnection).filter(
            DatabaseConnection.business_profile_id == profile.id
        ).all()

        summary.append({
            "profile_id": profile.id,
            "profile_name": profile.name,
            "is_active": profile.is_active,
            "platform_connections": [
                {
                    "id": conn.id,
                    "name": conn.name,
                    "type": conn.platform_type.value,
                    "status": conn.status.value,
                    "is_active": conn.is_active,
                    "last_sync": conn.last_sync.isoformat() if conn.last_sync else None
                }
                for conn in platform_conns
            ],
            "database_connections": [
                {
                    "id": conn.id,
                    "name": conn.name,
                    "db_type": conn.db_type,
                    "status": conn.status.value,
                    "is_active": conn.is_active
                }
                for conn in db_conns
            ]
        })

    return {"profiles": summary, "total_profiles": len(summary)}


@app.get("/mappings/summary")
def get_mappings_summary(db: Session = Depends(get_db)):
    """Get summary of all field mappings"""
    mappings = db.query(FieldMapping).all()

    summary = [
        {
            "id": mapping.id,
            "name": mapping.name,
            "platform_resource": mapping.platform_resource,
            "db_table": mapping.db_table,
            "sync_direction": mapping.sync_direction.value,
            "sync_interval_minutes": mapping.sync_interval_minutes,
            "is_active": mapping.is_active,
            "last_sync": mapping.last_sync.isoformat() if mapping.last_sync else None
        }
        for mapping in mappings
    ]

    return {"mappings": summary, "total": len(summary)}


@app.get("/logs/recent")
def get_recent_logs(limit: int = 50, db: Session = Depends(get_db)):
    """Get recent sync logs"""
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


@app.post("/connections/platform/{connection_id}/toggle")
def toggle_platform_connection(connection_id: int, db: Session = Depends(get_db)):
    """Enable or disable a platform connection"""
    conn = db.query(PlatformConnection).filter(
        PlatformConnection.id == connection_id
    ).first()

    if not conn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found"
        )

    conn.is_active = not conn.is_active
    db.commit()

    return {
        "connection_id": conn.id,
        "is_active": conn.is_active,
        "message": f"Connection {'enabled' if conn.is_active else 'disabled'}"
    }


@app.post("/connections/database/{connection_id}/toggle")
def toggle_database_connection(connection_id: int, db: Session = Depends(get_db)):
    """Enable or disable a database connection"""
    conn = db.query(DatabaseConnection).filter(
        DatabaseConnection.id == connection_id
    ).first()

    if not conn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found"
        )

    conn.is_active = not conn.is_active
    db.commit()

    return {
        "connection_id": conn.id,
        "is_active": conn.is_active,
        "message": f"Connection {'enabled' if conn.is_active else 'disabled'}"
    }


@app.post("/mappings/{mapping_id}/toggle")
def toggle_mapping(mapping_id: int, db: Session = Depends(get_db)):
    """Enable or disable a field mapping"""
    mapping = db.query(FieldMapping).filter(
        FieldMapping.id == mapping_id
    ).first()

    if not mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mapping not found"
        )

    mapping.is_active = not mapping.is_active
    db.commit()

    return {
        "mapping_id": mapping.id,
        "is_active": mapping.is_active,
        "message": f"Mapping {'enabled' if mapping.is_active else 'disabled'}"
    }


@app.get("/system/status")
def get_system_status(db: Session = Depends(get_db)):
    """Get overall system status"""
    try:
        # Check main app health
        main_app_url = f"http://{settings.api_host}:{settings.api_port}/health"
        main_app_status = "unknown"

        try:
            response = httpx.get(main_app_url, timeout=5.0)
            if response.status_code == 200:
                main_app_status = "running"
        except:
            main_app_status = "stopped"

        # Get database stats
        db_status = "connected" if db.is_active else "disconnected"

        return {
            "main_application": {
                "status": main_app_status,
                "url": main_app_url
            },
            "database": {
                "status": db_status
            },
            "admin_panel": {
                "status": "running",
                "version": "1.0.0"
            }
        }
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system status: {str(e)}"
        )


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "admin_app:app",
        host=settings.api_host,
        port=settings.admin_port,
        reload=settings.debug
    )
