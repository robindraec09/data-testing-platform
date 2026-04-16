from http.server import BaseHTTPRequestHandler, HTTPServer
import json


# Sample healthcare API data
patient_records = {
    "patients": [
        {
            "patient_id": "P001",
            "gender": "M",
            "age": 45,
            "blood_type": "O+",
            "diagnosis_date": "2024-01-15",
            "medication": "Lisinopril"
        },
        {
            "patient_id": "P002",
            "gender": "F",
            "age": 32,
            "blood_type": "A-",
            "diagnosis_date": "2024-02-20",
            "medication": "Metformin"
        }
    ]
}

lab_results = {
    "results": [
        {
            "patient_id": "P001",
            "test_name": "Blood Glucose",
            "value": 95,
            "unit": "mg/dL",
            "reference_range": "70-100",
            "test_date": "2024-01-15"
        }
    ]
}


class HealthcareMockApiHandler(BaseHTTPRequestHandler):
    def _set_response(self, status=200):
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/v1/patients":
            self._set_response()
            self.wfile.write(json.dumps(patient_records).encode("utf-8"))
        elif self.path == "/api/v1/lab-results":
            self._set_response()
            self.wfile.write(json.dumps(lab_results).encode("utf-8"))
        elif self.path.startswith("/api/v1/patient/"):
            patient_id = self.path.split("/")[-1]
            patient = next((p for p in patient_records["patients"] if p["patient_id"] == patient_id), None)
            if patient:
                self._set_response()
                self.wfile.write(json.dumps({"patient": patient}).encode("utf-8"))
            else:
                self._set_response(404)
                self.wfile.write(json.dumps({"error": "Patient not found"}).encode("utf-8"))
        else:
            self._set_response(404)
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode("utf-8"))

    def log_message(self, format, *args):
        return


def run(server_class=HTTPServer, handler_class=HealthcareMockApiHandler, port=8001):
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    print(f"Healthcare Mock API running on http://127.0.0.1:{port}")
    httpd.serve_forever()


if __name__ == "__main__":
    run()
