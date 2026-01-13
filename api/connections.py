"""
Platform and Database Connection API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import (
    PlatformConnection, DatabaseConnection, User,
    ConnectionStatus, PlatformType
)
from schemas import (
    PlatformConnectionCreate,
    PlatformConnectionUpdate,
    PlatformConnectionResponse,
    DatabaseConnectionCreate,
    DatabaseConnectionUpdate,
    DatabaseConnectionResponse,
    PlatformResourcesResponse,
    DatabaseSchemaResponse
)
from api.dependencies import get_current_user
from utils.security import encryption_manager
from integrations.shopify_client import ShopifyClient
from integrations.woocommerce_client import WooCommerceClient
from integrations.database_client import DatabaseClient

router = APIRouter(tags=["Connections"])


# Platform Connections
@router.post("/platform-connections", response_model=PlatformConnectionResponse, status_code=status.HTTP_201_CREATED)
def create_platform_connection(
    conn_data: PlatformConnectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new platform connection"""
    # Encrypt sensitive data
    encrypted_api_key = encryption_manager.encrypt(conn_data.api_key)
    encrypted_api_secret = encryption_manager.encrypt(conn_data.api_secret) if conn_data.api_secret else None
    encrypted_access_token = encryption_manager.encrypt(conn_data.access_token) if conn_data.access_token else None

    new_conn = PlatformConnection(
        business_profile_id=conn_data.business_profile_id,
        name=conn_data.name,
        platform_type=conn_data.platform_type,
        shop_url=conn_data.shop_url,
        api_key=encrypted_api_key,
        api_secret=encrypted_api_secret,
        access_token=encrypted_access_token,
        status=ConnectionStatus.ACTIVE
    )

    # Test connection
    try:
        if conn_data.platform_type == PlatformType.SHOPIFY:
            client = ShopifyClient(conn_data.shop_url, conn_data.access_token)
            client.test_connection()
        elif conn_data.platform_type == PlatformType.WOOCOMMERCE:
            client = WooCommerceClient(conn_data.shop_url, conn_data.api_key, conn_data.api_secret)
            client.test_connection()
    except Exception as e:
        new_conn.status = ConnectionStatus.ERROR
        db.add(new_conn)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Connection test failed: {str(e)}"
        )

    db.add(new_conn)
    db.commit()
    db.refresh(new_conn)
    return new_conn


@router.get("/platform-connections", response_model=List[PlatformConnectionResponse])
def list_platform_connections(
    business_profile_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List platform connections"""
    query = db.query(PlatformConnection)
    if business_profile_id:
        query = query.filter(PlatformConnection.business_profile_id == business_profile_id)
    connections = query.offset(skip).limit(limit).all()
    return connections


@router.get("/platform-connections/{connection_id}", response_model=PlatformConnectionResponse)
def get_platform_connection(
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific platform connection"""
    conn = db.query(PlatformConnection).filter(PlatformConnection.id == connection_id).first()
    if not conn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Platform connection not found"
        )
    return conn


@router.get("/platform-connections/{connection_id}/resources", response_model=PlatformResourcesResponse)
def get_platform_resources(
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get available resources and fields for a platform connection"""
    conn = db.query(PlatformConnection).filter(PlatformConnection.id == connection_id).first()
    if not conn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Platform connection not found"
        )

    try:
        if conn.platform_type == PlatformType.SHOPIFY:
            access_token = encryption_manager.decrypt(conn.access_token)
            client = ShopifyClient(conn.shop_url, access_token)
        elif conn.platform_type == PlatformType.WOOCOMMERCE:
            api_key = encryption_manager.decrypt(conn.api_key)
            api_secret = encryption_manager.decrypt(conn.api_secret)
            client = WooCommerceClient(conn.shop_url, api_key, api_secret)

        resources = client.get_available_resources()
        fields = {resource: client.get_resource_fields(resource) for resource in resources}

        return {"resources": resources, "fields": fields}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get resources: {str(e)}"
        )


# Database Connections
@router.post("/database-connections", response_model=DatabaseConnectionResponse, status_code=status.HTTP_201_CREATED)
def create_database_connection(
    conn_data: DatabaseConnectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new database connection"""
    # Encrypt sensitive data
    encrypted_username = encryption_manager.encrypt(conn_data.username)
    encrypted_password = encryption_manager.encrypt(conn_data.password)

    new_conn = DatabaseConnection(
        business_profile_id=conn_data.business_profile_id,
        name=conn_data.name,
        db_type=conn_data.db_type,
        host=conn_data.host,
        port=conn_data.port,
        database=conn_data.database,
        username=encrypted_username,
        password=encrypted_password,
        connection_params=conn_data.connection_params,
        status=ConnectionStatus.ACTIVE
    )

    # Test connection
    try:
        client = DatabaseClient(
            db_type=conn_data.db_type,
            host=conn_data.host,
            port=conn_data.port,
            database=conn_data.database,
            username=conn_data.username,
            password=conn_data.password,
            **(conn_data.connection_params or {})
        )
        client.test_connection()
        client.close()
    except Exception as e:
        new_conn.status = ConnectionStatus.ERROR
        db.add(new_conn)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Connection test failed: {str(e)}"
        )

    db.add(new_conn)
    db.commit()
    db.refresh(new_conn)
    return new_conn


@router.get("/database-connections", response_model=List[DatabaseConnectionResponse])
def list_database_connections(
    business_profile_id: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List database connections"""
    query = db.query(DatabaseConnection)
    if business_profile_id:
        query = query.filter(DatabaseConnection.business_profile_id == business_profile_id)
    connections = query.offset(skip).limit(limit).all()
    return connections


@router.get("/database-connections/{connection_id}", response_model=DatabaseConnectionResponse)
def get_database_connection(
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific database connection"""
    conn = db.query(DatabaseConnection).filter(DatabaseConnection.id == connection_id).first()
    if not conn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Database connection not found"
        )
    return conn


@router.get("/database-connections/{connection_id}/schema")
def get_database_schema(
    connection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get schema information for a database connection"""
    conn = db.query(DatabaseConnection).filter(DatabaseConnection.id == connection_id).first()
    if not conn:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Database connection not found"
        )

    try:
        username = encryption_manager.decrypt(conn.username)
        password = encryption_manager.decrypt(conn.password)

        client = DatabaseClient(
            db_type=conn.db_type,
            host=conn.host,
            port=conn.port,
            database=conn.database,
            username=username,
            password=password,
            **(conn.connection_params or {})
        )

        schemas = client.get_all_schemas()
        client.close()

        return {"tables": schemas}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get schema: {str(e)}"
        )
