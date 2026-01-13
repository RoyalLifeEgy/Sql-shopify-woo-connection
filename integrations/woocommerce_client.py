"""
WooCommerce Integration Client
"""
from woocommerce import API
from typing import List, Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)


class WooCommerceClient:
    """Client for interacting with WooCommerce API"""

    def __init__(self, shop_url: str, consumer_key: str, consumer_secret: str):
        """
        Initialize WooCommerce client

        Args:
            shop_url: WooCommerce store URL
            consumer_key: WooCommerce consumer key
            consumer_secret: WooCommerce consumer secret
        """
        self.shop_url = shop_url.rstrip('/')
        self.api = API(
            url=self.shop_url,
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            version="wc/v3",
            timeout=30
        )

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def test_connection(self) -> bool:
        """Test the WooCommerce connection"""
        try:
            response = self.api.get("system_status")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"WooCommerce connection test failed: {str(e)}")
            raise

    def get_available_resources(self) -> List[str]:
        """Get list of available WooCommerce resources"""
        return [
            "products",
            "product_variations",
            "orders",
            "customers",
            "coupons",
            "categories",
            "tags",
            "shipping_methods",
            "payment_gateways",
            "tax_rates"
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
                "name": "string",
                "slug": "string",
                "type": "string",
                "status": "string",
                "description": "text",
                "short_description": "text",
                "sku": "string",
                "price": "decimal",
                "regular_price": "decimal",
                "sale_price": "decimal",
                "date_created": "datetime",
                "date_modified": "datetime",
                "stock_status": "string",
                "stock_quantity": "integer",
                "manage_stock": "boolean",
                "categories": "array",
                "images": "array",
                "attributes": "array",
                "variations": "array"
            },
            "orders": {
                "id": "integer",
                "number": "string",
                "status": "string",
                "currency": "string",
                "date_created": "datetime",
                "date_modified": "datetime",
                "total": "decimal",
                "subtotal": "decimal",
                "total_tax": "decimal",
                "customer_id": "integer",
                "billing": "object",
                "shipping": "object",
                "payment_method": "string",
                "payment_method_title": "string",
                "line_items": "array",
                "shipping_lines": "array",
                "customer_note": "text"
            },
            "customers": {
                "id": "integer",
                "email": "string",
                "first_name": "string",
                "last_name": "string",
                "username": "string",
                "date_created": "datetime",
                "date_modified": "datetime",
                "billing": "object",
                "shipping": "object",
                "is_paying_customer": "boolean",
                "orders_count": "integer",
                "total_spent": "decimal"
            },
            "product_variations": {
                "id": "integer",
                "product_id": "integer",
                "sku": "string",
                "price": "decimal",
                "regular_price": "decimal",
                "sale_price": "decimal",
                "stock_status": "string",
                "stock_quantity": "integer",
                "weight": "string",
                "dimensions": "object",
                "attributes": "array"
            }
        }
        return field_mappings.get(resource_type, {})

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_products(self, per_page: int = 100, page: int = 1) -> List[Dict[str, Any]]:
        """Get products from WooCommerce"""
        try:
            response = self.api.get("products", params={"per_page": per_page, "page": page})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching products: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_orders(self, per_page: int = 100, page: int = 1) -> List[Dict[str, Any]]:
        """Get orders from WooCommerce"""
        try:
            response = self.api.get("orders", params={"per_page": per_page, "page": page})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching orders: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_customers(self, per_page: int = 100, page: int = 1) -> List[Dict[str, Any]]:
        """Get customers from WooCommerce"""
        try:
            response = self.api.get("customers", params={"per_page": per_page, "page": page})
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching customers: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a product in WooCommerce"""
        try:
            response = self.api.post("products", product_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def update_product(self, product_id: int, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a product in WooCommerce"""
        try:
            response = self.api.put(f"products/{product_id}", product_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error updating product {product_id}: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def create_order(self, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an order in WooCommerce"""
        try:
            response = self.api.post("orders", order_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def update_order(self, order_id: int, order_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an order in WooCommerce"""
        try:
            response = self.api.put(f"orders/{order_id}", order_data)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error updating order {order_id}: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_data(self, resource_type: str, per_page: int = 100, page: int = 1) -> List[Dict[str, Any]]:
        """
        Generic method to get data from any resource

        Args:
            resource_type: Type of resource (products, orders, customers)
            per_page: Number of records per page
            page: Page number

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

        return method(per_page=per_page, page=page)
