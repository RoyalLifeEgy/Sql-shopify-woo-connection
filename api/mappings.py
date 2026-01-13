"""
Field Mapping API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import FieldMapping, User, SyncLog
from schemas import (
    FieldMappingCreate,
    FieldMappingUpdate,
    FieldMappingResponse,
    SyncLogResponse,
    ManualSyncRequest,
    ManualSyncResponse
)
from api.dependencies import get_current_user
from services.sync_engine import SyncEngine
from services.scheduler import sync_scheduler

router = APIRouter(prefix="/mappings", tags=["Field Mappings"])


@router.post("", response_model=FieldMappingResponse, status_code=status.HTTP_201_CREATED)
def create_mapping(
    mapping_data: FieldMappingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new field mapping"""
    new_mapping = FieldMapping(**mapping_data.model_dump())
    db.add(new_mapping)
    db.commit()
    db.refresh(new_mapping)

    # Schedule sync job
    if new_mapping.is_active:
        sync_scheduler.add_sync_job(new_mapping)

    return new_mapping


@router.get("", response_model=List[FieldMappingResponse])
def list_mappings(
    platform_connection_id: int = None,
    database_connection_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List field mappings"""
    query = db.query(FieldMapping)
    if platform_connection_id:
        query = query.filter(FieldMapping.platform_connection_id == platform_connection_id)
    if database_connection_id:
        query = query.filter(FieldMapping.database_connection_id == database_connection_id)

    mappings = query.offset(skip).limit(limit).all()
    return mappings


@router.get("/{mapping_id}", response_model=FieldMappingResponse)
def get_mapping(
    mapping_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific field mapping"""
    mapping = db.query(FieldMapping).filter(FieldMapping.id == mapping_id).first()
    if not mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field mapping not found"
        )
    return mapping


@router.put("/{mapping_id}", response_model=FieldMappingResponse)
def update_mapping(
    mapping_id: int,
    mapping_data: FieldMappingUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a field mapping"""
    mapping = db.query(FieldMapping).filter(FieldMapping.id == mapping_id).first()
    if not mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field mapping not found"
        )

    # Update fields
    for field, value in mapping_data.model_dump(exclude_unset=True).items():
        setattr(mapping, field, value)

    db.commit()
    db.refresh(mapping)

    # Update sync job
    if mapping.is_active:
        sync_scheduler.update_sync_job(mapping)
    else:
        sync_scheduler.remove_sync_job(f"sync_mapping_{mapping.id}")

    return mapping


@router.delete("/{mapping_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mapping(
    mapping_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a field mapping"""
    mapping = db.query(FieldMapping).filter(FieldMapping.id == mapping_id).first()
    if not mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field mapping not found"
        )

    # Remove sync job
    sync_scheduler.remove_sync_job(f"sync_mapping_{mapping.id}")

    db.delete(mapping)
    db.commit()
    return None


@router.post("/{mapping_id}/sync", response_model=ManualSyncResponse)
def trigger_manual_sync(
    mapping_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger a manual sync for a specific mapping"""
    mapping = db.query(FieldMapping).filter(FieldMapping.id == mapping_id).first()
    if not mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Field mapping not found"
        )

    if not mapping.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot sync inactive mapping"
        )

    try:
        sync_engine = SyncEngine(db)
        sync_log = sync_engine.execute_sync(mapping_id)

        return {
            "sync_log_id": sync_log.id,
            "status": sync_log.status,
            "message": f"Sync completed: {sync_log.records_successful} successful, {sync_log.records_failed} failed"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sync failed: {str(e)}"
        )


@router.get("/{mapping_id}/logs", response_model=List[SyncLogResponse])
def get_sync_logs(
    mapping_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get sync logs for a specific mapping"""
    logs = db.query(SyncLog).filter(
        SyncLog.field_mapping_id == mapping_id
    ).order_by(SyncLog.started_at.desc()).offset(skip).limit(limit).all()

    return logs
