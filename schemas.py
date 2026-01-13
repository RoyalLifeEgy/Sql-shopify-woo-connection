"""
Pydantic schemas for API request/response validation
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from models import PlatformType, SyncDirection, ConnectionStatus


# User schemas
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: Optional[str]
    is_active: bool
    is_superuser: bool
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


# Business Profile schemas
class BusinessProfileCreate(BaseModel):
    name: str
    description: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None


class BusinessProfileUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    is_active: Optional[bool] = None


class BusinessProfileResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    contact_email: Optional[str]
    contact_phone: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Platform Connection schemas
class PlatformConnectionCreate(BaseModel):
    business_profile_id: int
    name: str
    platform_type: PlatformType
    shop_url: str
    api_key: str
    api_secret: Optional[str] = None  # For WooCommerce
    access_token: Optional[str] = None  # For Shopify


class PlatformConnectionUpdate(BaseModel):
    name: Optional[str] = None
    shop_url: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    access_token: Optional[str] = None
    is_active: Optional[bool] = None


class PlatformConnectionResponse(BaseModel):
    id: int
    business_profile_id: int
    name: str
    platform_type: PlatformType
    shop_url: str
    status: ConnectionStatus
    last_sync: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Database Connection schemas
class DatabaseConnectionCreate(BaseModel):
    business_profile_id: int
    name: str
    db_type: str
    host: str
    port: int
    database: str
    username: str
    password: str
    connection_params: Optional[Dict[str, Any]] = None


class DatabaseConnectionUpdate(BaseModel):
    name: Optional[str] = None
    host: Optional[str] = None
    port: Optional[int] = None
    database: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    connection_params: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class DatabaseConnectionResponse(BaseModel):
    id: int
    business_profile_id: int
    name: str
    db_type: str
    host: str
    port: int
    database: str
    status: ConnectionStatus
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Field Mapping schemas
class FieldMappingCreate(BaseModel):
    platform_connection_id: int
    database_connection_id: int
    name: str
    db_table: str
    db_fields: Dict[str, str]
    platform_resource: str
    platform_fields: Dict[str, str]
    sync_direction: SyncDirection
    sync_interval_minutes: int = 60
    transformation_rules: Optional[Dict[str, Any]] = None


class FieldMappingUpdate(BaseModel):
    name: Optional[str] = None
    db_table: Optional[str] = None
    db_fields: Optional[Dict[str, str]] = None
    platform_resource: Optional[str] = None
    platform_fields: Optional[Dict[str, str]] = None
    sync_direction: Optional[SyncDirection] = None
    sync_interval_minutes: Optional[int] = None
    transformation_rules: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class FieldMappingResponse(BaseModel):
    id: int
    platform_connection_id: int
    database_connection_id: int
    name: str
    db_table: str
    db_fields: Dict[str, str]
    platform_resource: str
    platform_fields: Dict[str, str]
    sync_direction: SyncDirection
    sync_interval_minutes: int
    transformation_rules: Optional[Dict[str, Any]]
    is_active: bool
    last_sync: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Schema Discovery schemas
class TableSchema(BaseModel):
    table_name: str
    columns: List[Dict[str, Any]]


class DatabaseSchemaResponse(BaseModel):
    tables: Dict[str, TableSchema]


class PlatformResourcesResponse(BaseModel):
    resources: List[str]
    fields: Dict[str, Dict[str, str]]


# Sync Log schemas
class SyncLogResponse(BaseModel):
    id: int
    field_mapping_id: int
    sync_direction: SyncDirection
    started_at: datetime
    completed_at: Optional[datetime]
    records_processed: int
    records_successful: int
    records_failed: int
    status: str
    error_message: Optional[str]

    class Config:
        from_attributes = True


# Manual Sync schemas
class ManualSyncRequest(BaseModel):
    field_mapping_id: int


class ManualSyncResponse(BaseModel):
    sync_log_id: int
    status: str
    message: str
