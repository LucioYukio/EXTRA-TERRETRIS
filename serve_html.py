import http.server
import sys
import webbrowser
from functools import partial


class CORSHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        self.send_header("Cross-Origin-Resource-Policy", "cross-origin")
        super().end_headers()


PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
directory = sys.argv[2] if len(sys.argv) > 2 else "build/web"

handler = partial(CORSHandler, directory=directory)
print(f"Serving {directory} at http://localhost:{PORT}")
webbrowser.open(f"http://localhost:{PORT}")
http.server.HTTPServer(("", PORT), handler).serve_forever()
