import http.server
import socketserver
import webbrowser
from pathlib import Path

START_PORT = 8000
PORT_TRIES = 10
HTML_FILE = "pdlc_arch_v1.html"


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def bind(directory: str):
    handler = lambda *args, **kwargs: http.server.SimpleHTTPRequestHandler(
        *args, directory=directory, **kwargs
    )
    for offset in range(PORT_TRIES):
        port = START_PORT + offset
        try:
            return ReusableTCPServer(("", port), handler), port
        except OSError as e:
            if e.errno != 48:
                raise
    raise SystemExit(
        f"Could not bind any port in {START_PORT}-{START_PORT + PORT_TRIES - 1}."
    )


if __name__ == "__main__":
    directory = str(Path(__file__).parent.resolve())
    httpd, port = bind(directory)
    with httpd:
        url = f"http://localhost:{port}/{HTML_FILE}"
        print(f"Serving {directory} at {url}")
        print("Press Ctrl+C to stop.")
        webbrowser.open(url)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server.")
