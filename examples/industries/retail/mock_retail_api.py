from http.server import BaseHTTPRequestHandler, HTTPServer
import json


# Sample retail API data
product_inventory = {
    "products": [
        {
            "product_id": "PRD001",
            "name": "Wireless Headphones",
            "category": "Electronics",
            "price": 199.99,
            "stock_quantity": 50,
            "supplier_id": "SUP001"
        },
        {
            "product_id": "PRD002",
            "name": "Cotton T-Shirt",
            "category": "Clothing",
            "price": 29.99,
            "stock_quantity": 200,
            "supplier_id": "SUP002"
        }
    ]
}

order_status = {
    "orders": [
        {
            "order_id": "ORD001",
            "customer_id": "CUST001",
            "status": "shipped",
            "total_amount": 199.99,
            "order_date": "2024-01-15"
        }
    ]
}


class RetailMockApiHandler(BaseHTTPRequestHandler):
    def _set_response(self, status=200):
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/v1/products":
            self._set_response()
            self.wfile.write(json.dumps(product_inventory).encode("utf-8"))
        elif self.path == "/api/v1/orders":
            self._set_response()
            self.wfile.write(json.dumps(order_status).encode("utf-8"))
        elif self.path.startswith("/api/v1/product/"):
            product_id = self.path.split("/")[-1]
            product = next((p for p in product_inventory["products"] if p["product_id"] == product_id), None)
            if product:
                self._set_response()
                self.wfile.write(json.dumps({"product": product}).encode("utf-8"))
            else:
                self._set_response(404)
                self.wfile.write(json.dumps({"error": "Product not found"}).encode("utf-8"))
        else:
            self._set_response(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def log_message(self, format, *args):
        return


def run(server_class=HTTPServer, handler_class=RetailMockApiHandler, port=8003):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Retail Mock API running on http://127.0.0.1:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
