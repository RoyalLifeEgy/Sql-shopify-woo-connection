"""
Database Models
"""
from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, Text,
    ForeignKey, Enum, JSON, Float
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
import enum


class PlatformType(str, enum.Enum):
    """E-commerce platform types"""
    SHOPIFY = "shopify"
    WOOCOMMERCE = "woocommerce"


class SyncDirection(str, enum.Enum):
    """Sync direction options"""
    TO_PLATFORM = "to_platform"  # SQL -> Platform
    FROM_PLATFORM = "from_platform"  # Platform -> SQL
    BIDIRECTIONAL = "bidirectional"  # Both ways


class ConnectionStatus(str, enum.Enum):
    """Connection status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class BusinessProfile(Base):
    """Business profile for managing multiple connections"""
    __tablename__ = "business_profiles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    platform_connections = relationship("PlatformConnection", back_populates="business_profile", cascade="all, delete-orphan")
    database_connections = relationship("DatabaseConnection", back_populates="business_profile", cascade="all, delete-orphan")


class PlatformConnection(Base):
    """E-commerce platform connections (Shopify/WooCommerce)"""
    __tablename__ = "platform_connections"

    id = Column(Integer, primary_key=True, index=True)
    business_profile_id = Column(Integer, ForeignKey("business_profiles.id"), nullable=False)
    name = Column(String(255), nullable=False)
    platform_type = Column(Enum(PlatformType), nullable=False)

    # Platform credentials (encrypted)
    shop_url = Column(String(500), nullable=False)
    api_key = Column(Text, nullable=False)  # Encrypted
    api_secret = Column(Text, nullable=True)  # Encrypted (for WooCommerce)
    access_token = Column(Text, nullable=True)  # Encrypted (for Shopify)

    # Status
    status = Column(Enum(ConnectionStatus), default=ConnectionStatus.ACTIVE)
    last_sync = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    business_profile = relationship("BusinessProfile", back_populates="platform_connections")
    field_mappings = relationship("FieldMapping", back_populates="platform_connection", cascade="all, delete-orphan")
    sync_logs = relationship("SyncLog", back_populates="platform_connection", cascade="all, delete-orphan")


class DatabaseConnection(Base):
    """SQL database connections"""
    __tablename__ = "database_connections"

    id = Column(Integer, primary_key=True, index=True)
    business_profile_id = Column(Integer, ForeignKey("business_profiles.id"), nullable=False)
    name = Column(String(255), nullable=False)

    # Database credentials (encrypted)
    db_type = Column(String(50), nullable=False)  # postgresql, mysql, mssql, etc.
    host = Column(String(500), nullable=False)
    port = Column(Integer, nullable=False)
    database = Column(String(255), nullable=False)
    username = Column(Text, nullable=False)  # Encrypted
    password = Column(Text, nullable=False)  # Encrypted

    # Additional connection parameters
    connection_params = Column(JSON, nullable=True)

    # Status
    status = Column(Enum(ConnectionStatus), default=ConnectionStatus.ACTIVE)
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    business_profile = relationship("BusinessProfile", back_populates="database_connections")
    field_mappings = relationship("FieldMapping", back_populates="database_connection", cascade="all, delete-orphan")


class FieldMapping(Base):
    """Field mapping between database and platform"""
    __tablename__ = "field_mappings"

    id = Column(Integer, primary_key=True, index=True)
    platform_connection_id = Column(Integer, ForeignKey("platform_connections.id"), nullable=False)
    database_connection_id = Column(Integer, ForeignKey("database_connections.id"), nullable=False)

    name = Column(String(255), nullable=False)  # Mapping name

    # Database side
    db_table = Column(String(255), nullable=False)
    db_fields = Column(JSON, nullable=False)  # List of field mappings

    # Platform side
    platform_resource = Column(String(100), nullable=False)  # products, orders, customers, etc.
    platform_fields = Column(JSON, nullable=False)  # List of field mappings

    # Sync configuration
    sync_direction = Column(Enum(SyncDirection), default=SyncDirection.BIDIRECTIONAL)
    sync_interval_minutes = Column(Integer, default=60)  # Sync every X minutes

    # Transformation rules (optional)
    transformation_rules = Column(JSON, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    last_sync = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    platform_connection = relationship("PlatformConnection", back_populates="field_mappings")
    database_connection = relationship("DatabaseConnection", back_populates="field_mappings")
    sync_logs = relationship("SyncLog", back_populates="field_mapping", cascade="all, delete-orphan")


class SyncLog(Base):
    """Sync operation logs"""
    __tablename__ = "sync_logs"

    id = Column(Integer, primary_key=True, index=True)
    field_mapping_id = Column(Integer, ForeignKey("field_mappings.id"), nullable=False)
    platform_connection_id = Column(Integer, ForeignKey("platform_connections.id"), nullable=False)

    sync_direction = Column(Enum(SyncDirection), nullable=False)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Statistics
    records_processed = Column(Integer, default=0)
    records_successful = Column(Integer, default=0)
    records_failed = Column(Integer, default=0)

    # Status and errors
    status = Column(String(50), nullable=False)  # running, completed, failed
    error_message = Column(Text, nullable=True)
    error_details = Column(JSON, nullable=True)

    # Relationships
    field_mapping = relationship("FieldMapping", back_populates="sync_logs")
    platform_connection = relationship("PlatformConnection", back_populates="sync_logs")


class User(Base):
    """Admin users for the control panel"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)

    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
