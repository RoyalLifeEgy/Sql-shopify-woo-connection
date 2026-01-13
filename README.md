# SQL E-commerce Connector

A powerful Python application to connect SQL databases to Shopify and WooCommerce, enabling bidirectional data synchronization with customizable field mappings and automated scheduling.

## Features

### Core Functionality
- **Multi-Platform Support**: Connect to both Shopify and WooCommerce
- **Database Support**: Works with PostgreSQL, MySQL, MS SQL, and SQLite
- **Business Profiles**: Manage multiple businesses/websites with separate configurations
- **Field Mapping**: Flexible field mapping between database tables and platform resources
- **Bidirectional Sync**: Sync data FROM platform, TO platform, or BOTH directions
- **Automated Scheduling**: Configure sync intervals for each mapping (minutes-based)
- **Real-time Monitoring**: Track sync operations with detailed logs

### Security Features
- **Encryption**: All sensitive credentials (API keys, passwords) are encrypted
- **JWT Authentication**: Secure API access with JSON Web Tokens
- **Password Hashing**: Bcrypt-based password hashing
- **Rate Limiting**: Built-in rate limiting for API protection

### Admin Control Panel
- **Dashboard**: View all connections and their status
- **Connection Management**: Enable/disable connections on the fly
- **Sync Monitoring**: View recent sync operations and their results
- **System Status**: Monitor the health of the main application
- **Full Control**: Manage all aspects of the connector from a simple interface

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Main Application (FastAPI)                │
│                         Port: 8000                           │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Business   │  │  Platform    │  │  Database    │     │
│  │   Profiles   │  │ Connections  │  │ Connections  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            Field Mappings & Sync Engine              │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           APScheduler (Automated Syncs)              │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ REST API
                            │
┌─────────────────────────────────────────────────────────────┐
│               Admin Control Panel (FastAPI)                  │
│                         Port: 8001                           │
├─────────────────────────────────────────────────────────────┤
│  • View all connections                                      │
│  • Monitor sync operations                                   │
│  • Enable/disable connections                                │
│  • System health monitoring                                  │
└─────────────────────────────────────────────────────────────┘
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- A SQL database (PostgreSQL, MySQL, MS SQL, or SQLite)

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd Sql-shopify-woo-connection
```

2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

**Important**: Update the following in `.env`:
- `SECRET_KEY`: A strong secret key for the application
- `JWT_SECRET_KEY`: A strong secret key for JWT tokens
- `ENCRYPTION_KEY`: A 32-character encryption key
- `DATABASE_URL`: Your database connection string

5. **Initialize the database**
```bash
python init_database.py
```

This will create all necessary tables and a default admin user:
- Username: `admin`
- Password: `admin`
- Email: `admin@example.com`

**IMPORTANT**: Change the default password after first login!

## Running the Application

### Option 1: Run Main Application Only
```bash
python main.py
# or
chmod +x run_main.sh
./run_main.sh
```

Access at: http://localhost:8000

### Option 2: Run Admin Panel Only
```bash
python admin_app.py
# or
chmod +x run_admin.sh
./run_admin.sh
```

Access at: http://localhost:8001

### Option 3: Run Both Applications
```bash
chmod +x run_both.sh
./run_both.sh
```

Access:
- Main Application: http://localhost:8000
- Admin Panel: http://localhost:8001
- API Documentation: http://localhost:8000/docs

## Usage Guide

### 1. Create a Business Profile

A business profile represents a company or business entity. You can have multiple profiles for managing different businesses.

**API Endpoint**: `POST /profiles`

```json
{
  "name": "My E-commerce Business",
  "description": "Main business profile",
  "contact_email": "contact@business.com",
  "contact_phone": "+1234567890"
}
```

### 2. Add Platform Connection (Shopify or WooCommerce)

#### Shopify Connection

**API Endpoint**: `POST /platform-connections`

```json
{
  "business_profile_id": 1,
  "name": "My Shopify Store",
  "platform_type": "shopify",
  "shop_url": "mystore.myshopify.com",
  "api_key": "your-api-key",
  "access_token": "your-access-token"
}
```

#### WooCommerce Connection

```json
{
  "business_profile_id": 1,
  "name": "My WooCommerce Store",
  "platform_type": "woocommerce",
  "shop_url": "https://mystore.com",
  "api_key": "ck_xxxxxxxxxxxxx",
  "api_secret": "cs_xxxxxxxxxxxxx"
}
```

### 3. Add Database Connection

**API Endpoint**: `POST /database-connections`

```json
{
  "business_profile_id": 1,
  "name": "Production Database",
  "db_type": "postgresql",
  "host": "localhost",
  "port": 5432,
  "database": "ecommerce_db",
  "username": "db_user",
  "password": "db_password"
}
```

Supported database types:
- `postgresql`
- `mysql`
- `mssql`
- `sqlite`

### 4. Discover Available Fields

#### Get Platform Resources and Fields

**API Endpoint**: `GET /platform-connections/{connection_id}/resources`

Returns all available resources (products, orders, customers) and their fields.

#### Get Database Schema

**API Endpoint**: `GET /database-connections/{connection_id}/schema`

Returns all tables and their columns from the database.

### 5. Create Field Mapping

**API Endpoint**: `POST /mappings`

```json
{
  "platform_connection_id": 1,
  "database_connection_id": 1,
  "name": "Products Sync",
  "db_table": "products",
  "db_fields": {
    "id": "platform_product_id",
    "name": "title",
    "description": "body_html",
    "price": "price",
    "sku": "sku"
  },
  "platform_resource": "products",
  "platform_fields": {
    "id": "id",
    "title": "title",
    "body_html": "body_html",
    "variants[0].price": "price",
    "variants[0].sku": "sku"
  },
  "sync_direction": "bidirectional",
  "sync_interval_minutes": 60
}
```

**Sync Direction Options**:
- `from_platform`: Platform → Database
- `to_platform`: Database → Platform
- `bidirectional`: Both directions

### 6. Trigger Manual Sync

**API Endpoint**: `POST /mappings/{mapping_id}/sync`

### 7. View Sync Logs

**API Endpoint**: `GET /mappings/{mapping_id}/logs`

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Admin Panel Features

Access the admin panel at http://localhost:8001

### Dashboard
- Total profiles, connections, and mappings
- Active vs inactive connections
- Recent sync statistics

### Connection Management
- View all platform and database connections
- Enable/disable connections with one click
- View connection status and last sync time

### Mapping Control
- View all field mappings
- Enable/disable mappings
- Monitor sync intervals and directions

### Sync Logs
- View recent sync operations
- See success/failure statistics
- Inspect error messages

### System Status
- Monitor main application health
- Database connection status
- Admin panel status

## Configuration

### Sync Intervals

Each field mapping can have its own sync interval (in minutes). For example:
- Products: Sync every 60 minutes
- Orders: Sync every 15 minutes
- Customers: Sync every 120 minutes

### Transformation Rules (Advanced)

You can add custom transformation rules to field mappings to modify data during sync:

```json
{
  "transformation_rules": {
    "price": {
      "type": "multiply",
      "value": 1.1
    },
    "status": {
      "type": "map",
      "mapping": {
        "active": "published",
        "inactive": "draft"
      }
    }
  }
}
```

## Security Best Practices

1. **Change default admin password** immediately after first login
2. **Use strong encryption keys** in production (32+ characters)
3. **Use HTTPS** in production environment
4. **Restrict CORS origins** to your frontend domains
5. **Regularly rotate API keys** and access tokens
6. **Use environment variables** for all sensitive data
7. **Enable rate limiting** in production
8. **Regular database backups**

## Troubleshooting

### Connection Test Fails

**Shopify**:
- Verify shop URL format: `mystore.myshopify.com`
- Check access token is valid
- Ensure API permissions are granted

**WooCommerce**:
- Verify REST API is enabled in WooCommerce
- Check consumer key and secret
- Ensure proper URL format (with https://)

**Database**:
- Verify host, port, and credentials
- Check firewall rules
- Ensure database server is running

### Sync Fails

1. Check sync logs for error messages
2. Verify field mappings are correct
3. Ensure connections are active
4. Check data types match between source and destination

### Scheduler Not Running

1. Check main application logs
2. Verify database connection
3. Restart the application

## Performance Optimization

1. **Adjust sync intervals** based on data volume
2. **Use selective field mapping** (only sync required fields)
3. **Implement batch processing** for large datasets
4. **Monitor database performance**
5. **Use connection pooling** for database connections

## Development

### Project Structure

```
Sql-shopify-woo-connection/
├── main.py                 # Main FastAPI application
├── admin_app.py           # Admin control panel
├── config.py              # Configuration settings
├── database.py            # Database setup
├── models.py              # SQLAlchemy models
├── schemas.py             # Pydantic schemas
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── api/                  # API endpoints
│   ├── auth.py          # Authentication
│   ├── profiles.py      # Business profiles
│   ├── connections.py   # Platform/DB connections
│   └── mappings.py      # Field mappings
├── integrations/        # Platform integrations
│   ├── shopify_client.py
│   ├── woocommerce_client.py
│   └── database_client.py
├── services/            # Business logic
│   ├── sync_engine.py  # Sync operations
│   └── scheduler.py    # Scheduling
└── utils/              # Utilities
    └── security.py     # Security functions
```

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or feature requests, please open an issue on GitHub.

## Roadmap

- [ ] Support for more e-commerce platforms (Magento, BigCommerce)
- [ ] Advanced data transformation capabilities
- [ ] Webhook support for real-time updates
- [ ] Web-based UI for configuration
- [ ] Docker containerization
- [ ] Kubernetes deployment support
- [ ] Advanced monitoring and alerting
- [ ] Data validation and conflict resolution
- [ ] Audit logging
- [ ] Multi-user support with roles

## Acknowledgments

Built with:
- FastAPI
- SQLAlchemy
- APScheduler
- Shopify Python API
- WooCommerce REST API