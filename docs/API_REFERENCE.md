# Data Testing Platform API Documentation

## Overview

The Data Testing Platform provides a comprehensive API for building, executing, and managing data quality tests, ETL validations, API contract tests, and AI-assisted anomaly detection.

## Core Classes

### TestRunner

The main entry point for executing test definitions.

```python
from src.data_test_tool.engine.runner import TestRunner

runner = TestRunner()
results = runner.run("path/to/test.yaml")
runner.write_reports(results, "output/directory")
```

#### Methods

- `run(test_path: str) -> List[EvaluationResult]`: Execute a test definition file
- `write_reports(results: List[EvaluationResult], output_dir: str)`: Generate reports in multiple formats

### RuleEvaluator

Core evaluation engine that processes test rules against data sources.

```python
from src.data_test_tool.engine.evaluator import RuleEvaluator

evaluator = RuleEvaluator()
results = evaluator.evaluate(test_definition)
```

#### Supported Test Types

- `data_quality`: Column-level validation rules
- `etl_pipeline`: Source-to-target data pipeline validation
- `api_contract`: API response validation against schemas
- `anomaly_detection`: ML-based outlier detection
- `sql_assertion`: Custom SQL-based validations

## Connectors

### BaseConnector

Abstract base class for all data connectors.

```python
from src.data_test_tool.connectors.base import BaseConnector

class CustomConnector(BaseConnector):
    def fetch(self, config: dict) -> pd.DataFrame:
        # Implement data fetching logic
        pass
```

### FileConnector

Handles file-based data sources (CSV, JSON, Parquet).

```python
connector = FileConnector()
df = connector.fetch({
    "path": "data/file.csv",
    "format": "csv",
    "delimiter": ",",
    "encoding": "utf-8"
})
```

### DatabaseConnector

Supports SQL databases (PostgreSQL, MySQL, SQL Server, Oracle).

```python
connector = DatabaseConnector()
df = connector.fetch({
    "type": "postgres",
    "host": "localhost",
    "database": "mydb",
    "table": "customers",
    "query": "SELECT * FROM customers WHERE active = true"
})
```

### ApiConnector

Handles REST API endpoints and responses.

```python
connector = ApiConnector()
response = connector.fetch({
    "url": "https://api.example.com/users",
    "method": "GET",
    "headers": {"Authorization": "Bearer token"},
    "params": {"limit": 100}
})
```

## AI Features

### AnomalyDetector

Unified interface for anomaly detection using statistical and ML methods.

```python
from src.data_test_tool.ai import AnomalyDetector

detector = AnomalyDetector(contamination=0.1)

# Establish baseline
detector.establish_baseline(df, "amount", method="isolation_forest")

# Detect anomalies
result = detector.detect_anomalies(df, "amount", method="auto")
print(f"Anomalies found: {len(result['anomalies'])}")
```

#### Methods

- `establish_baseline(df, column, method)`: Train detection model on baseline data
- `detect_anomalies(df, column, method)`: Find outliers in data
- `detect_multivariate_anomalies(df, columns)`: Cross-column anomaly detection
- `detect_seasonal_anomalies(df, column, time_column)`: Time-series anomaly detection

### DataProfiler

Automatic data profiling and rule suggestion.

```python
from src.data_test_tool.ai.profile import profile_dataframe, suggest_rules_from_dataframe

# Profile dataset
profile = profile_dataframe(df)
print(f"Columns: {profile['columns']}")
print(f"Null counts: {profile['null_counts']}")

# Generate rules
rules = suggest_rules_from_dataframe(df)
```

### NLPRuleParser

Convert natural language descriptions to test rules.

```python
from src.data_test_tool.ai.nlp import parse_nl_to_rules

rules = parse_nl_to_rules("email should be valid and age between 18 and 120")
# Returns: [{"regex": {...}}, {"range": {...}}]
```

## Reporting

### JSONReportGenerator

Generate JSON-formatted test results.

```python
from src.data_test_tool.reporting.json_report import JSONReportGenerator

generator = JSONReportGenerator()
generator.generate(results, "output/results.json")
```

### JUnitReportGenerator

Generate JUnit XML for CI/CD integration.

```python
from src.data_test_tool.reporting.junit_report import JUnitReportGenerator

generator = JUnitReportGenerator()
generator.generate(results, "output/junit.xml")
```

### HTMLReportGenerator

Create interactive HTML dashboards.

```python
from src.data_test_tool.reporting.html_report import HTMLReportGenerator

generator = HTMLReportGenerator()
generator.generate(results, "output/dashboard.html")
```

### AlertManager

Send notifications via Slack, Email, or webhooks.

```python
from src.data_test_tool.reporting.alerts import AlertManager

alerts = AlertManager()
alerts.send_slack_notification(results, webhook_url)
alerts.send_email(results, smtp_config)
```

## Models

### TestDefinition

Unified test definition model using Pydantic.

```python
from src.data_test_tool.models.test_definition import TestDefinition

test = TestDefinition(
    name="Customer Quality Check",
    type="data_quality",
    source=SourceConfig(type="file", path="customers.csv"),
    rules=[
        RuleDefinition(not_null={"column": "id"}),
        RuleDefinition(unique={"column": "email"})
    ]
)
```

### EvaluationResult

Test execution result model.

```python
class EvaluationResult(BaseModel):
    test_name: str
    rule: dict[str, Any]
    passed: bool
    message: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)
```

## Rule Types

### Data Quality Rules

- `not_null`: Check for null values
  ```yaml
  - not_null:
      column: "customer_id"
  ```

- `unique`: Check for duplicate values
  ```yaml
  - unique:
      column: "email"
  ```

- `range`: Validate numeric ranges
  ```yaml
  - range:
      column: "age"
      min: 18
      max: 120
  ```

- `regex`: Pattern matching
  ```yaml
  - regex:
      column: "email"
      pattern: "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+$"
  ```

### ETL Rules

- `row_count_match`: Source/target count validation
- `checksum_match`: Data integrity validation
- `columns_match`: Schema consistency
- `incremental_load`: Change data validation
- `scd_validation`: Slowly changing dimension checks

### API Contract Rules

- `schema`: JSON Schema validation
- `response_code`: HTTP status validation
- `response_time`: Performance validation

### Anomaly Detection Rules

- `establish_baseline`: Train detection models
- `detect_anomalies`: Find outliers
- `multivariate_anomalies`: Cross-column analysis
- `seasonal_anomalies`: Time-series analysis

## Configuration

### Environment Variables

```bash
# Database connections
DATABASE_URL=postgresql://user:pass@localhost/db

# API endpoints
API_BASE_URL=https://api.example.com
API_TOKEN=your_jwt_token

# Notifications
SLACK_WEBHOOK=<your-slack-webhook-url>
SMTP_HOST=smtp.gmail.com
SMTP_USER=your_email@gmail.com
```

### YAML Configuration

Test definitions use YAML for configuration:

```yaml
test:
  name: "Comprehensive Test"
  type: "data_quality"
  source:
    type: "postgres"
    host: "localhost"
    database: "analytics"
    table: "users"
  rules:
    - not_null:
        column: "user_id"
    - unique:
        column: "email"
    - range:
        column: "signup_year"
        min: 2020
        max: 2024
```

## Error Handling

The platform provides comprehensive error handling:

```python
try:
    results = runner.run("test.yaml")
except ValueError as e:
    print(f"Configuration error: {e}")
except ConnectionError as e:
    print(f"Data source connection failed: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Performance Considerations

- Use appropriate data sampling for large datasets
- Cache baseline models for repeated anomaly detection
- Implement connection pooling for database connectors
- Use async processing for multiple test executions

## Extensibility

### Custom Connectors

```python
from src.data_test_tool.connectors.base import BaseConnector

class S3Connector(BaseConnector):
    def fetch(self, config: dict) -> pd.DataFrame:
        import boto3
        s3 = boto3.client('s3')
        obj = s3.get_object(Bucket=config['bucket'], Key=config['key'])
        return pd.read_csv(obj['Body'])
```

### Custom Rules

```python
# Extend evaluator with custom rule types
def evaluate_custom_rule(df: pd.DataFrame, config: dict) -> EvaluationResult:
    # Implement custom validation logic
    pass
```

### Custom Reports

```python
from src.data_test_tool.reporting.base import BaseReportGenerator

class CustomReportGenerator(BaseReportGenerator):
    def generate(self, results, output_path):
        # Implement custom report format
        pass
```

## Best Practices

1. **Test Organization**: Group related tests in separate files
2. **Baseline Management**: Regularly update anomaly detection baselines
3. **Error Monitoring**: Implement alerting for test failures
4. **Performance**: Use sampling for large datasets
5. **Version Control**: Keep test definitions in version control
6. **Documentation**: Document custom rules and connectors

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Connection Failures**: Verify connection strings and credentials
3. **Schema Mismatches**: Check data types and column names
4. **Memory Issues**: Use data sampling for large datasets

### Debug Mode

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Validation

Validate test definitions before execution:

```python
from src.data_test_tool.models.test_definition import TestDefinition

try:
    test = TestDefinition(**yaml_content)
    print("Test definition is valid")
except ValidationError as e:
    print(f"Validation error: {e}")
```