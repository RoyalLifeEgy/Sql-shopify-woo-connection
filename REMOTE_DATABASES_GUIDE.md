# Remote Databases Guide

The application supports connecting to databases on **different servers, different cloud providers, or anywhere on the internet**.

## Architecture with Remote Databases

```
┌─────────────────────────────────────────────────────────┐
│    Your Server (Application)                            │
│    - Main App (Python FastAPI)                          │
│    - Admin Panel                                        │
│    - Local SQLite (for config only)                     │
└─────────────────┬───────────────────────────────────────┘
                  │
    ┌─────────────┼─────────────┬──────────────────┐
    │             │             │                  │
    ▼             ▼             ▼                  ▼
┌─────────┐  ┌─────────┐  ┌──────────┐    ┌──────────┐
│Server A │  │Server B │  │AWS RDS   │    │Azure SQL │
│         │  │         │  │          │    │          │
│Business1│  │Business2│  │Business3 │    │Business4 │
│PG DB    │  │MySQL DB │  │MySQL DB  │    │MS SQL DB │
└─────────┘  └─────────┘  └──────────┘    └──────────┘
     │            │             │               │
     ▼            ▼             ▼               ▼
  Shopify    WooCommerce    Shopify       WooCommerce
```

## Example Configurations

### Business 1: PostgreSQL on Remote Server

```json
POST /database-connections
{
  "business_profile_id": 1,
  "name": "Business 1 - Remote PostgreSQL",
  "db_type": "postgresql",
  "host": "db1.company-a.com",
  "port": 5432,
  "database": "ecommerce_db",
  "username": "app_user",
  "password": "secure_password"
}
```

### Business 2: MySQL on Different Remote Server

```json
POST /database-connections
{
  "business_profile_id": 2,
  "name": "Business 2 - Remote MySQL",
  "db_type": "mysql",
  "host": "db2.company-b.com",
  "port": 3306,
  "database": "store_db",
  "username": "mysql_user",
  "password": "secure_password"
}
```

### Business 3: AWS RDS MySQL

```json
POST /database-connections
{
  "business_profile_id": 3,
  "name": "Business 3 - AWS RDS",
  "db_type": "mysql",
  "host": "myinstance.xxxxx.us-east-1.rds.amazonaws.com",
  "port": 3306,
  "database": "production_db",
  "username": "admin",
  "password": "aws_password"
}
```

### Business 4: Azure SQL Database

```json
POST /database-connections
{
  "business_profile_id": 4,
  "name": "Business 4 - Azure SQL",
  "db_type": "mssql",
  "host": "myserver.database.windows.net",
  "port": 1433,
  "database": "azure_db",
  "username": "sqladmin",
  "password": "azure_password",
  "connection_params": {
    "driver": "ODBC Driver 17 for SQL Server",
    "Encrypt": "yes",
    "TrustServerCertificate": "no"
  }
}
```

### Business 5: Google Cloud SQL

```json
POST /database-connections
{
  "business_profile_id": 5,
  "name": "Business 5 - Google Cloud SQL",
  "db_type": "postgresql",
  "host": "35.xxx.xxx.xxx",
  "port": 5432,
  "database": "gcloud_db",
  "username": "postgres",
  "password": "gcp_password"
}
```

### Business 6: DigitalOcean Managed Database

```json
POST /database-connections
{
  "business_profile_id": 6,
  "name": "Business 6 - DigitalOcean",
  "db_type": "mysql",
  "host": "db-mysql-nyc3-xxxxx.ondigitalocean.com",
  "port": 25060,
  "database": "defaultdb",
  "username": "doadmin",
  "password": "do_password"
}
```

## Real-World Scenarios

### Scenario 1: Multiple Clients, Each with Their Own Server

```python
# Client A: Their own server in New York
{
  "host": "db.client-a.com",
  "port": 5432,
  "db_type": "postgresql"
}

# Client B: Their own server in London
{
  "host": "database.client-b.co.uk",
  "port": 3306,
  "db_type": "mysql"
}

# Client C: Their own server in Tokyo
{
  "host": "db.client-c.jp",
  "port": 1433,
  "db_type": "mssql"
}
```

### Scenario 2: Mix of Cloud Providers

```python
# Business 1: AWS RDS
{
  "host": "prod-db.xxxxx.us-west-2.rds.amazonaws.com",
  "db_type": "mysql"
}

# Business 2: Azure SQL
{
  "host": "myserver.database.windows.net",
  "db_type": "mssql"
}

# Business 3: Google Cloud SQL
{
  "host": "35.xxx.xxx.xxx",
  "db_type": "postgresql"
}

# Business 4: On-premise server
{
  "host": "192.168.1.100",
  "db_type": "mysql"
}
```

### Scenario 3: Same Server, Different Databases

```python
# All on the same server, but different databases
# Business 1
{
  "host": "shared-db-server.com",
  "database": "client1_store"
}

# Business 2
{
  "host": "shared-db-server.com",
  "database": "client2_shop"
}

# Business 3
{
  "host": "shared-db-server.com",
  "database": "client3_ecommerce"
}
```

## Network & Firewall Configuration

### Allow Application Server to Access Remote Databases

**From Remote Database Server (Firewall Rules):**
```bash
# Allow your application server IP
# PostgreSQL (port 5432)
sudo ufw allow from YOUR_APP_SERVER_IP to any port 5432

# MySQL (port 3306)
sudo ufw allow from YOUR_APP_SERVER_IP to any port 3306

# MS SQL (port 1433)
sudo ufw allow from YOUR_APP_SERVER_IP to any port 1433
```

**For AWS RDS:**
- Edit Security Group
- Add Inbound Rule: Custom TCP, Port 3306 (MySQL) or 5432 (PostgreSQL)
- Source: Your application server IP

**For Azure SQL:**
- Go to SQL Database → Firewall settings
- Add client IP: Your application server IP
- Or use "Allow Azure services" for Azure-hosted apps

**For Google Cloud SQL:**
- Go to Connections → Authorized networks
- Add your application server IP

## Connection String Examples

### PostgreSQL with SSL

```python
connection_params = {
    "sslmode": "require",
    "sslrootcert": "/path/to/ca-certificate.crt",
    "sslcert": "/path/to/client-cert.pem",
    "sslkey": "/path/to/client-key.pem"
}
```

### MySQL with SSL

```python
connection_params = {
    "ssl_ca": "/path/to/ca.pem",
    "ssl_cert": "/path/to/client-cert.pem",
    "ssl_key": "/path/to/client-key.pem"
}
```

### MS SQL with Encryption

```python
connection_params = {
    "Encrypt": "yes",
    "TrustServerCertificate": "no",
    "Connection Timeout": "30"
}
```

## Testing Remote Connections

### Using the API

```bash
# Test connection
curl -X GET http://localhost:8000/database-connections/1/test \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Using Python Script

```python
from setup_multi_business import MultiBusinessSetup

setup = MultiBusinessSetup()
setup.login()

# Test each remote database
setup.test_database_connection(1)  # Business 1
setup.test_database_connection(2)  # Business 2
setup.test_database_connection(3)  # Business 3
```

### Manual Test with psql (PostgreSQL)

```bash
psql -h db.remote-server.com -p 5432 -U username -d database_name
```

### Manual Test with mysql

```bash
mysql -h db.remote-server.com -P 3306 -u username -p database_name
```

### Manual Test with sqlcmd (MS SQL)

```bash
sqlcmd -S db.remote-server.com,1433 -U username -P password -d database_name
```

## Security Best Practices

### 1. Use SSL/TLS for Remote Connections
Always encrypt connections to remote databases:

```python
# PostgreSQL
"connection_params": {"sslmode": "require"}

# MySQL
"connection_params": {"ssl_ca": "/path/to/ca.pem"}

# MS SQL
"connection_params": {"Encrypt": "yes"}
```

### 2. Use Strong Passwords
- Minimum 16 characters
- Mix of letters, numbers, symbols
- Unique per database

### 3. Restrict IP Access
Only allow your application server IP to access the database

### 4. Use Read-Only Users Where Possible
If syncing FROM platform TO database only:
```sql
-- Create read-only user
GRANT SELECT ON database.* TO 'readonly_user'@'app_server_ip';
```

### 5. VPN or Private Network
For sensitive data, use:
- VPN connection between servers
- Private networks (AWS VPC, Azure VNet)
- SSH tunnels

## SSH Tunnel Example

If you need to connect through SSH:

```bash
# Create SSH tunnel
ssh -L 3307:localhost:3306 user@remote-server.com

# Then connect to localhost:3307
{
  "host": "localhost",
  "port": 3307,
  "database": "remote_db"
}
```

## Monitoring Remote Connections

### Check Connection Status

```bash
# Get all database connections
curl http://localhost:8000/database-connections \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get specific connection details
curl http://localhost:8000/database-connections/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### View Sync Logs

```bash
# Admin panel
http://localhost:8001/logs/recent

# Or via API
curl http://localhost:8000/mappings/1/logs \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Troubleshooting

### Connection Timeout

```
Error: connection timed out
```

**Solutions:**
1. Check firewall rules on remote server
2. Verify security groups (AWS/Azure/GCP)
3. Test with telnet: `telnet db.server.com 5432`
4. Check if database is listening on external interface

### Access Denied

```
Error: Access denied for user
```

**Solutions:**
1. Verify username and password
2. Check user has proper permissions
3. Ensure user is allowed from your IP
4. For MySQL: `GRANT ALL ON db.* TO 'user'@'your_ip'`

### SSL Certificate Error

```
Error: SSL certificate verification failed
```

**Solutions:**
1. Use proper SSL certificates
2. For testing: `"sslmode": "require"` (PostgreSQL)
3. For testing: `"TrustServerCertificate": "yes"` (MS SQL)

### Connection Refused

```
Error: Connection refused
```

**Solutions:**
1. Database server not running
2. Wrong host or port
3. Firewall blocking connection
4. Database not configured for external connections

## Performance Optimization

### 1. Connection Pooling

The application uses SQLAlchemy connection pooling automatically:
- Maintains persistent connections
- Reduces connection overhead
- Reuses connections efficiently

### 2. Network Latency

For databases far from your application:
- Use CDN or edge locations
- Consider regional replicas
- Adjust sync intervals based on latency

### 3. Data Transfer

Large datasets over the internet:
- Use compression where possible
- Sync during off-peak hours
- Consider batch sizes in sync intervals

## Example: Complete Setup with Remote Databases

```python
from setup_multi_business import MultiBusinessSetup

setup = MultiBusinessSetup()
setup.login()

# Business 1: AWS RDS MySQL (US East)
profile1 = setup.create_business_profile(
    name="US Store",
    contact_email="admin@us-store.com"
)

db1 = setup.create_database_connection(
    business_profile_id=profile1,
    name="AWS RDS MySQL",
    db_type="mysql",
    host="prod-db.xxxxx.us-east-1.rds.amazonaws.com",
    port=3306,
    database="us_store_db",
    username="admin",
    password="aws_password"
)

# Business 2: Azure SQL (Europe)
profile2 = setup.create_business_profile(
    name="EU Store",
    contact_email="admin@eu-store.com"
)

db2 = setup.create_database_connection(
    business_profile_id=profile2,
    name="Azure SQL",
    db_type="mssql",
    host="euserver.database.windows.net",
    port=1433,
    database="eu_store_db",
    username="sqladmin",
    password="azure_password"
)

# Business 3: On-Premise PostgreSQL (Asia)
profile3 = setup.create_business_profile(
    name="Asia Store",
    contact_email="admin@asia-store.com"
)

db3 = setup.create_database_connection(
    business_profile_id=profile3,
    name="On-Premise PostgreSQL",
    db_type="postgresql",
    host="db.asia-datacenter.com",
    port=5432,
    database="asia_store_db",
    username="postgres",
    password="secure_password"
)

print("All remote databases connected!")
```

## Summary

✅ **Each business can have its database on a completely different server**
✅ **Mix cloud providers (AWS, Azure, GCP, etc.)**
✅ **Connect to on-premise servers**
✅ **Use any combination of PostgreSQL, MySQL, MS SQL**
✅ **Secure connections with SSL/TLS**
✅ **Independent sync schedules per business**
✅ **Centralized monitoring and control**

The application handles all the complexity of managing multiple remote database connections automatically!
