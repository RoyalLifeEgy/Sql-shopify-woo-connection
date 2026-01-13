"""
Simple HTTP server to serve the web UI
"""
import http.server
import socketserver
import os

PORT = 3000
DIRECTORY = "web"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║     SQL E-commerce Connector - Web UI Server            ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝

🌐 Web UI: http://localhost:{PORT}
🚀 Login Page: http://localhost:{PORT}/login.html

📌 Default Credentials:
   Username: admin
   Password: admin

ℹ️  Make sure the API server is running at http://localhost:8000

Press Ctrl+C to stop the server
""")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n✓ Server stopped")
