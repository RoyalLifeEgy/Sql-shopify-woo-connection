"""
Shopify Integration Client
"""
import shopify
from typing import List, Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)


class ShopifyClient:
    """Client for interacting with Shopify API"""

    def __init__(self, shop_url: str, access_token: str):
        """
        Initialize Shopify client

        Args:
            shop_url: Shopify shop URL (e.g., 'myshop.myshopify.com')
            access_token: Shopify access token
        """
        self.shop_url = shop_url.replace('https://', '').replace('http://', '')
        self.access_token = access_token
        self._setup_session()

    def _setup_session(self):
        """Setup Shopify session"""
        shopify.ShopifyResource.set_site(f"https://{self.shop_url}/admin/api/2024-01")
        shopify.ShopifyResource.headers = {"X-Shopify-Access-Token": self.access_token}

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def test_connection(self) -> bool:
        """Test the Shopify connection"""
        try:
            shop = shopify.Shop.current()
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
            params = {"limit": limit}
            if since_id:
                params["since_id"] = since_id

            products = shopify.Product.find(**params)
            return [product.to_dict() for product in products]
        except Exception as e:
            logger.error(f"Error fetching products: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_orders(self, limit: int = 250, since_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get orders from Shopify"""
        try:
            params = {"limit": limit, "status": "any"}
            if since_id:
                params["since_id"] = since_id

            orders = shopify.Order.find(**params)
            return [order.to_dict() for order in orders]
        except Exception as e:
            logger.error(f"Error fetching orders: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_customers(self, limit: int = 250, since_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get customers from Shopify"""
        try:
            params = {"limit": limit}
            if since_id:
                params["since_id"] = since_id

            customers = shopify.Customer.find(**params)
            return [customer.to_dict() for customer in customers]
        except Exception as e:
            logger.error(f"Error fetching customers: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def create_product(self, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a product in Shopify"""
        try:
            product = shopify.Product()
            product.title = product_data.get("title")
            product.body_html = product_data.get("body_html", "")
            product.vendor = product_data.get("vendor", "")
            product.product_type = product_data.get("product_type", "")
            product.tags = product_data.get("tags", "")

            if product.save():
                return product.to_dict()
            else:
                raise Exception(f"Failed to create product: {product.errors.full_messages()}")
        except Exception as e:
            logger.error(f"Error creating product: {str(e)}")
            raise

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def update_product(self, product_id: int, product_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a product in Shopify"""
        try:
            product = shopify.Product.find(product_id)
            for key, value in product_data.items():
                if hasattr(product, key):
                    setattr(product, key, value)

            if product.save():
                return product.to_dict()
            else:
                raise Exception(f"Failed to update product: {product.errors.full_messages()}")
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
