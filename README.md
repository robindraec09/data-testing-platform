# Data Testing Platform

A comprehensive, production-grade data testing platform that combines data quality validation, ETL pipeline testing, API contract verification, and AI-assisted testing into a single, extensible tool.

## Features

### 🔍 Data Quality Testing
- **Null/Unique Validation**: Ensure data integrity with null checks and uniqueness constraints
- **Range Validation**: Validate numeric ranges and boundaries
- **Regex Pattern Matching**: Custom pattern validation for strings
- **Statistical Profiling**: Automated rule generation based on data patterns

### 🔄 ETL Pipeline Testing
- **Row Count Reconciliation**: Verify source-to-target record counts
- **Checksum Validation**: Data integrity checks across pipeline stages
- **Column Mapping**: Ensure schema consistency
- **Incremental Load Testing**: Validate change data capture processes
- **SCD (Slowly Changing Dimensions)**: Type 1, 2, and 3 validation

### 🌐 API Contract Testing
- **Schema Validation**: JSON Schema compliance checking
- **Response Code Validation**: HTTP status code verification
- **Mock Server Generation**: Automated API mocking for testing
- **Contract Versioning**: Multi-version API support

### 🤖 AI-Assisted Testing
- **ML-Based Anomaly Detection**: Isolation Forest, DBSCAN, and statistical methods
- **Multivariate Anomaly Detection**: Cross-column pattern analysis
- **Seasonal Anomaly Detection**: Time-series based outlier detection
- **Automated Rule Generation**: NLP-driven test creation
- **Data Profiling**: Intelligent data pattern recognition

### 📊 Reporting & Automation
- **Multiple Output Formats**: JSON, JUnit XML, HTML dashboards
- **CI/CD Integration**: GitHub Actions, GitLab CI, Jenkins support
- **Alerting**: Slack, Email, webhook notifications
- **Dashboard Generation**: Interactive HTML reports with visualizations

## Installation

```bash
pip install -r requirements.txt
```

## Quick Start

### 1. Data Quality Testing

Create a test definition file (`data_quality.yaml`):

```yaml
test:
  name: "Customer Data Quality"
  type: "data_quality"
  source:
    type: "file"
    path: "data/customers.csv"
    format: "csv"
  rules:
    - not_null:
        column: "customer_id"
    - unique:
        column: "email"
    - range:
        column: "age"
        min: 18
        max: 120
    - regex:
        column: "email"
        pattern: "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+$"
```

Run the test:

```bash
python -m src.data_test_tool.cli --test data_quality.yaml --output reports
```

### 2. ETL Pipeline Testing

Create an ETL test (`etl_test.yaml`):

```yaml
test:
  name: "Customer ETL Validation"
  type: "etl_pipeline"
  source:
    type: "postgres"
    host: "localhost"
    database: "staging"
    table: "raw_customers"
  target:
    type: "postgres"
    host: "localhost"
    database: "warehouse"
    table: "dim_customers"
  rules:
    - row_count_match: {}
    - checksum_match:
        columns: ["customer_id", "email", "first_name", "last_name"]
    - columns_match: {}
```

### 3. API Contract Testing

Create an API test (`api_contract.yaml`):

```yaml
test:
  name: "User API Contract"
  type: "api_contract"
  source:
    type: "rest"
    url: "https://api.example.com/users"
    method: "GET"
    headers:
      Authorization: "Bearer token"
  rules:
    - response_code:
        value: 200
    - schema:
        file: "schemas/user_response.json"
```

### 4. ML-Based Anomaly Detection

Create an anomaly detection test (`anomaly_detection.yaml`):

```yaml
test:
  name: "Financial Transaction Anomalies"
  type: "anomaly_detection"
  source:
    type: "file"
    path: "data/transactions.csv"
    format: "csv"
  rules:
    - establish_baseline:
        column: "amount"
        method: "isolation_forest"
    - detect_anomalies:
        column: "amount"
        method: "auto"
    - multivariate_anomalies:
        columns: ["amount", "balance", "transaction_count"]
    - seasonal_anomalies:
        column: "amount"
        time_column: "timestamp"
```

## Advanced Features

### Custom Connectors

Extend the platform with custom data connectors:

```python
from src.data_test_tool.connectors.base import BaseConnector

class CustomConnector(BaseConnector):
    def fetch(self, config: dict) -> pd.DataFrame:
        # Implement your custom data fetching logic
        pass
```

### AI Rule Generation

Generate tests automatically from natural language:

```python
from src.data_test_tool.ai import DataProfiler, NLPRuleParser

# Profile your data
profiler = DataProfiler()
profile = profiler.profile_dataframe(df)

# Generate rules from text
parser = NLPRuleParser()
rules = parser.parse("customer email should be valid and age between 18 and 120")
```

### CI/CD Integration

Integrate with your CI/CD pipeline:

```yaml
# .github/workflows/data-tests.yml
name: Data Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Data Tests
        run: |
          pip install -r requirements.txt
          python -m src.data_test_tool.cli --test tests/ --output reports
      - name: Upload Reports
        uses: actions/upload-artifact@v3
        with:
          name: test-reports
          path: reports/
```

## Architecture

```
src/data_test_tool/
├── cli.py                 # Command-line interface
├── connectors/           # Data source connectors
│   ├── base.py          # Abstract base connector
│   ├── file.py          # File-based connectors (CSV, JSON, Parquet)
│   ├── database.py      # Database connectors (PostgreSQL, MySQL, SQL Server)
│   └── api.py           # API/REST connectors
├── engine/              # Core testing engine
│   ├── evaluator.py     # Rule evaluation logic
│   ├── runner.py        # Test execution orchestration
│   ├── etl_validators.py # ETL-specific validation
│   └── api_contract_manager.py # API contract handling
├── models/              # Data models and schemas
│   └── test_definition.py # Unified test definition model
├── reporting/           # Output generation and notifications
│   ├── json_report.py   # JSON report generation
│   ├── junit_report.py  # JUnit XML reports
│   ├── html_report.py   # HTML dashboard generation
│   ├── alerts.py        # Notification system (Slack, Email)
│   └── ci_cd.py         # CI/CD integration
└── ai/                  # AI-assisted testing features
    ├── anomaly_detector.py      # ML-based anomaly detection
    ├── ml_anomaly_detector.py   # Advanced ML algorithms
    ├── generator.py             # Automated rule generation
    ├── nlp.py                   # Natural language processing
    └── profile.py               # Data profiling utilities
```

## Configuration

### Environment Variables

```bash
# Database connections
DB_HOST=localhost
DB_USER=user
DB_PASSWORD=password

# API testing
API_BASE_URL=https://api.example.com
API_TOKEN=your_token

# Notifications
SLACK_WEBHOOK_URL=<your-slack-webhook-url>
EMAIL_SMTP_HOST=smtp.gmail.com
```

### Test Definition Schema

All test definitions follow a unified schema:

```yaml
test:
  name: "Test Name"
  description: "Optional description"
  type: "data_quality|etl_pipeline|api_contract|anomaly_detection|sql_assertion"
  source:  # Source configuration
    type: "file|postgres|mysql|rest|api"
    # ... type-specific config
  target:  # For ETL tests only
    type: "file|postgres|mysql|rest|api"
    # ... type-specific config
  rules:   # Array of validation rules
    - rule_type:
        parameter1: value1
        parameter2: value2
```

## Industry Examples

### Healthcare
- HIPAA compliance validation
- Patient data quality checks
- Medical record ETL verification
- PHI (Protected Health Information) masking validation

### Finance
- PCI DSS compliance testing
- Transaction anomaly detection
- Account balance reconciliation
- Regulatory reporting validation

### Retail/E-commerce
- Product catalog data quality
- Sales order ETL validation
- Inventory reconciliation
- Customer behavior anomaly detection

## Running Examples

### Data Quality Test
```bash
python -m src.data_test_tool.cli --test examples/data_quality.yaml --output reports
```

### ETL Test
```bash
python -m src.data_test_tool.cli --test examples/etl_test.yaml --output reports
```

### API Contract Test
```bash
# Start mock API server
python examples/mock_api.py &
# Run test
python -m src.data_test_tool.cli --test examples/api_contract.yaml --output reports
```

### Anomaly Detection Test
```bash
python -m src.data_test_tool.cli --test examples/anomaly_detection.yaml --output reports
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For questions and support:
- Documentation: [docs/](docs/)
- Issues: [GitHub Issues](https://github.com/your-repo/issues)
- Discussions: [GitHub Discussions](https://github.com/your-repo/discussions)
