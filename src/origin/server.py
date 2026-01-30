import logging
import time
import http.server
import socketserver

logger = logging.getLogger(__name__)

PORT = 80

class MyHandler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self) -> None:
        time.sleep(1)
        return super().do_GET()

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    logger.info(f"Serving at port {PORT}")
    httpd.serve_forever()