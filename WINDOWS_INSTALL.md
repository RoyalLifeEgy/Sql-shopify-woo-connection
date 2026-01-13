# Windows Installation Guide

This guide will help you install and run the SQL E-commerce Connector on Windows, especially with Python 3.13.

## Prerequisites

- Python 3.8 or higher (tested with Python 3.13)
- pip (comes with Python)
- Git (optional, for cloning the repository)

## Installation Steps

### 1. Clone or Download the Repository

```powershell
# If you have Git installed
git clone <repository-url>
cd Sql-shopify-woo-connection

# Or download and extract the ZIP file, then navigate to the folder
cd path\to\Sql-shopify-woo-connection
```

### 2. Create a Virtual Environment

```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# You should see (venv) in your prompt
```

### 3. Upgrade pip (Important!)

```powershell
python -m pip install --upgrade pip
```

### 4. Install Dependencies

**Basic Installation (works with all Python versions including 3.13):**

```powershell
pip install -r requirements.txt
```

This installs the core application with SQLite support (no external database drivers needed).

**Optional: Install Database Drivers**

Only install the drivers you need:

**For PostgreSQL:**
```powershell
# Note: May fail on Python 3.13 without PostgreSQL installed
pip install psycopg2-binary
```
If psycopg2-binary fails, you have two options:
1. Use SQLite instead (already included)
2. Install PostgreSQL on your system first, then retry

**For MySQL:**
```powershell
pip install pymysql
```

**For MS SQL Server:**
```powershell
# Requires Microsoft ODBC Driver 17 or 18 for SQL Server
pip install pyodbc
```
Download ODBC Driver: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

### 5. Configure Environment Variables

```powershell
# Copy the example environment file
copy .env.example .env

# Edit .env with Notepad or your preferred editor
notepad .env
```

**Minimum configuration for testing:**
```ini
# Application
APP_NAME="SQL E-commerce Connector"
DEBUG=true

# Database (SQLite - no setup needed)
DATABASE_URL=sqlite:///./ecommerce_connector.db

# Security (generate random strings for production)
SECRET_KEY=your-secret-key-here-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-here
ENCRYPTION_KEY=12345678901234567890123456789012

# API Ports
API_PORT=8000
ADMIN_PORT=8001
```

### 6. Initialize the Database

```powershell
python init_database.py
```

You should see:
```
Database initialized successfully!
Default admin user created:
  Username: admin
  Password: admin
  Email: admin@example.com
```

### 7. Run the Applications

**Option A: Run Both Applications Together**
```powershell
# In PowerShell
start python main.py
start python admin_app.py
```

**Option B: Run Separately in Different Terminals**

Terminal 1 - Main Application:
```powershell
python main.py
```

Terminal 2 - Admin Panel:
```powershell
python admin_app.py
```

### 8. Access the Applications

- **Main API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Admin Panel**: http://localhost:8001

## Troubleshooting

### Issue: "psycopg2-binary" installation fails

**Solution**: Skip PostgreSQL support and use SQLite instead:
```powershell
# The base requirements.txt already excludes psycopg2
# SQLite works out of the box, no installation needed
```

### Issue: "Module not found" errors

**Solution**: Ensure virtual environment is activated:
```powershell
# Check if (venv) is in your prompt
# If not, activate it:
venv\Scripts\activate
```

### Issue: Port already in use

**Solution**: Change ports in `.env` file:
```ini
API_PORT=8080
ADMIN_PORT=8081
```

### Issue: Permission errors

**Solution**: Run PowerShell as Administrator or use a different directory:
```powershell
# Move to your Documents folder
cd $env:USERPROFILE\Documents
# Then clone/copy the project here
```

### Issue: "Scripts disabled" error in PowerShell

**Solution**: Enable script execution:
```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: Python not found

**Solution**: Add Python to PATH or use full path:
```powershell
# Find Python installation
where python

# Or use Python Launcher
py -m pip install -r requirements.txt
py main.py
```

## Testing the Installation

### Test 1: Check API Health
```powershell
# Using PowerShell
Invoke-WebRequest -Uri http://localhost:8000/health

# Or open in browser
start http://localhost:8000/docs
```

### Test 2: Login to get Access Token
```powershell
# Create a file called test-login.ps1
$body = @{
    username = "admin"
    password = "admin"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:8000/auth/login" `
    -Method Post `
    -Body $body `
    -ContentType "application/json"

$response.access_token
```

## Database Options

### SQLite (Default - Recommended for Testing)
- ✅ No installation needed
- ✅ Works on all Python versions
- ✅ Perfect for development and testing
- ✅ Single file database
- ❌ Not suitable for high-traffic production

### PostgreSQL
- Requires PostgreSQL server installation
- Install from: https://www.postgresql.org/download/windows/
- Then: `pip install psycopg2-binary`

### MySQL
- Requires MySQL server installation
- Install from: https://dev.mysql.com/downloads/installer/
- Then: `pip install pymysql`

### MS SQL Server
- Requires SQL Server and ODBC Driver
- Install ODBC Driver: https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
- Then: `pip install pyodbc`

## Production Deployment

For production on Windows:

1. **Use a real database** (PostgreSQL, MySQL, or SQL Server)
2. **Change all secret keys** in `.env`
3. **Set `DEBUG=false`** in `.env`
4. **Use HTTPS** with a reverse proxy (IIS, nginx, or Apache)
5. **Run as Windows Service** using NSSM or similar
6. **Set up automatic backups**

### Running as Windows Service

Using NSSM (Non-Sucking Service Manager):

```powershell
# Download NSSM from https://nssm.cc/download

# Install main app as service
nssm install EcommerceConnector "C:\path\to\venv\Scripts\python.exe" "C:\path\to\main.py"

# Install admin panel as service
nssm install EcommerceAdmin "C:\path\to\venv\Scripts\python.exe" "C:\path\to\admin_app.py"

# Start services
nssm start EcommerceConnector
nssm start EcommerceAdmin
```

## Development Tips

### VS Code Setup
1. Install Python extension
2. Select Python interpreter (Ctrl+Shift+P → "Python: Select Interpreter")
3. Choose the venv interpreter

### PyCharm Setup
1. File → Settings → Project → Python Interpreter
2. Add Interpreter → Existing Environment
3. Select `venv\Scripts\python.exe`

## Getting Help

- Check the main [README.md](README.md) for detailed documentation
- Review [QUICKSTART.md](QUICKSTART.md) for a quick start guide
- Check API documentation at http://localhost:8000/docs
- Open an issue on GitHub for bugs or questions

## Next Steps

After installation:
1. Change the default admin password
2. Create a business profile
3. Add your first connection (Shopify or WooCommerce)
4. Set up field mappings
5. Start syncing data!

See [QUICKSTART.md](QUICKSTART.md) for usage examples.
