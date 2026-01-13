# Web UI Guide - User-Friendly Dashboard

A beautiful, modern web interface for managing your SQL to E-commerce connections.

## Features

✨ **Beautiful Dashboard** - Modern, responsive design with real-time statistics
🔐 **Secure Login** - JWT-based authentication
📊 **Visual Analytics** - Charts and statistics for monitoring syncs
🏢 **Business Management** - Easy creation and management of business profiles
🔌 **Connection Builder** - Visual interface for adding database and platform connections
🗺️ **Field Mapper** - Drag-and-drop field mapping interface
📝 **Sync Logs** - Real-time monitoring of synchronization operations
📱 **Responsive** - Works on desktop, tablet, and mobile

## Quick Start

### 1. Start the API Server

```bash
# In terminal 1
python main.py
```

### 2. Start the Web UI Server

```bash
# In terminal 2
python web_server.py
```

### 3. Open Your Browser

Go to: **http://localhost:3000/login.html**

Default credentials:
- Username: `admin`
- Password: `admin`

## Screenshot Tour

### Login Page
Modern, gradient-based login page with secure authentication

### Dashboard
- View total business profiles, connections, and mappings
- Real-time sync statistics
- Recent activity timeline
- Quick action buttons

### Business Profiles
- Create business profiles for each company/website
- Manage contact information
- View associated connections

### Connections
- Add database connections (PostgreSQL, MySQL, MS SQL, SQLite)
- Add platform connections (Shopify, WooCommerce)
- Test connections with one click
- View connection status

### Field Mappings
- Visual field mapping builder
- Drag and drop interface
- Configure sync direction (To Platform, From Platform, Bidirectional)
- Set sync intervals
- Preview mappings before saving

### Sync Logs
- View all sync operations
- Filter by date, status, or mapping
- See success/failure statistics
- Export logs

## Architecture

```
┌─────────────────────────────────────────────────┐
│                  Web Browser                     │
│         http://localhost:3000                    │
└────────────────┬────────────────────────────────┘
                 │
                 │ HTTP/JavaScript
                 │
┌────────────────▼────────────────────────────────┐
│            Web Server (Python)                   │
│         Serves HTML/CSS/JS files                 │
│              Port: 3000                          │
└────────────────┬────────────────────────────────┘
                 │
                 │ REST API Calls
                 │
┌────────────────▼────────────────────────────────┐
│         FastAPI Backend (main.py)                │
│           Business Logic & API                   │
│              Port: 8000                          │
└─────────────────────────────────────────────────┘
```

## File Structure

```
web/
├── login.html           # Login page
├── dashboard.html       # Main dashboard
├── businesses.html      # Business management
├── connections.html     # Connection management
├── mappings.html        # Field mapping builder
├── logs.html           # Sync logs viewer
├── css/
│   └── style.css       # Custom styles
└── js/
    └── common.js       # Common JavaScript functions
```

## Features by Page

### Login Page
- Secure authentication
- Remember credentials
- Password visibility toggle
- Error handling

### Dashboard
- Statistics cards (profiles, connections, mappings, syncs)
- Recent activity feed
- Quick actions menu
- Business profile overview

### Businesses Page
- Create new business profiles
- Edit existing profiles
- Delete profiles (with confirmation)
- View connections per business
- Search and filter

### Connections Page
- Add database connections
- Add platform connections (Shopify/WooCommerce)
- Test connection status
- Enable/disable connections
- View connection details
- Edit connection settings

### Mappings Page
- Visual field mapping builder
- Select source database and table
- Select destination platform and resource
- Drag-and-drop field matching
- Configure sync direction
- Set sync interval
- Save and activate mappings

### Logs Page
- View all sync operations
- Filter by:
  - Date range
  - Status (completed, running, failed)
  - Mapping ID
  - Business profile
- Export logs to CSV/JSON
- View detailed error messages

## API Integration

The web UI communicates with the FastAPI backend:

```javascript
// Example API call
const response = await fetch('http://localhost:8000/profiles', {
    method: 'GET',
    headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    }
});
```

All API calls are handled in `js/common.js` with:
- Automatic token management
- Error handling
- Loading states
- Toast notifications

## Customization

### Change Colors

Edit `web/css/style.css`:

```css
/* Change primary gradient */
.bg-gradient {
    background: linear-gradient(135deg, #YOUR_COLOR1 0%, #YOUR_COLOR2 100%);
}
```

### Change API URL

Edit `web/js/common.js`:

```javascript
const API_URL = 'http://your-server:8000';
```

### Change Port

Edit `web_server.py`:

```python
PORT = 3000  # Change to your preferred port
```

## Security

### In Development
- Uses HTTP
- Simple password authentication
- LocalStorage for tokens

### For Production
1. **Use HTTPS** - Enable SSL/TLS
2. **Secure Cookies** - Use httpOnly cookies instead of localStorage
3. **CORS Policy** - Restrict to specific domains
4. **Rate Limiting** - Enable API rate limiting
5. **Strong Passwords** - Enforce password policies
6. **Two-Factor Auth** - Add 2FA support

## Troubleshooting

### Cannot connect to API

**Problem**: "Cannot connect to server" error

**Solution**:
1. Make sure `main.py` is running
2. Check API is accessible at http://localhost:8000
3. Open http://localhost:8000/health to verify

### CORS Errors

**Problem**: "Access blocked by CORS policy"

**Solution**:
1. Make sure both servers are running
2. Check `main.py` has CORS middleware configured
3. Verify API_URL in `common.js` is correct

### Not Logged In

**Problem**: Redirects to login page immediately

**Solution**:
1. Check browser console for errors
2. Verify token is stored in localStorage
3. Re-login with correct credentials

### Styles Not Loading

**Problem**: Page looks broken, no styles

**Solution**:
1. Make sure web server is running
2. Check `web/css/style.css` exists
3. Clear browser cache (Ctrl+Shift+R)

## Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## Mobile Support

The UI is fully responsive and works on:
- 📱 Mobile phones (320px+)
- 📱 Tablets (768px+)
- 💻 Desktops (1024px+)

## Keyboard Shortcuts

- `Ctrl/Cmd + K` - Quick search
- `Ctrl/Cmd + S` - Save current form
- `Escape` - Close modals
- `Enter` - Submit forms

## Tips & Tricks

1. **Quick Profile Switch**: Click profile name in navbar
2. **Bulk Actions**: Select multiple items with checkboxes
3. **Export Data**: Use export buttons to download data
4. **Dark Mode**: Toggle in user menu (coming soon)
5. **Keyboard Navigation**: Tab through forms faster

## Next Steps

After accessing the web UI:

1. **Create a Business Profile**
   - Go to "Businesses" page
   - Click "Add New Business"
   - Fill in details

2. **Add Database Connection**
   - Go to "Connections" page
   - Click "Add Database"
   - Enter server details
   - Test connection

3. **Add Platform Connection**
   - Go to "Connections" page
   - Click "Add Platform"
   - Choose Shopify or WooCommerce
   - Enter API credentials

4. **Create Field Mapping**
   - Go to "Mappings" page
   - Select connections
   - Map fields visually
   - Set sync interval
   - Save and activate

5. **Monitor Syncs**
   - Check dashboard for statistics
   - View logs for detailed information
   - Enable/disable as needed

## Getting Help

- 📖 Read the main [README.md](README.md)
- 🚀 Check [QUICKSTART.md](QUICKSTART.md)
- 🌐 View API docs at http://localhost:8000/docs
- 💬 Open an issue on GitHub

Enjoy your beautiful new dashboard! 🎉
