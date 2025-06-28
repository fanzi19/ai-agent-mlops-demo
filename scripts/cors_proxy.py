from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import json

class CORSHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_cors_headers()
        self.end_headers()
    
    def do_POST(self):
        if self.path in ['/predict', '/health']:
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                
                # Forward to actual API
                response = requests.post(
                    f"http://localhost:8000{self.path}",
                    data=post_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                self.send_cors_headers()
                self.wfile.write(response.content)
            except Exception as e:
                print(f"Error: {e}")
                self.send_error(500)
        else:
            self.send_error(404)
    
    def do_GET(self):
        if self.path == '/health':
            try:
                response = requests.get("http://localhost:8000/health", timeout=10)
                self.send_cors_headers()
                self.wfile.write(response.content)
            except Exception as e:
                print(f"Error: {e}")
                self.send_error(500)
        else:
            self.send_error(404)
    
    def send_cors_headers(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Content-Type', 'application/json')

if __name__ == '__main__':
    try:
        server = HTTPServer(('0.0.0.0', 8001), CORSHandler)
        print("🌍 CORS proxy running on port 8001")
        print("📡 Forwarding requests to http://localhost:8000")
        server.serve_forever()
    except Exception as e:
        print(f"❌ Failed to start CORS proxy: {e}")
