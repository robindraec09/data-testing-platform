# Industry-Specific Examples

This directory contains real-world examples demonstrating the unified data testing platform across different industries.

## Healthcare Examples

### Patient Data Quality Testing
- **File**: `patient_quality.yaml`
- **Data**: `patient_data.csv`
- **Features**:
  - HIPAA-compliant data validation
  - Blood type format validation
  - Age range checks
  - Medication data integrity

### Healthcare API Contract Testing
- **File**: `api_contract.yaml`
- **Mock API**: `mock_healthcare_api.py`
- **Features**:
  - Patient record schema validation
  - Lab results API testing
  - Individual patient lookup validation

## Finance Examples

### Transaction Data Quality Testing
- **File**: `transaction_quality.yaml`
- **Data**: `transaction_data.csv`
- **Features**:
  - Account ID format validation
  - Balance range checks
  - Transaction amount validation
  - Date format compliance

### Financial ETL Reconciliation
- **File**: `etl_reconciliation.yaml`
- **Source**: `transaction_data.csv`
- **Target**: `account_balances.csv`
- **Features**:
  - Account balance reconciliation
  - Incremental load validation
  - Checksum verification

## Retail Examples

### Product Catalog Quality Testing
- **File**: `product_quality.yaml`
- **Data**: `product_catalog.csv`
- **Features**:
  - Product ID format validation
  - Price range checks
  - Stock quantity validation
  - Supplier ID verification

### Retail Sales ETL Validation
- **File**: `etl_sales.yaml`
- **Source**: `product_catalog.csv`
- **Target**: `sales_orders.csv`
- **Features**:
  - Product reference integrity
  - Sales order validation
  - Incremental sales data loading

## Running Industry Examples

### Healthcare
```bash
# Start mock API
python examples/industries/healthcare/mock_healthcare_api.py &
# Run tests
python -m data_test_tool.cli --test examples/industries/healthcare/patient_quality.yaml --output reports
python -m data_test_tool.cli --test examples/industries/healthcare/api_contract.yaml --output reports
```

### Finance
```bash
python -m data_test_tool.cli --test examples/industries/finance/transaction_quality.yaml --output reports
python -m data_test_tool.cli --test examples/industries/finance/etl_reconciliation.yaml --output reports
```

### Retail
```bash
python -m data_test_tool.cli --test examples/industries/retail/product_quality.yaml --output reports
python -m data_test_tool.cli --test examples/industries/retail/etl_sales.yaml --output reports
```

## Industry-Specific Considerations

### Healthcare
- PHI (Protected Health Information) compliance
- Medical data format validation
- Regulatory reporting requirements
- Patient privacy constraints

### Finance
- PCI DSS compliance for payment data
- Financial reporting accuracy
- Regulatory audit trails
- Real-time transaction validation

### Retail
- Product catalog management
- Inventory accuracy
- Sales transaction integrity
- Customer data validation

## AI-Enhanced Industry Testing

The platform's AI features can be particularly valuable for industry-specific testing:

```python
from data_test_tool.ai.generator import generate_rules_from_dataframe
from data_test_tool.ai.anomaly_detector import AnomalyDetector

# Healthcare anomaly detection
detector = AnomalyDetector()
detector.establish_baseline(healthcare_df, 'patient_age')
anomalies = detector.detect_anomalies(new_patient_data, 'patient_age')

# Finance fraud detection
fraud_detector = AnomalyDetector()
fraud_detector.establish_baseline(transaction_df, 'transaction_amount')
suspicious_transactions = fraud_detector.detect_anomalies(new_transactions, 'transaction_amount')
```

These examples demonstrate how the unified platform can be adapted to industry-specific requirements while maintaining consistent testing patterns and extensibility.
