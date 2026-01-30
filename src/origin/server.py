import time
import http.server
import socketserver

PORT = 8000

class MyHandler(http.server.SimpleHTTPRequestHandler):

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "max-age=600, public")
        return super().end_headers()

    def do_GET(self) -> None:
        time.sleep(1)
        return super().do_GET()

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()