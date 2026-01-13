# Multi-Database Setup Guide

This guide shows how to connect multiple businesses, each with their own SQL database and e-commerce platform.

## Architecture Overview

```
Application (SQLite)
├── Business Profile 1
│   ├── PostgreSQL Database → Products, Orders
│   └── Shopify Store → Sync bidirectionally
│
├── Business Profile 2
│   ├── MySQL Database → Products, Orders
│   └── WooCommerce Store → Sync bidirectionally
│
└── Business Profile 3
    ├── MS SQL Database → Products, Orders
    └── Shopify Store → Sync bidirectionally
```

## Step-by-Step Setup

### Prerequisites

Install the database drivers you need:

```bash
# For PostgreSQL
pip install psycopg2-binary

# For MySQL
pip install pymysql

# For MS SQL
pip install pyodbc
```

### 1. Start the Application

```bash
# Make sure .env uses SQLite (already configured)
python init_database.py
python main.py
```

### 2. Login and Get Access Token

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'
```

Save the `access_token` from the response.

### 3. Create Business Profiles

**Business 1:**
```bash
curl -X POST http://localhost:8000/profiles \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tech Store Inc",
    "description": "Electronics and gadgets",
    "contact_email": "admin@techstore.com"
  }'
```

**Business 2:**
```bash
curl -X POST http://localhost:8000/profiles \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Fashion Boutique",
    "description": "Clothing and accessories",
    "contact_email": "admin@fashionboutique.com"
  }'
```

**Business 3:**
```bash
curl -X POST http://localhost:8000/profiles \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Home Essentials",
    "description": "Home goods and furniture",
    "contact_email": "admin@homeessentials.com"
  }'
```

### 4. Connect Each Business to Its Database

**Business 1 - PostgreSQL Database:**
```bash
curl -X POST http://localhost:8000/database-connections \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "business_profile_id": 1,
    "name": "Tech Store PostgreSQL DB",
    "db_type": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "techstore_db",
    "username": "postgres",
    "password": "your_password"
  }'
```

**Business 2 - MySQL Database:**
```bash
curl -X POST http://localhost:8000/database-connections \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "business_profile_id": 2,
    "name": "Fashion Boutique MySQL DB",
    "db_type": "mysql",
    "host": "localhost",
    "port": 3306,
    "database": "fashion_db",
    "username": "root",
    "password": "your_password"
  }'
```

**Business 3 - MS SQL Database:**
```bash
curl -X POST http://localhost:8000/database-connections \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "business_profile_id": 3,
    "name": "Home Essentials MS SQL DB",
    "db_type": "mssql",
    "host": "localhost",
    "port": 1433,
    "database": "home_db",
    "username": "sa",
    "password": "your_password"
  }'
```

### 5. Connect Each Business to Its E-commerce Platform

**Business 1 - Shopify:**
```bash
curl -X POST http://localhost:8000/platform-connections \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "business_profile_id": 1,
    "name": "Tech Store Shopify",
    "platform_type": "shopify",
    "shop_url": "techstore.myshopify.com",
    "api_key": "your_api_key",
    "access_token": "your_access_token"
  }'
```

**Business 2 - WooCommerce:**
```bash
curl -X POST http://localhost:8000/platform-connections \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "business_profile_id": 2,
    "name": "Fashion Boutique WooCommerce",
    "platform_type": "woocommerce",
    "shop_url": "https://fashionboutique.com",
    "api_key": "ck_xxxxxxxxxxxxx",
    "api_secret": "cs_xxxxxxxxxxxxx"
  }'
```

**Business 3 - Shopify:**
```bash
curl -X POST http://localhost:8000/platform-connections \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "business_profile_id": 3,
    "name": "Home Essentials Shopify",
    "platform_type": "shopify",
    "shop_url": "homeessentials.myshopify.com",
    "api_key": "your_api_key",
    "access_token": "your_access_token"
  }'
```

### 6. Test Database Connections

```bash
# Test Business 1 - PostgreSQL
curl http://localhost:8000/database-connections/1/test \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test Business 2 - MySQL
curl http://localhost:8000/database-connections/2/test \
  -H "Authorization: Bearer YOUR_TOKEN"

# Test Business 3 - MS SQL
curl http://localhost:8000/database-connections/3/test \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 7. Create Field Mappings

**Business 1 - Products Sync (PostgreSQL ↔ Shopify):**
```bash
curl -X POST http://localhost:8000/mappings \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "platform_connection_id": 1,
    "database_connection_id": 1,
    "name": "Tech Store Products",
    "db_table": "products",
    "db_fields": {
      "id": "product_id",
      "name": "product_name",
      "description": "description",
      "price": "price",
      "sku": "sku",
      "stock": "inventory"
    },
    "platform_resource": "products",
    "platform_fields": {
      "id": "id",
      "title": "title",
      "body_html": "body_html",
      "variants[0].price": "price",
      "variants[0].sku": "sku",
      "variants[0].inventory_quantity": "inventory_quantity"
    },
    "sync_direction": "bidirectional",
    "sync_interval_minutes": 30
  }'
```

**Business 2 - Orders Sync (MySQL ↔ WooCommerce):**
```bash
curl -X POST http://localhost:8000/mappings \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "platform_connection_id": 2,
    "database_connection_id": 2,
    "name": "Fashion Orders",
    "db_table": "orders",
    "db_fields": {
      "id": "order_id",
      "customer_email": "email",
      "total": "total_amount",
      "status": "order_status",
      "created": "created_date"
    },
    "platform_resource": "orders",
    "platform_fields": {
      "id": "id",
      "billing.email": "email",
      "total": "total",
      "status": "status",
      "date_created": "date_created"
    },
    "sync_direction": "from_platform",
    "sync_interval_minutes": 15
  }'
```

**Business 3 - Customers Sync (MS SQL ↔ Shopify):**
```bash
curl -X POST http://localhost:8000/mappings \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "platform_connection_id": 3,
    "database_connection_id": 3,
    "name": "Home Customers",
    "db_table": "customers",
    "db_fields": {
      "id": "customer_id",
      "email": "email",
      "first_name": "first_name",
      "last_name": "last_name",
      "phone": "phone"
    },
    "platform_resource": "customers",
    "platform_fields": {
      "id": "id",
      "email": "email",
      "first_name": "first_name",
      "last_name": "last_name",
      "phone": "phone"
    },
    "sync_direction": "bidirectional",
    "sync_interval_minutes": 60
  }'
```

## Using the Admin Panel

Access the admin panel at http://localhost:8001 to:

1. **View all connections** in one dashboard
2. **Enable/disable** specific business syncs
3. **Monitor sync logs** for each business
4. **Control sync intervals** on the fly

## Database Schema Discovery

To see what tables and fields are available in each database:

```bash
# Get schema for Business 1 (PostgreSQL)
curl http://localhost:8000/database-connections/1/schema \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get schema for Business 2 (MySQL)
curl http://localhost:8000/database-connections/2/schema \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get schema for Business 3 (MS SQL)
curl http://localhost:8000/database-connections/3/schema \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Monitoring

### View All Connections
```bash
curl http://localhost:8001/connections/summary
```

### View Sync Logs
```bash
# Recent logs for all businesses
curl http://localhost:8001/logs/recent?limit=50

# Logs for specific mapping
curl http://localhost:8000/mappings/1/logs \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Manual Sync Trigger
```bash
# Trigger manual sync for a specific mapping
curl -X POST http://localhost:8000/mappings/1/sync \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Scaling to Many Businesses

This architecture supports:
- ✅ Unlimited business profiles
- ✅ Each business with its own database (any SQL type)
- ✅ Each business with multiple platform connections
- ✅ Different sync intervals per mapping
- ✅ Independent sync operations (one failure doesn't affect others)
- ✅ Centralized monitoring and control

## Best Practices

1. **Database Isolation**: Each business should have its own database for security
2. **Sync Intervals**: Adjust based on data volume and update frequency
3. **Monitoring**: Check admin panel regularly for sync failures
4. **Backups**: Regular backups of both app database and customer databases
5. **Security**: Use strong passwords and encryption in production
6. **Testing**: Test connections before enabling automatic sync

## Troubleshooting

### Connection Fails
```bash
# Test specific database connection
curl http://localhost:8000/database-connections/{id}/test \
  -H "Authorization: Bearer YOUR_TOKEN"

# Check connection details
curl http://localhost:8000/database-connections/{id} \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Sync Not Running
1. Check if mapping is active
2. Verify both connections are active
3. Check sync logs for errors
4. Ensure scheduler is running (main.py)

### Data Not Syncing
1. Verify field mappings are correct
2. Check data types match
3. Ensure sync direction is correct
4. Review sync logs for specific errors

## Production Deployment

For production with multiple businesses:

1. Use a production database for app config (PostgreSQL recommended over SQLite)
2. Set up database connection pooling
3. Use environment-specific configurations
4. Implement monitoring and alerting
5. Set up automatic backups
6. Use HTTPS for all connections
7. Implement rate limiting per business
8. Scale horizontally with multiple app instances

## API Documentation

Full API documentation available at:
- http://localhost:8000/docs (Swagger)
- http://localhost:8000/redoc (ReDoc)

Use the interactive docs to test all endpoints!
