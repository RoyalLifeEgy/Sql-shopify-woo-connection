"""
Quick Setup Script for Multiple Businesses with Different Databases

This script helps you set up multiple business profiles, each with:
- Its own SQL database (PostgreSQL, MySQL, MS SQL, or SQLite)
- Its own e-commerce platform (Shopify or WooCommerce)
- Custom field mappings and sync intervals
"""
import requests
import json
from typing import Dict, Any, Optional


class MultiBusinessSetup:
    """Setup multiple businesses with different databases"""

    def __init__(self, api_url: str = "http://localhost:8000"):
        self.api_url = api_url
        self.token: Optional[str] = None
        self.headers: Dict[str, str] = {}

    def login(self, username: str = "admin", password: str = "admin") -> bool:
        """Login and get access token"""
        try:
            response = requests.post(
                f"{self.api_url}/auth/login",
                json={"username": username, "password": password}
            )
            response.raise_for_status()
            self.token = response.json()["access_token"]
            self.headers = {
                "Authorization": f"Bearer {self.token}",
                "Content-Type": "application/json"
            }
            print("✓ Successfully logged in")
            return True
        except Exception as e:
            print(f"✗ Login failed: {str(e)}")
            return False

    def create_business_profile(
        self,
        name: str,
        description: str = "",
        contact_email: str = ""
    ) -> Optional[int]:
        """Create a business profile"""
        try:
            response = requests.post(
                f"{self.api_url}/profiles",
                headers=self.headers,
                json={
                    "name": name,
                    "description": description,
                    "contact_email": contact_email
                }
            )
            response.raise_for_status()
            profile_id = response.json()["id"]
            print(f"✓ Created business profile: {name} (ID: {profile_id})")
            return profile_id
        except Exception as e:
            print(f"✗ Failed to create profile {name}: {str(e)}")
            return None

    def create_database_connection(
        self,
        business_profile_id: int,
        name: str,
        db_type: str,
        host: str,
        port: int,
        database: str,
        username: str,
        password: str
    ) -> Optional[int]:
        """Create a database connection"""
        try:
            response = requests.post(
                f"{self.api_url}/database-connections",
                headers=self.headers,
                json={
                    "business_profile_id": business_profile_id,
                    "name": name,
                    "db_type": db_type,
                    "host": host,
                    "port": port,
                    "database": database,
                    "username": username,
                    "password": password
                }
            )
            response.raise_for_status()
            conn_id = response.json()["id"]
            print(f"✓ Created database connection: {name} ({db_type}) (ID: {conn_id})")
            return conn_id
        except Exception as e:
            print(f"✗ Failed to create database connection {name}: {str(e)}")
            return None

    def test_database_connection(self, connection_id: int) -> bool:
        """Test a database connection"""
        try:
            response = requests.get(
                f"{self.api_url}/database-connections/{connection_id}/test",
                headers=self.headers
            )
            response.raise_for_status()
            result = response.json()
            if result.get("success"):
                print(f"✓ Database connection {connection_id} test passed")
                return True
            else:
                print(f"✗ Database connection {connection_id} test failed")
                return False
        except Exception as e:
            print(f"✗ Database connection test failed: {str(e)}")
            return False

    def create_shopify_connection(
        self,
        business_profile_id: int,
        name: str,
        shop_url: str,
        api_key: str,
        access_token: str
    ) -> Optional[int]:
        """Create a Shopify connection"""
        try:
            response = requests.post(
                f"{self.api_url}/platform-connections",
                headers=self.headers,
                json={
                    "business_profile_id": business_profile_id,
                    "name": name,
                    "platform_type": "shopify",
                    "shop_url": shop_url,
                    "api_key": api_key,
                    "access_token": access_token
                }
            )
            response.raise_for_status()
            conn_id = response.json()["id"]
            print(f"✓ Created Shopify connection: {name} (ID: {conn_id})")
            return conn_id
        except Exception as e:
            print(f"✗ Failed to create Shopify connection {name}: {str(e)}")
            return None

    def create_woocommerce_connection(
        self,
        business_profile_id: int,
        name: str,
        shop_url: str,
        consumer_key: str,
        consumer_secret: str
    ) -> Optional[int]:
        """Create a WooCommerce connection"""
        try:
            response = requests.post(
                f"{self.api_url}/platform-connections",
                headers=self.headers,
                json={
                    "business_profile_id": business_profile_id,
                    "name": name,
                    "platform_type": "woocommerce",
                    "shop_url": shop_url,
                    "api_key": consumer_key,
                    "api_secret": consumer_secret
                }
            )
            response.raise_for_status()
            conn_id = response.json()["id"]
            print(f"✓ Created WooCommerce connection: {name} (ID: {conn_id})")
            return conn_id
        except Exception as e:
            print(f"✗ Failed to create WooCommerce connection {name}: {str(e)}")
            return None

    def create_field_mapping(
        self,
        platform_connection_id: int,
        database_connection_id: int,
        name: str,
        db_table: str,
        db_fields: Dict[str, str],
        platform_resource: str,
        platform_fields: Dict[str, str],
        sync_direction: str = "bidirectional",
        sync_interval_minutes: int = 60
    ) -> Optional[int]:
        """Create a field mapping"""
        try:
            response = requests.post(
                f"{self.api_url}/mappings",
                headers=self.headers,
                json={
                    "platform_connection_id": platform_connection_id,
                    "database_connection_id": database_connection_id,
                    "name": name,
                    "db_table": db_table,
                    "db_fields": db_fields,
                    "platform_resource": platform_resource,
                    "platform_fields": platform_fields,
                    "sync_direction": sync_direction,
                    "sync_interval_minutes": sync_interval_minutes
                }
            )
            response.raise_for_status()
            mapping_id = response.json()["id"]
            print(f"✓ Created field mapping: {name} (ID: {mapping_id})")
            return mapping_id
        except Exception as e:
            print(f"✗ Failed to create field mapping {name}: {str(e)}")
            return None


def example_setup():
    """Example: Set up 3 businesses with different databases"""

    setup = MultiBusinessSetup()

    print("\n" + "="*60)
    print("Multi-Business Setup - Example Configuration")
    print("="*60 + "\n")

    # Login
    if not setup.login():
        print("\nPlease make sure the application is running at http://localhost:8000")
        return

    print("\n" + "-"*60)
    print("Setting up Business 1: Tech Store (PostgreSQL + Shopify)")
    print("-"*60)

    # Business 1: PostgreSQL + Shopify
    profile1 = setup.create_business_profile(
        name="Tech Store Inc",
        description="Electronics and gadgets",
        contact_email="admin@techstore.com"
    )

    if profile1:
        db1 = setup.create_database_connection(
            business_profile_id=profile1,
            name="Tech Store PostgreSQL",
            db_type="postgresql",
            host="localhost",
            port=5432,
            database="techstore_db",
            username="postgres",
            password="your_password"
        )

        # Note: Replace with real Shopify credentials
        platform1 = setup.create_shopify_connection(
            business_profile_id=profile1,
            name="Tech Store Shopify",
            shop_url="techstore.myshopify.com",
            api_key="your_api_key",
            access_token="your_access_token"
        )

    print("\n" + "-"*60)
    print("Setting up Business 2: Fashion Boutique (MySQL + WooCommerce)")
    print("-"*60)

    # Business 2: MySQL + WooCommerce
    profile2 = setup.create_business_profile(
        name="Fashion Boutique",
        description="Clothing and accessories",
        contact_email="admin@fashionboutique.com"
    )

    if profile2:
        db2 = setup.create_database_connection(
            business_profile_id=profile2,
            name="Fashion MySQL",
            db_type="mysql",
            host="localhost",
            port=3306,
            database="fashion_db",
            username="root",
            password="your_password"
        )

        # Note: Replace with real WooCommerce credentials
        platform2 = setup.create_woocommerce_connection(
            business_profile_id=profile2,
            name="Fashion WooCommerce",
            shop_url="https://fashionboutique.com",
            consumer_key="ck_xxxxxxxxxxxxx",
            consumer_secret="cs_xxxxxxxxxxxxx"
        )

    print("\n" + "-"*60)
    print("Setting up Business 3: Home Essentials (MS SQL + Shopify)")
    print("-"*60)

    # Business 3: MS SQL + Shopify
    profile3 = setup.create_business_profile(
        name="Home Essentials",
        description="Home goods and furniture",
        contact_email="admin@homeessentials.com"
    )

    if profile3:
        db3 = setup.create_database_connection(
            business_profile_id=profile3,
            name="Home MS SQL",
            db_type="mssql",
            host="localhost",
            port=1433,
            database="home_db",
            username="sa",
            password="your_password"
        )

        # Note: Replace with real Shopify credentials
        platform3 = setup.create_shopify_connection(
            business_profile_id=profile3,
            name="Home Essentials Shopify",
            shop_url="homeessentials.myshopify.com",
            api_key="your_api_key",
            access_token="your_access_token"
        )

    print("\n" + "="*60)
    print("Setup Complete!")
    print("="*60)
    print("\nNext steps:")
    print("1. Update the database and platform credentials above")
    print("2. Create field mappings for each business")
    print("3. View all connections at http://localhost:8001")
    print("4. Start syncing!")


if __name__ == "__main__":
    example_setup()
