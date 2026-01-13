"""
Shopify Integration Client
"""
import httpx
from typing import List, Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)


class ShopifyClient:
    """Client for interacting with Shopify API"""

    def __init__(self, shop_url: str, access_token: str, api_version: str = "2024-01"):
        """
        Initialize Shopify client

        Args:
            shop_url: Shopify shop URL (e.g., 'myshop.myshopify.com')
            access_token: Shopify access token
            api_version: Shopify API version
        """
        self.shop_url = shop_url.replace('https://', '').replace('http://', '')
        self.access_token = access_token
        self.api_version = api_version
        self.base_url = f"https://{self.shop_url}/admin/api/{self.api_version}"
        self.headers = {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json"
        }
        self.client = httpx.Client(headers=self.headers, timeout=30.0)

    def __del__(self):
        """Cleanup httpx client"""
        if hasattr(self, 'client'):
            self.client.close()

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def test_connection(self) -> bool:
        """Test the Shopify connection"""
        try:
            response = self.client.get(f"{self.base_url}/shop.json")
            response.raise_for_status()
            return True
        except Exception as e:
            logger.error(f"Shopify connection test failed: {str(e)}")
            raise

    def get_available_resources(self) -> List[str]:
        """Get list of available Shopify resources"""
        return [
            "products",
            "variants",
            "orders",
            "customers",
            "collections",
            "inventory_items",
            "inventory_levels",
            "locations",
            "fulfillments",
            "transactions"
        ]

    def get_resource_fields(self, resource_type: str) -> Dict[str, str]:
        """
        Get available fields for a resource type

        Args:
            resource_type: Type of resource (products, orders, etc.)

        Returns:
            Dictionary of field names and their types
        """
        field_mappings = {
            "products": {
                "id": "integer",
                "title": "string",
                "body_html": "text",
                "vendor": "string",
                "product_type": "string",
                "created_at": "datetime",
                "updated_at": "datetime",
                "published_at": "datetime",
                "status": "string",
                "tags": "string",
                "variants": "array",
                "images": "array",
                "options": "array"
            },
            "orders": {
                "id": "integer",
                "email": "string",
                "created_at": "datetime",
                "updated_at": "datetime",
                "number": "integer",
                "note": "text",
                "total_price": "decimal",
                "subtotal_price": "decimal",
                "total_tax": "decimal",
                "currency": "string",
                "financial_status": "string",
                "fulfillment_status": "string",
                "line_items": "array",
                "customer": "object",
                "shipping_address": "object",
                "billing_address": "object"
            },
            "customers": {
                "id": "integer",
                "email": "string",
                "first_name": "string",
                "last_name": "string",
                "phone": "string",
                "created_at": "datetime",
                "updated_at": "datetime",
                "state": "string",
                "total_spent": "decimal",
                "orders_count": "integer",
                "tags": "string",
                "addresses": "array"
            },
            "variants": {
                "id": "integer",
                "product_id": "integer",
                "title": "string",
                "price": "decimal",
                "sku": "string",
                "barcode": "string",
                "weight": "decimal",
                "weight_unit": "string",
                "inventory_quantity": "integer",
                "inventory_management": "string",
                "option1": "string",
                "option2": "string",
                "option3": "string"
            }
        }
        return field_mappings.get(resource_type, {})

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_products(self, limit: int = 250, since_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get products from Shopify"""
        try:
            params = {"limit": min(limit, 250)}
            if since_id:
                params["since_id"] = since_id

            response = self.client.get(f"{self.base_url}/products.json", params=params)
            response.raise_for_status()
            return response.json().get("products", [])
        except Exception as e:
            logger.error(f"Error fetching products: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_orders(self, limit: int = 250, since_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get orders from Shopify"""
        try:
            params = {"limit": min(limit, 250), "status": "any"}
            if since_id:
                params["since_id"] = since_id

            response = self.client.get(f"{self.base_url}/orders.json", params=params)
            response.raise_for_status()
            return response.json().get("orders", [])
        except Exception as e:
            logger.error(f"Error fetching orders: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_customers(self, limit: int = 250, since_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get customers from Shopify"""
        try:
            params = {"limit": min(limit, 250)}
            if since_id:
                params["since_id"] = since_id

            response = self.client.get(f"{self.base_url}/customers.json", params=params)
            response.raise_for_status()
            return response.json().get("customers", [])
        except Exception as e:
            logger.error(f"Error fetching customers: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a product in Shopify"""
        try:
            payload = {"product": product_data}
            response = self.client.post(f"{self.base_url}/products.json", json=payload)
            response.raise_for_status()
            return response.json().get("product", {})
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def update_product(self, product_id: int, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a product in Shopify"""
        try:
            payload = {"product": product_data}
            response = self.client.put(f"{self.base_url}/products/{product_id}.json", json=payload)
            response.raise_for_status()
            return response.json().get("product", {})
        except Exception as e:
            logger.error(f"Error updating product {product_id}: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_data(self, resource_type: str, limit: int = 250, since_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generic method to get data from any resource

        Args:
            resource_type: Type of resource (products, orders, customers)
            limit: Number of records to fetch
            since_id: Fetch records after this ID

        Returns:
            List of records
        """
        resource_methods = {
            "products": self.get_products,
            "orders": self.get_orders,
            "customers": self.get_customers
        }

        method = resource_methods.get(resource_type)
        if not method:
            raise ValueError(f"Unsupported resource type: {resource_type}")

        return method(limit=limit, since_id=since_id)
