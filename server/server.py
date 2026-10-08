from http.server import HTTPServer, BaseHTTPRequestHandler

PORT = 8000


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if not self.path.startswith("/output"):
            self.send_error(404)
            return

        try:
            with open("output" + self.path, "rb") as f:
                data = f.read()

            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Content-Disposition", 'attachment; filename="app.bin"')
            self.end_headers()
            self.wfile.write(data)

        except FileNotFoundError:
            self.send_error(404, "File not found")

server = HTTPServer(("0.0.0.0", PORT), Handler)

print(f"Serving files on http://0.0.0.0:{PORT}")

server.serve_forever()

