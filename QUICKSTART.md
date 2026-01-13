# Quick Start Guide

Get up and running with SQL E-commerce Connector in 5 minutes!

## Step 1: Installation

```bash
# Clone and enter directory
git clone <repository-url>
cd Sql-shopify-woo-connection

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configuration

```bash
# Copy environment template
cp .env.example .env
```

Edit `.env` and set:
- `SECRET_KEY`: Any random string (32+ characters)
- `JWT_SECRET_KEY`: Another random string
- `ENCRYPTION_KEY`: Exactly 32 characters
- `DATABASE_URL`: Leave as default for SQLite or use your database URL

## Step 3: Initialize Database

```bash
python init_database.py
```

Default credentials:
- Username: `admin`
- Password: `admin`

## Step 4: Run Applications

```bash
# Run both applications
chmod +x run_both.sh
./run_both.sh
```

Or run separately:
```bash
# Main app
python main.py

# Admin panel (in another terminal)
python admin_app.py
```

## Step 5: Access Applications

- **Main API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:8001

## Step 6: First Steps

### Using the API

1. **Login** to get access token:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin"}'
```

2. **Create Business Profile**:
```bash
curl -X POST http://localhost:8000/profiles \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "My Business", "contact_email": "admin@business.com"}'
```

3. **Add Shopify Connection**:
```bash
curl -X POST http://localhost:8000/platform-connections \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "business_profile_id": 1,
    "name": "My Shopify Store",
    "platform_type": "shopify",
    "shop_url": "mystore.myshopify.com",
    "api_key": "your-key",
    "access_token": "your-token"
  }'
```

4. **Add Database Connection**:
```bash
curl -X POST http://localhost:8000/database-connections \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "business_profile_id": 1,
    "name": "My Database",
    "db_type": "postgresql",
    "host": "localhost",
    "port": 5432,
    "database": "mydb",
    "username": "user",
    "password": "pass"
  }'
```

5. **Create Field Mapping**:
```bash
curl -X POST http://localhost:8000/mappings \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "platform_connection_id": 1,
    "database_connection_id": 1,
    "name": "Products Sync",
    "db_table": "products",
    "db_fields": {"id": "product_id", "name": "title"},
    "platform_resource": "products",
    "platform_fields": {"id": "id", "title": "title"},
    "sync_direction": "bidirectional",
    "sync_interval_minutes": 60
  }'
```

### Using the Admin Panel

1. Open http://localhost:8001
2. Click "Dashboard" to see overview
3. Click "Connections" to view all connections
4. Toggle connections on/off as needed
5. View sync logs to monitor operations

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Explore the API at http://localhost:8000/docs
- Configure your real connections
- Set up field mappings for your use case

## Common Issues

**Port already in use?**
```bash
# Change ports in .env
API_PORT=8080
ADMIN_PORT=8081
```

**Database connection fails?**
```bash
# Use SQLite for testing (already configured)
DATABASE_URL="sqlite:///./ecommerce_connector.db"
```

**Import errors?**
```bash
# Make sure virtual environment is activated
source venv/bin/activate
pip install -r requirements.txt
```

## Getting Help

- Check [README.md](README.md) for detailed docs
- Review API documentation at http://localhost:8000/docs
- Open an issue on GitHub

Happy syncing!
