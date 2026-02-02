import logging
import http.server
import socketserver

logger = logging.getLogger(__name__)

PORT = 80

with socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
    logger.info(f"Serving at port {PORT}")
    httpd.serve_forever()