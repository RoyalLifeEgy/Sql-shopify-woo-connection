"""
Sync Engine for bidirectional data synchronization
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from sqlalchemy.orm import Session

from models import (
    FieldMapping, PlatformConnection, DatabaseConnection,
    SyncDirection, PlatformType, SyncLog
)
from integrations.shopify_client import ShopifyClient
from integrations.woocommerce_client import WooCommerceClient
from integrations.database_client import DatabaseClient
from utils.security import encryption_manager

logger = logging.getLogger(__name__)


class SyncEngine:
    """Engine for synchronizing data between databases and e-commerce platforms"""

    def __init__(self, db_session: Session):
        """
        Initialize sync engine

        Args:
            db_session: SQLAlchemy database session
        """
        self.db_session = db_session

    def _get_platform_client(self, platform_conn: PlatformConnection):
        """Get the appropriate platform client"""
        if platform_conn.platform_type == PlatformType.SHOPIFY:
            access_token = encryption_manager.decrypt(platform_conn.access_token)
            return ShopifyClient(
                shop_url=platform_conn.shop_url,
                access_token=access_token
            )
        elif platform_conn.platform_type == PlatformType.WOOCOMMERCE:
            api_key = encryption_manager.decrypt(platform_conn.api_key)
            api_secret = encryption_manager.decrypt(platform_conn.api_secret)
            return WooCommerceClient(
                shop_url=platform_conn.shop_url,
                consumer_key=api_key,
                consumer_secret=api_secret
            )
        else:
            raise ValueError(f"Unsupported platform type: {platform_conn.platform_type}")

    def _get_database_client(self, db_conn: DatabaseConnection) -> DatabaseClient:
        """Get database client"""
        username = encryption_manager.decrypt(db_conn.username)
        password = encryption_manager.decrypt(db_conn.password)

        return DatabaseClient(
            db_type=db_conn.db_type,
            host=db_conn.host,
            port=db_conn.port,
            database=db_conn.database,
            username=username,
            password=password,
            **(db_conn.connection_params or {})
        )

    def _transform_data(
        self,
        data: Dict[str, Any],
        field_mapping: Dict[str, str],
        transformation_rules: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Transform data according to field mapping and transformation rules

        Args:
            data: Source data
            field_mapping: Mapping of source fields to target fields
            transformation_rules: Optional transformation rules

        Returns:
            Transformed data
        """
        transformed = {}

        for source_field, target_field in field_mapping.items():
            if source_field in data:
                value = data[source_field]

                # Apply transformation rules if specified
                if transformation_rules and source_field in transformation_rules:
                    rule = transformation_rules[source_field]
                    # Apply custom transformations here
                    # For now, we'll just pass through
                    pass

                transformed[target_field] = value

        return transformed

    def sync_from_platform_to_database(
        self,
        field_mapping: FieldMapping
    ) -> Dict[str, Any]:
        """
        Sync data from e-commerce platform to database

        Args:
            field_mapping: Field mapping configuration

        Returns:
            Sync statistics
        """
        stats = {
            "records_processed": 0,
            "records_successful": 0,
            "records_failed": 0,
            "errors": []
        }

        try:
            # Get clients
            platform_conn = field_mapping.platform_connection
            db_conn = field_mapping.database_connection

            platform_client = self._get_platform_client(platform_conn)
            db_client = self._get_database_client(db_conn)

            # Fetch data from platform
            logger.info(f"Fetching {field_mapping.platform_resource} from platform")
            platform_data = platform_client.get_data(
                resource_type=field_mapping.platform_resource
            )

            logger.info(f"Fetched {len(platform_data)} records from platform")

            # Process each record
            for record in platform_data:
                stats["records_processed"] += 1
                try:
                    # Transform data according to field mapping
                    transformed_data = self._transform_data(
                        data=record,
                        field_mapping=field_mapping.platform_fields,
                        transformation_rules=field_mapping.transformation_rules
                    )

                    # Insert or update in database
                    db_client.insert_data(
                        table_name=field_mapping.db_table,
                        data=transformed_data
                    )
                    stats["records_successful"] += 1

                except Exception as e:
                    stats["records_failed"] += 1
                    error_msg = f"Failed to sync record: {str(e)}"
                    logger.error(error_msg)
                    stats["errors"].append(error_msg)

            db_client.close()

        except Exception as e:
            error_msg = f"Sync failed: {str(e)}"
            logger.error(error_msg)
            stats["errors"].append(error_msg)

        return stats

    def sync_from_database_to_platform(
        self,
        field_mapping: FieldMapping
    ) -> Dict[str, Any]:
        """
        Sync data from database to e-commerce platform

        Args:
            field_mapping: Field mapping configuration

        Returns:
            Sync statistics
        """
        stats = {
            "records_processed": 0,
            "records_successful": 0,
            "records_failed": 0,
            "errors": []
        }

        try:
            # Get clients
            platform_conn = field_mapping.platform_connection
            db_conn = field_mapping.database_connection

            platform_client = self._get_platform_client(platform_conn)
            db_client = self._get_database_client(db_conn)

            # Fetch data from database
            logger.info(f"Fetching data from database table {field_mapping.db_table}")
            db_data = db_client.fetch_data(
                table_name=field_mapping.db_table,
                columns=list(field_mapping.db_fields.keys())
            )

            logger.info(f"Fetched {len(db_data)} records from database")

            # Process each record
            for record in db_data:
                stats["records_processed"] += 1
                try:
                    # Transform data according to field mapping
                    transformed_data = self._transform_data(
                        data=record,
                        field_mapping=field_mapping.db_fields,
                        transformation_rules=field_mapping.transformation_rules
                    )

                    # Create or update on platform
                    if field_mapping.platform_resource == "products":
                        # Check if product exists (you'd need to implement logic to check)
                        platform_client.create_product(transformed_data)
                    # Add similar logic for other resources

                    stats["records_successful"] += 1

                except Exception as e:
                    stats["records_failed"] += 1
                    error_msg = f"Failed to sync record: {str(e)}"
                    logger.error(error_msg)
                    stats["errors"].append(error_msg)

            db_client.close()

        except Exception as e:
            error_msg = f"Sync failed: {str(e)}"
            logger.error(error_msg)
            stats["errors"].append(error_msg)

        return stats

    def sync_bidirectional(
        self,
        field_mapping: FieldMapping
    ) -> Dict[str, Any]:
        """
        Perform bidirectional sync

        Args:
            field_mapping: Field mapping configuration

        Returns:
            Combined sync statistics
        """
        logger.info(f"Starting bidirectional sync for mapping: {field_mapping.name}")

        # Sync from platform to database
        stats_from_platform = self.sync_from_platform_to_database(field_mapping)

        # Sync from database to platform
        stats_from_db = self.sync_from_database_to_platform(field_mapping)

        # Combine statistics
        combined_stats = {
            "from_platform": stats_from_platform,
            "from_database": stats_from_db,
            "total_records_processed": (
                stats_from_platform["records_processed"] +
                stats_from_db["records_processed"]
            ),
            "total_records_successful": (
                stats_from_platform["records_successful"] +
                stats_from_db["records_successful"]
            ),
            "total_records_failed": (
                stats_from_platform["records_failed"] +
                stats_from_db["records_failed"]
            )
        }

        return combined_stats

    def execute_sync(self, field_mapping_id: int) -> SyncLog:
        """
        Execute a sync operation and log the results

        Args:
            field_mapping_id: ID of the field mapping to sync

        Returns:
            Sync log record
        """
        # Get field mapping
        field_mapping = self.db_session.query(FieldMapping).filter(
            FieldMapping.id == field_mapping_id
        ).first()

        if not field_mapping:
            raise ValueError(f"Field mapping with ID {field_mapping_id} not found")

        if not field_mapping.is_active:
            raise ValueError(f"Field mapping {field_mapping.name} is not active")

        # Create sync log
        sync_log = SyncLog(
            field_mapping_id=field_mapping.id,
            platform_connection_id=field_mapping.platform_connection_id,
            sync_direction=field_mapping.sync_direction,
            status="running"
        )
        self.db_session.add(sync_log)
        self.db_session.commit()

        try:
            # Execute sync based on direction
            if field_mapping.sync_direction == SyncDirection.FROM_PLATFORM:
                stats = self.sync_from_platform_to_database(field_mapping)
            elif field_mapping.sync_direction == SyncDirection.TO_PLATFORM:
                stats = self.sync_from_database_to_platform(field_mapping)
            elif field_mapping.sync_direction == SyncDirection.BIDIRECTIONAL:
                stats = self.sync_bidirectional(field_mapping)
            else:
                raise ValueError(f"Invalid sync direction: {field_mapping.sync_direction}")

            # Update sync log
            sync_log.completed_at = datetime.utcnow()
            sync_log.records_processed = stats.get("total_records_processed", stats.get("records_processed", 0))
            sync_log.records_successful = stats.get("total_records_successful", stats.get("records_successful", 0))
            sync_log.records_failed = stats.get("total_records_failed", stats.get("records_failed", 0))
            sync_log.status = "completed"

            if stats.get("errors"):
                sync_log.error_details = {"errors": stats["errors"]}

            # Update field mapping last sync time
            field_mapping.last_sync = datetime.utcnow()

        except Exception as e:
            # Update sync log with error
            sync_log.completed_at = datetime.utcnow()
            sync_log.status = "failed"
            sync_log.error_message = str(e)
            logger.error(f"Sync failed for mapping {field_mapping.name}: {str(e)}")

        self.db_session.commit()
        return sync_log
