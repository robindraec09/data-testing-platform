from http.server import BaseHTTPRequestHandler, HTTPServer
import json


data = {
    "orders": [
        {"order_id": 1, "customer_id": 1, "amount": 42.5, "status": "shipped"},
        {"order_id": 2, "customer_id": 2, "amount": 19.95, "status": "processing"}
    ]
}


class MockApiHandler(BaseHTTPRequestHandler):
    def _set_response(self, status=200):
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def do_GET(self):
        if self.path == "/orders":
            self._set_response()
            self.wfile.write(json.dumps(data).encode("utf-8"))
        else:
            self._set_response(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode("utf-8"))

    def log_message(self, format, *args):
        return


def run(server_class=HTTPServer, handler_class=MockApiHandler, port=8000):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Mock API running on http://127.0.0.1:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
