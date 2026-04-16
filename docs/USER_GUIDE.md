# Data Testing Platform User Guide

## Getting Started

### Installation

1. Clone the repository:
```bash
git clone https://github.com/your-org/data-testing-platform.git
cd data-testing-platform
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Verify installation:
```bash
python -m src.data_test_tool.cli --help
```

## Tutorial 1: Data Quality Testing

### Step 1: Prepare Your Data

Create a sample CSV file (`customers.csv`):

```csv
customer_id,name,email,age,city
1,John Doe,john@example.com,30,New York
2,Jane Smith,jane@example.com,25,Los Angeles
3,Bob Johnson,bob@invalid,150,Boston
4,Alice Brown,,28,Chicago
```

### Step 2: Create Test Definition

Create `customer_quality.yaml`:

```yaml
test:
  name: "Customer Data Quality Check"
  description: "Validate customer data integrity"
  type: "data_quality"
  source:
    type: "file"
    path: "customers.csv"
    format: "csv"
  rules:
    - not_null:
        column: "customer_id"
    - unique:
        column: "customer_id"
    - regex:
        column: "email"
        pattern: "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+$"
    - range:
        column: "age"
        min: 18
        max: 120
```

### Step 3: Run the Test

```bash
python -m src.data_test_tool.cli --test customer_quality.yaml --output reports
```

### Step 4: Review Results

Check the generated reports in the `reports/` directory:

- `results.json`: Detailed JSON results
- `results.xml`: JUnit XML format
- `dashboard.html`: Interactive HTML dashboard

## Tutorial 2: ETL Pipeline Testing

### Step 1: Set Up Source and Target Data

Create source data (`source_orders.csv`):

```csv
order_id,customer_id,product,quantity,price
1001,1,Laptop,1,1200.00
1002,2,Mouse,2,25.00
1003,1,Keyboard,1,75.00
```

Create target data (`target_orders.csv`):

```csv
order_id,customer_id,product,quantity,price,total
1001,1,Laptop,1,1200.00,1200.00
1002,2,Mouse,2,25.00,50.00
1003,1,Keyboard,1,75.00,75.00
```

### Step 2: Create ETL Test

Create `etl_validation.yaml`:

```yaml
test:
  name: "Order ETL Validation"
  type: "etl_pipeline"
  source:
    type: "file"
    path: "source_orders.csv"
    format: "csv"
  target:
    type: "file"
    path: "target_orders.csv"
    format: "csv"
  rules:
    - row_count_match: {}
    - checksum_match:
        columns: ["order_id", "customer_id", "quantity", "price"]
    - columns_match: {}
```

### Step 3: Run ETL Test

```bash
python -m src.data_test_tool.cli --test etl_validation.yaml --output reports
```

## Tutorial 3: API Contract Testing

### Step 1: Start Mock API Server

Create `mock_user_api.py`:

```python
from flask import Flask, jsonify
import json

app = Flask(__name__)

@app.route('/api/users')
def get_users():
    return jsonify({
        "users": [
            {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "age": 30
            },
            {
                "id": 2,
                "name": "Jane Smith",
                "email": "jane@example.com",
                "age": 25
            }
        ]
    })

if __name__ == '__main__':
    app.run(port=5000)
```

Start the server:

```bash
python mock_user_api.py
```

### Step 2: Create JSON Schema

Create `user_schema.json`:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "users": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {"type": "integer"},
          "name": {"type": "string"},
          "email": {"type": "string", "format": "email"},
          "age": {"type": "integer", "minimum": 0, "maximum": 150}
        },
        "required": ["id", "name", "email"]
      }
    }
  },
  "required": ["users"]
}
```

### Step 3: Create API Test

Create `api_contract.yaml`:

```yaml
test:
  name: "User API Contract Test"
  type: "api_contract"
  source:
    type: "rest"
    url: "http://localhost:5000/api/users"
    method: "GET"
  rules:
    - response_code:
        value: 200
    - schema:
        file: "user_schema.json"
```

### Step 4: Run API Test

```bash
python -m src.data_test_tool.cli --test api_contract.yaml --output reports
```

## Tutorial 4: Anomaly Detection

### Step 1: Prepare Transaction Data

Create `transactions.csv` with some anomalies:

```csv
timestamp,account_id,amount,balance
2024-01-01,ACC001,100.00,1000.00
2024-01-02,ACC001,-50.00,950.00
2024-01-03,ACC001,200.00,1150.00
2024-01-04,ACC001,-25.00,1125.00
2024-01-05,ACC001,5000.00,6125.00  # Anomaly: unusually large deposit
2024-01-06,ACC001,-10000.00,-3875.00  # Anomaly: large withdrawal
2024-01-07,ACC001,150.00,-3725.00
```

### Step 2: Create Anomaly Detection Test

Create `anomaly_test.yaml`:

```yaml
test:
  name: "Transaction Anomaly Detection"
  type: "anomaly_detection"
  source:
    type: "file"
    path: "transactions.csv"
    format: "csv"
  rules:
    - establish_baseline:
        column: "amount"
        method: "isolation_forest"
    - detect_anomalies:
        column: "amount"
        method: "auto"
    - seasonal_anomalies:
        column: "amount"
        time_column: "timestamp"
```

### Step 3: Run Anomaly Detection

```bash
python -m src.data_test_tool.cli --test anomaly_test.yaml --output reports
```

## Tutorial 5: CI/CD Integration

### Step 1: Create GitHub Actions Workflow

Create `.github/workflows/data-tests.yml`:

```yaml
name: Data Tests
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  data-tests:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt

    - name: Run data quality tests
      run: |
        python -m src.data_test_tool.cli --test tests/data_quality/ --output test-results

    - name: Run ETL tests
      run: |
        python -m src.data_test_tool.cli --test tests/etl/ --output test-results

    - name: Upload test results
      uses: actions/upload-artifact@v3
      with:
        name: data-test-results
        path: test-results/

    - name: Fail on test failures
      run: |
        if [ -f test-results/results.json ]; then
          python -c "
          import json
          with open('test-results/results.json') as f:
              results = json.load(f)
          failures = [r for r in results if not r['passed']]
          if failures:
              print(f'Found {len(failures)} test failures')
              exit(1)
          "
        fi
```

### Step 2: Organize Test Files

Create directory structure:

```
tests/
├── data_quality/
│   ├── customer_tests.yaml
│   └── product_tests.yaml
├── etl/
│   ├── customer_etl.yaml
│   └── sales_etl.yaml
└── api/
    └── user_api.yaml
```

### Step 3: Run Tests Locally

```bash
python -m src.data_test_tool.cli --test tests/ --output test-results
```

## Tutorial 6: Custom Connectors

### Step 1: Create Custom Connector

Create `custom_connector.py`:

```python
from src.data_test_tool.connectors.base import BaseConnector
import pandas as pd
import requests

class WeatherAPIConnector(BaseConnector):
    """Custom connector for weather API data."""

    def fetch(self, config: dict) -> pd.DataFrame:
        api_key = config.get('api_key')
        city = config.get('city', 'London')

        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            'q': city,
            'appid': api_key,
            'units': 'metric'
        }

        response = requests.get(url, params=params)
        response.raise_for_status()

        data = response.json()
        return pd.DataFrame([{
            'city': data['name'],
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'pressure': data['main']['pressure'],
            'timestamp': pd.Timestamp.now()
        }])
```

### Step 2: Register Custom Connector

Update the evaluator to include your custom connector:

```python
# In your test script or custom evaluator
from custom_connector import WeatherAPIConnector

evaluator = RuleEvaluator()
evaluator.connectors['weather'] = WeatherAPIConnector()
```

### Step 3: Use Custom Connector

Create `weather_test.yaml`:

```yaml
test:
  name: "Weather Data Quality"
  type: "data_quality"
  source:
    type: "weather"
    api_key: "your_openweather_api_key"
    city: "New York"
  rules:
    - range:
        column: "temperature"
        min: -50
        max: 60
    - range:
        column: "humidity"
        min: 0
        max: 100
```

## Tutorial 7: Alerting and Notifications

### Step 1: Configure Slack Alerts

Create `alert_config.yaml`:

```yaml
alerts:
  slack:
    webhook_url: "https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
    channel: "#data-alerts"
  email:
    smtp_host: "smtp.gmail.com"
    smtp_port: 587
    username: "your-email@gmail.com"
    password: "your-app-password"
    recipients: ["team@company.com"]
```

### Step 2: Create Alerting Test

Create `monitored_test.yaml`:

```yaml
test:
  name: "Critical Data Pipeline"
  type: "etl_pipeline"
  source:
    type: "postgres"
    host: "prod-db.company.com"
    database: "production"
    table: "orders"
  target:
    type: "postgres"
    host: "warehouse.company.com"
    database: "analytics"
    table: "fact_orders"
  rules:
    - row_count_match: {}
    - checksum_match:
        columns: ["order_id", "customer_id", "total_amount"]
  alerts:
    on_failure:
      - slack: "Data pipeline validation failed!"
      - email: "Urgent: ETL pipeline issues detected"
```

### Step 3: Run with Alerting

```bash
python -c "
from src.data_test_tool.engine.runner import TestRunner
from src.data_test_tool.reporting.alerts import AlertManager

runner = TestRunner()
alerts = AlertManager()

# Load alert config
import yaml
with open('alert_config.yaml') as f:
    config = yaml.safe_load(f)

results = runner.run('monitored_test.yaml')
runner.write_reports(results, 'reports')

# Send alerts for failures
failed_results = [r for r in results if not r.passed]
if failed_results:
    alerts.send_slack_notification(failed_results, config['alerts']['slack']['webhook_url'])
    alerts.send_email_alert(failed_results, config['alerts']['email'])
"
```

## Tutorial 8: Advanced AI Features

### Step 1: Automated Rule Generation

```python
from src.data_test_tool.ai.profile import suggest_rules_from_dataframe
from src.data_test_tool.ai.nlp import parse_nl_to_rules
import pandas as pd

# Load your data
df = pd.read_csv('customer_data.csv')

# Generate rules from data patterns
auto_rules = suggest_rules_from_dataframe(df)
print("Auto-generated rules:", auto_rules)

# Generate rules from natural language
nl_rules = parse_nl_to_rules('customer id should be unique, email must be valid format, age between 18 and 120')
print("NLP-generated rules:", nl_rules)
```

### Step 2: Multivariate Anomaly Detection

Create `multivariate_anomaly.yaml`:

```yaml
test:
  name: "Customer Behavior Analysis"
  type: "anomaly_detection"
  source:
    type: "postgres"
    host: "analytics.company.com"
    database: "customer_db"
    query: "SELECT customer_id, login_count, purchase_amount, support_tickets FROM customer_metrics WHERE created_date >= '2024-01-01'"
  rules:
    - multivariate_anomalies:
        columns: ["login_count", "purchase_amount", "support_tickets"]
```

### Step 3: Custom AI Models

```python
from src.data_test_tool.ai.ml_anomaly_detector import MLAnomalyDetector
import pandas as pd

# Create custom ML detector
detector = MLAnomalyDetector(contamination=0.05, random_state=42)

# Load training data
training_data = pd.read_csv('normal_transactions.csv')

# Train on normal data
detector.establish_baseline(training_data, 'amount', 'isolation_forest')

# Detect anomalies in new data
new_data = pd.read_csv('current_transactions.csv')
result = detector.detect_anomalies_ml(new_data, 'amount')

print(f"Anomalies detected: {len(result['anomalies'])}")
```

## Best Practices

### Test Organization
- Group tests by domain (data_quality/, etl/, api/)
- Use descriptive names for test files
- Include comments in YAML files

### Performance Optimization
- Use data sampling for large datasets
- Cache baseline models
- Run tests in parallel when possible

### Error Handling
- Always check connection configurations
- Validate data schemas before testing
- Implement retry logic for flaky connections

### Monitoring
- Set up alerts for critical test failures
- Monitor test execution times
- Track test success rates over time

## Troubleshooting

### Common Issues

1. **Connection Errors**
   - Verify database credentials
   - Check network connectivity
   - Ensure API endpoints are accessible

2. **Schema Mismatches**
   - Validate column names and data types
   - Check for missing required fields
   - Update test definitions after schema changes

3. **Performance Issues**
   - Use LIMIT clauses for large tables
   - Implement data sampling
   - Optimize query performance

4. **False Positives in Anomaly Detection**
   - Adjust contamination parameter
   - Update baselines with new normal data
   - Use domain knowledge to filter results

### Debug Commands

```bash
# Enable debug logging
export PYTHONPATH=src
python -c "import logging; logging.basicConfig(level=logging.DEBUG)"

# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('test.yaml'))"

# Test connector independently
python -c "
from src.data_test_tool.connectors.file import FileConnector
connector = FileConnector()
df = connector.fetch({'path': 'data.csv', 'format': 'csv'})
print(df.head())
"
```

## Next Steps

- Explore advanced AI features in the API documentation
- Set up automated testing in your CI/CD pipeline
- Create custom connectors for your specific data sources
- Implement comprehensive monitoring and alerting
- Contribute back to the project with new features