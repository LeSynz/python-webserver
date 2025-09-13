from http.server import BaseHTTPRequestHandler, HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(b"<b>Hello World</b>")

server = HTTPServer(("localhost", 3000), Handler)
print('Server started at http://localhost:3000/')
server.serve_forever()