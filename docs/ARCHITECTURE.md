# Full Architecture & Documentation

## Overview

This document defines a production-grade architecture for a unified data testing platform that combines:

- Data Quality Testing
- ETL / Pipeline Testing
- API / Data Contract Testing
- AI-Assisted Test Generation

The goal is a single platform with a flexible, extensible rule definition engine and a layered architecture that supports multiple data sources, reporting outputs, and automation.

---

## 1. High-Level Architecture

The platform is built as a layered architecture with the following components:

1. Connectors Layer
2. AI-Assisted Intelligence Layer
3. Test Engine Layer
4. Rule Definition Layer
5. Reporting & Observability Layer
6. Automation & CI/CD Layer

Each layer is designed to be modular and pluggable.

---

## 2. Layer 1: Connectors Layer

### Purpose

Abstract all source and target interfaces so test logic can run uniformly across:

- Databases
- Files
- APIs
- Pipeline metadata systems

### Supported source types

- Databases: Snowflake, BigQuery, Postgres, SQL Server, Oracle, MySQL
- Files: CSV, Parquet, JSON, Excel
- APIs: REST, GraphQL, gRPC (optional)
- Pipelines: Airflow, dbt, Kafka, Spark

### Components

- `ConnectorFactory`
- `DatabaseConnector`
- `FileConnector`
- `ApiConnector`
- `PipelineMetadataConnector`

### Responsibilities

- Connect to sources securely
- Load metadata and schemas
- Read data frames or query results
- Support connection pooling and credential rotation

---

## 3. Layer 2: AI-Assisted Intelligence Layer

### Purpose

Provide value-add capabilities beyond static rules using profiling, NLP, and anomaly detection.

### Capabilities

- Auto-generate test cases from schema and sample data
- Suggest anomaly detection rules
- Detect distribution drift and feature drift
- Generate SQL assertions automatically
- Convert natural language to a unified test definition

### Example usage

User input:

> "Check if customer data is clean."

AI output:

- Null checks on required columns
- Email regex validation
- Age range validation
- Duplicate `customer_id` detection
- Referential integrity with `orders` table

### Components

- `AiRuleGenerator`
- `SchemaProfiler`
- `DriftDetector`
- `NlpParser`

---

## 4. Layer 3: Test Engine

The platform's central execution engine runs tests across the three major domains.

### 4.1 Data Quality Testing Engine

Supports:

- Null / not-null checks
- Unique constraints
- Regex validation
- Range checks
- Schema validation
- Freshness checks
- Distribution checks
- Drift detection

### 4.2 ETL / Pipeline Testing Engine

Supports:

- Source → target reconciliation
- Row count matching
- Checksums / hash comparisons
- Transformation logic validation
- Incremental load validation
- Slowly changing dimension (SCD) validation

### 4.3 API / Data Contract Testing Engine

Supports:

- JSON schema validation
- Field type validation
- Response time SLAs
- Contract versioning
- API-to-database consistency checks

### Core components

- `TestRunner`
- `TestExecutor`
- `RuleEvaluator`
- `ResultAggregator`
- `FailureReporter`

---

## 5. Layer 4: Rule Definition Layer

### Purpose

Allow users to express tests in multiple ways while preserving a single underlying model.

### Supported definitions

1. YAML / JSON test files
2. SQL assertions
3. Natural language definitions via AI

### Unified test model sample

```yaml
test:
  name: customer_data_integrity
  type: data_quality
  source: customers
  rules:
    - not_null: customer_id
    - unique: customer_id
    - regex:
        column: email
        pattern: "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+$"
```

API contract example:

```yaml
test:
  name: orders_api_contract
  type: api_contract
  endpoint: /orders
  rules:
    - schema: order_schema.json
    - max_response_time: 500ms
```
```

### Rule categories

- Column-level rules
- Table-level rules
- Source-target comparison rules
- API response and contract rules
- AI-generated suggestion rules

---

## 6. Layer 5: Reporting & Observability

### Reports

- HTML summary reports
- JSON result payloads
- JUnit XML for CI/CD

### Dashboards

- Data quality score
- Pipeline health score
- API contract compliance
- Trend analysis and historical drift

### Alerts

- Slack
- Microsoft Teams
- Email
- Webhooks

### Observability components

- `ReportGenerator`
- `DashboardExporter`
- `AlertDispatcher`
- `MetricsPublisher`

---

## 7. Layer 6: Automation & CI/CD

### Purpose

Make testing part of the deployment lifecycle.

### Integration points

- GitHub Actions
- GitLab CI
- Azure DevOps
- Jenkins
- Airflow DAGs
- dbt run/test

### Automation capabilities

- Test execution from Git commits
- Scheduled pipeline health checks
- Regression detection across releases
- Automatic alerting on quality failures

---

## 8. Non-Obvious Insight: Unified Test Definition

A single test definition model should support both data and API domains.

### Benefits

- Easier extensibility
- Shared validation concepts
- Less context switching for users
- Future-proof architecture

### Example unified model

```yaml
test:
  name: customer_data_integrity
  type: data_quality
  source: customers
  rules:
    - not_null: customer_id
    - unique: customer_id
    - regex:
        column: email
        pattern: email
```

```yaml
test:
  name: orders_api_contract
  type: api_contract
  endpoint: /orders
  rules:
    - schema: order_schema.json
    - max_response_time: 500ms
```

---

## 9. Recommended Tech Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- Pandas / Polars
- PySpark (optional)
- Great Expectations (inspiration)

### AI Layer

- OpenAI / Azure OpenAI
- Hugging Face models
- Custom anomaly detection

### Frontend (optional)

- React
- Next.js
- Tailwind

### Storage

- PostgreSQL
- SQLite (local/dev mode)

### Optional test automation

- Playwright for API/UI flows
- `pytest` for internal test suites

---

## 10. Project Folder Structure

```text
./
├── README.md
├── docs/
│   └── ARCHITECTURE.md
├── src/
│   ├── connectors/
│   │   ├── base.py
│   │   ├── database.py
│   │   ├── file.py
│   │   └── api.py
│   ├── engine/
│   │   ├── runner.py
│   │   ├── evaluator.py
│   │   └── results.py
│   ├── models/
│   │   ├── test_definition.py
│   │   └── rule.py
│   ├── reporting/
│   │   ├── json_report.py
│   │   ├── junit_report.py
│   │   └── html_report.py
│   ├── ai/
│   │   ├── profile.py
│   │   ├── generator.py
│   │   └── nlp.py
│   ├── cli.py
│   └── api.py
├── tests/
│   ├── unit/
│   └── integration/
└── examples/
    ├── data_quality.yaml
    ├── etl_test.yaml
    └── api_contract.yaml
```

---

## 11. Phase Plan

### Phase 1: Core Platform

- Build connector abstraction
- Implement unified YAML/JSON test model
- Build rule engine for data quality and SQL assertions
- Create CLI runner and JSON/JUnit reporting

### Phase 2: ETL / Pipeline Testing

- Add source-target reconciliation
- Implement row count / checksum validation
- Support incremental load and transformation assertions

### Phase 3: API / Contract Testing

- Add REST/GraphQL request execution
- Add JSON schema validation
- Support response time SLAs and contract versioning
- Add API-to-DB consistency checks

### Phase 4: AI-Assisted Testing

- Add profiling and auto-rule generation
- Add natural language → test conversion
- Add drift and anomaly detection

### Phase 5: Reporting & Automation

- Add dashboard exports and trend reports
- Add Slack/Teams/Webhook alerts
- Add CI/CD pipeline templates and Airflow/dbt integration

---

## 12. Sample YAML Test Definition

```yaml
test:
  name: customer_data_integrity
  type: data_quality
  source:
    type: postgres
    connection: ${PG_CONN}
    table: customers
  rules:
    - not_null:
        column: customer_id
    - unique:
        column: customer_id
    - regex:
        column: email
        pattern: '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+$'
    - range:
        column: age
        min: 0
        max: 120
```

---

## 13. Example API Contract Definition

```yaml
test:
  name: orders_api_contract
  type: api_contract
  source:
    type: rest
    url: https://api.example.com/orders
    method: GET
    headers:
      Authorization: Bearer ${API_TOKEN}
  rules:
    - schema:
        file: schemas/order_schema.json
    - max_response_time: 500ms
    - response_code: 200
```

---

## 14. Deployment and CI/CD

### Recommended pipeline steps

1. `install` dependencies
2. `lint` and `unit test`
3. `compile` or validate test definitions
4. `run` platform tests
5. `publish` JSON/JUnit reports
6. `notify` via alerts on failure

### Sample CI outputs

- `reports/results.json`
- `reports/results.xml`
- `reports/summary.html`

---

## 15. Next Deliverables

To make this architecture actionable, the next implementation step is:

- scaffold Phase 1 project files
- generate sample test YAML definitions
- add a CLI-based test runner

Optional additions:

- architecture diagrams in `docs/` as Mermaid or images
- sample `docker-compose` for local execution
- API docs for the FastAPI server
