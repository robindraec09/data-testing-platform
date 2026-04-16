from http.server import BaseHTTPRequestHandler, HTTPServer
import json


# Sample finance API data
account_summary = {
    "accounts": [
        {
            "account_id": "ACC001",
            "account_type": "checking",
            "balance": 2450.50,
            "currency": "USD",
            "last_transaction": "2024-01-15"
        },
        {
            "account_id": "ACC002",
            "account_type": "savings",
            "balance": 15500.00,
            "currency": "USD",
            "last_transaction": "2024-01-16"
        }
    ]
}

transaction_history = {
    "transactions": [
        {
            "account_id": "ACC001",
            "transaction_id": "TXN001",
            "amount": -50.00,
            "description": "Grocery Store",
            "date": "2024-01-15",
            "balance_after": 2450.50
        }
    ]
}


class FinanceMockApiHandler(BaseHTTPRequestHandler):
    def _set_response(self, status=200):
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/v1/accounts":
            self._set_response()
            self.wfile.write(json.dumps(account_summary).encode("utf-8"))
        elif self.path == "/api/v1/transactions":
            self._set_response()
            self.wfile.write(json.dumps(transaction_history).encode("utf-8"))
        elif self.path.startswith("/api/v1/account/"):
            account_id = self.path.split("/")[-1]
            account = next((a for a in account_summary["accounts"] if a["account_id"] == account_id), None)
            if account:
                self._set_response()
                self.wfile.write(json.dumps({"account": account}).encode("utf-8"))
            else:
                self._set_response(404)
                self.wfile.write(json.dumps({"error": "Account not found"}).encode("utf-8"))
        else:
            self._set_response(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def log_message(self, format, *args):
        return


def run(server_class=HTTPServer, handler_class=FinanceMockApiHandler, port=8002):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Finance Mock API running on http://127.0.0.1:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
