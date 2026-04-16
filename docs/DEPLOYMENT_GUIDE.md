# Data Testing Platform Deployment Guide

## Overview

This guide covers deploying the Data Testing Platform in various environments including Docker, cloud platforms, and production setups.

## Docker Deployment

### Step 1: Create Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY examples/ ./examples/
COPY pyproject.toml .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port for web interface (if implemented)
EXPOSE 8000

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python", "-m", "src.data_test_tool.cli", "--help"]
```

### Step 2: Create Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  data-testing-platform:
    build: .
    volumes:
      - ./tests:/app/tests
      - ./reports:/app/reports
      - ./config:/app/config
    environment:
      - DATABASE_URL=postgresql://user:pass@postgres:5432/testdb
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis
    networks:
      - testing-network

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: testdb
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    networks:
      - testing-network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    networks:
      - testing-network

volumes:
  postgres_data:

networks:
  testing-network:
    driver: bridge
```

### Step 3: Build and Run

```bash
# Build the image
docker-compose build

# Run tests
docker-compose run --rm data-testing-platform \
  python -m src.data_test_tool.cli --test tests/ --output reports

# Run with custom config
docker-compose run --rm \
  -e DATABASE_URL=postgresql://prod:pass@prod-db:5432/prod \
  data-testing-platform \
  python -m src.data_test_tool.cli --test production_tests/
```

## Cloud Deployment

### AWS Deployment

#### Step 1: Create ECS Task Definition

Create `ecs-task-definition.json`:

```json
{
  "family": "data-testing-platform",
  "taskRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "executionRoleArn": "arn:aws:iam::123456789012:role/ecsTaskExecutionRole",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "data-testing-platform",
      "image": "123456789012.dkr.ecr.us-east-1.amazonaws.com/data-testing-platform:latest",
      "essential": true,
      "environment": [
        {"name": "DATABASE_URL", "value": "${DATABASE_URL}"},
        {"name": "SLACK_WEBHOOK", "value": "${SLACK_WEBHOOK}"},
        {"name": "AWS_REGION", "value": "us-east-1"}
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/data-testing-platform",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

#### Step 2: Create Lambda Function

For scheduled testing, create `lambda_function.py`:

```python
import boto3
import json
import os
from src.data_test_tool.engine.runner import TestRunner

def lambda_handler(event, context):
    # Initialize runner
    runner = TestRunner()

    # Run tests
    test_path = os.environ.get('TEST_PATH', 's3://bucket/tests/')
    output_path = os.environ.get('OUTPUT_PATH', 's3://bucket/reports/')

    # Download test files from S3
    s3 = boto3.client('s3')
    # ... download logic ...

    # Run tests
    results = runner.run(test_path)
    runner.write_reports(results, '/tmp/reports')

    # Upload results to S3
    # ... upload logic ...

    # Send notifications
    failed_tests = [r for r in results if not r.passed]
    if failed_tests:
        # Send SNS notification
        sns = boto3.client('sns')
        sns.publish(
            TopicArn=os.environ['SNS_TOPIC_ARN'],
            Subject='Data Testing Platform - Test Failures',
            Message=f'Found {len(failed_tests)} test failures'
        )

    return {
        'statusCode': 200,
        'body': json.dumps({
            'total_tests': len(results),
            'failed_tests': len(failed_tests)
        })
    }
```

#### Step 3: CloudFormation Template

Create `cloudformation.yaml`:

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Data Testing Platform Infrastructure'

Parameters:
  VpcId:
    Type: String
    Description: VPC ID
  SubnetIds:
    Type: List<AWS::EC2::Subnet::Id>
    Description: Subnet IDs

Resources:
  ECSCluster:
    Type: AWS::ECS::Cluster
    Properties:
      ClusterName: data-testing-platform

  ECSTaskDefinition:
    Type: AWS::ECS::TaskDefinition
    Properties:
      Family: data-testing-platform
      Cpu: 1024
      Memory: 2048
      NetworkMode: awsvpc
      ExecutionRoleArn: !GetAtt ECSExecutionRole.Arn
      ContainerDefinitions:
        - Name: data-testing-platform
          Image: !Ref ECRRepositoryUri
          Essential: true
          Environment:
            - Name: DATABASE_URL
              Value: !Ref DatabaseURL
            - Name: SLACK_WEBHOOK
              Value: !Ref SlackWebhook
          LogConfiguration:
            LogDriver: awslogs
            Options:
              awslogs-group: !Ref LogGroup
              awslogs-region: !Ref AWS::Region

  ECSExecutionRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: ecs-tasks.amazonaws.com
            Action: sts:AssumeRole
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

  LogGroup:
    Type: AWS::Logs::LogGroup
    Properties:
      LogGroupName: /ecs/data-testing-platform
      RetentionInDays: 30

  ScheduledRule:
    Type: AWS::Events::Rule
    Properties:
      Description: Daily data testing
      ScheduleExpression: rate(1 day)
      State: ENABLED
      Targets:
        - Id: DataTestingTask
          Arn: !GetAtt ECSCluster.Arn
          RoleArn: !GetAtt EventRole.Arn
          EcsParameters:
            TaskDefinitionArn: !Ref ECSTaskDefinition
            TaskCount: 1
            LaunchType: FARGATE
            NetworkConfiguration:
              AwsVpcConfiguration:
                Subnets: !Ref SubnetIds
                SecurityGroups:
                  - !Ref SecurityGroup

  EventRole:
    Type: AWS::IAM::Role
    Properties:
      AssumeRolePolicyDocument:
        Version: '2012-10-17'
        Statement:
          - Effect: Allow
            Principal:
              Service: events.amazonaws.com
            Action: sts:AssumeRole
      Policies:
        - PolicyName: ecs-execution
          PolicyDocument:
            Version: '2012-10-17'
            Statement:
              - Effect: Allow
                Action: ecs:RunTask
                Resource: !Ref ECSTaskDefinition

  SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Security group for data testing platform
      VpcId: !Ref VpcId
      SecurityGroupEgress:
        - IpProtocol: tcp
          FromPort: 0
          ToPort: 65535
          CidrIp: 0.0.0.0/0
```

### Google Cloud Platform

#### Step 1: Cloud Run Deployment

Create `cloud-run.yaml`:

```yaml
apiVersion: serving.knuckles.dev/v1
kind: Service
metadata:
  name: data-testing-platform
spec:
  template:
    spec:
      containers:
      - image: gcr.io/project-id/data-testing-platform:latest
        env:
        - name: DATABASE_URL
          value: /secrets/database-url
        - name: SLACK_WEBHOOK
          value: /secrets/slack-webhook
        resources:
          limits:
            cpu: 1000m
            memory: 2Gi
```

#### Step 2: Cloud Scheduler

Create scheduled runs using Cloud Scheduler:

```bash
gcloud scheduler jobs create http data-testing-daily \
  --schedule="0 2 * * *" \
  --uri="https://data-testing-platform-abc123.run.app/run-tests" \
  --http-method=POST \
  --oauth-service-account-email=service@project.iam.gserviceaccount.com
```

### Azure Deployment

#### Step 1: Azure Container Instances

Create `aci-deployment.yaml`:

```yaml
apiVersion: '2019-12-01'
location: eastus
name: data-testing-platform
properties:
  containers:
  - name: data-testing-platform
    properties:
      image: myregistry.azurecr.io/data-testing-platform:latest
      environmentVariables:
      - name: DATABASE_URL
        secureValue: $DATABASE_URL
      - name: SLACK_WEBHOOK
        secureValue: $SLACK_WEBHOOK
      resources:
        requests:
          cpu: 1.0
          memoryInGB: 2.0
  osType: Linux
  restartPolicy: Never
tags: {}
type: Microsoft.ContainerInstance/containerGroups
```

#### Step 2: Azure Functions

For serverless deployment:

```python
import azure.functions as func
from src.data_test_tool.engine.runner import TestRunner

def main(req: func.HttpRequest) -> func.HttpResponse:
    runner = TestRunner()

    # Get test configuration from request
    test_config = req.get_json()

    # Run tests
    results = runner.run(test_config['test_path'])

    # Return results
    return func.HttpResponse(
        json.dumps(results),
        mimetype="application/json"
    )
```

## Production Setup

### Step 1: Environment Configuration

Create `.env` file:

```bash
# Database connections
DATABASE_URL=postgresql://user:pass@prod-db.company.com:5432/production
WAREHOUSE_URL=snowflake://user:pass@account.snowflakecomputing.com/database/schema

# API endpoints
API_BASE_URL=https://api.company.com
API_TOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...

# Notifications
SLACK_WEBHOOK=<your-slack-webhook-url>
EMAIL_SMTP_HOST=smtp.company.com
EMAIL_SMTP_USER=alerts@company.com
EMAIL_SMTP_PASS=<secure-password>

# Monitoring
DATADOG_API_KEY=<your-datadog-api-key>
PROMETHEUS_PUSHGATEWAY=http://prometheus-pushgateway.company.com:9091

# Security
ENCRYPTION_KEY=your-256-bit-secret
JWT_SECRET=another-secure-secret

# Performance
MAX_WORKERS=4
BATCH_SIZE=1000
TIMEOUT_SECONDS=300
```

### Step 2: Production Dockerfile

Create `Dockerfile.prod`:

```dockerfile
FROM python:3.11-slim

# Install production dependencies
RUN apt-get update && apt-get install -y \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir gunicorn

# Copy application
COPY --chown=appuser:appuser . .

# Create necessary directories
RUN mkdir -p /app/reports /app/logs /app/cache && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run with gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "src.data_test_tool.web:app"]
```

### Step 3: Kubernetes Deployment

Create `k8s-deployment.yaml`:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: data-testing-platform
  labels:
    app: data-testing-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: data-testing-platform
  template:
    metadata:
      labels:
        app: data-testing-platform
    spec:
      containers:
      - name: data-testing-platform
        image: company-registry.com/data-testing-platform:latest
        ports:
        - containerPort: 8000
        envFrom:
        - secretRef:
            name: data-testing-secrets
        resources:
          requests:
            cpu: 500m
            memory: 1Gi
          limits:
            cpu: 2000m
            memory: 4Gi
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: config-volume
          mountPath: /app/config
        - name: reports-volume
          mountPath: /app/reports
      volumes:
      - name: config-volume
        configMap:
          name: data-testing-config
      - name: reports-volume
        persistentVolumeClaim:
          claimName: reports-pvc

---
apiVersion: v1
kind: Service
metadata:
  name: data-testing-platform
spec:
  selector:
    app: data-testing-platform
  ports:
    - port: 80
      targetPort: 8000
  type: ClusterIP

---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: data-testing-platform
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  rules:
  - host: data-testing.company.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: data-testing-platform
            port:
              number: 80
```

### Step 4: Monitoring Setup

Create `monitoring.yaml`:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
      - job_name: 'data-testing-platform'
        static_configs:
          - targets: ['data-testing-platform:8000']

---
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: data-testing-platform
spec:
  selector:
    matchLabels:
      app: data-testing-platform
  endpoints:
  - port: web
    path: /metrics
```

### Step 5: Backup Strategy

Create `backup-job.yaml`:

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: data-testing-backup
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: backup
            image: google/cloud-sdk:alpine
            command:
            - /bin/sh
            - -c
            - |
              gsutil -m rsync -r /app/reports gs://backups/data-testing-reports/$(date +%Y-%m-%d)
              gsutil -m rsync -r /app/config gs://backups/data-testing-config/$(date +%Y-%m-%d)
          restartPolicy: OnFailure
          volumes:
          - name: reports-volume
            persistentVolumeClaim:
              claimName: reports-pvc
          - name: config-volume
            configMap:
              name: data-testing-config
```

## Security Considerations

### Step 1: Secret Management

Use Kubernetes secrets or cloud secret managers:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: data-testing-secrets
type: Opaque
data:
  database-url: <base64-encoded-url>
  slack-webhook: <base64-encoded-webhook>
  encryption-key: <base64-encoded-key>
```

### Step 2: Network Security

Configure network policies:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: data-testing-network-policy
spec:
  podSelector:
    matchLabels:
      app: data-testing-platform
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
  - to: []
    ports:
    - protocol: TCP
      port: 443  # HTTPS for external APIs
```

### Step 3: RBAC Configuration

Create role-based access control:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: data-testing-role
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps", "secrets"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
- apiGroups: ["batch"]
  resources: ["jobs", "cronjobs"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: data-testing-rolebinding
subjects:
- kind: ServiceAccount
  name: data-testing-sa
roleRef:
  kind: Role
  name: data-testing-role
  apiGroup: rbac.authorization.k8s.io
```

## Performance Tuning

### Step 1: Resource Optimization

Configure resource limits based on workload:

```yaml
resources:
  requests:
    cpu: 500m
    memory: 1Gi
  limits:
    cpu: 2000m
    memory: 4Gi
```

### Step 2: Database Connection Pooling

Implement connection pooling for database connectors:

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=3600
)
```

### Step 3: Caching Strategy

Implement Redis caching for frequently accessed data:

```python
import redis
from src.data_test_tool.connectors.cache import CacheManager

cache = CacheManager(redis_url=os.environ.get('REDIS_URL'))

@cache.cached(ttl=3600)
def fetch_large_dataset(query):
    # Expensive operation
    return execute_query(query)
```

## Troubleshooting Production Issues

### Step 1: Logging Configuration

Configure structured logging:

```python
import logging
import json
from pythonjsonlogger import jsonlogger

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    fmt='%(asctime)s %(name)s %(levelname)s %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### Step 2: Health Checks

Implement comprehensive health checks:

```python
from flask import Flask, jsonify
import psycopg2
import redis

app = Flask(__name__)

@app.route('/health')
def health():
    checks = {
        'database': check_database(),
        'redis': check_redis(),
        'disk_space': check_disk_space()
    }

    overall_status = 'healthy' if all(checks.values()) else 'unhealthy'

    return jsonify({
        'status': overall_status,
        'checks': checks,
        'timestamp': datetime.utcnow().isoformat()
    })

def check_database():
    try:
        conn = psycopg2.connect(os.environ['DATABASE_URL'])
        conn.close()
        return True
    except:
        return False

def check_redis():
    try:
        r = redis.from_url(os.environ['REDIS_URL'])
        r.ping()
        return True
    except:
        return False

def check_disk_space():
    stat = os.statvfs('/app')
    free_space = stat.f_bavail * stat.f_frsize
    return free_space > 1e9  # 1GB free
```

### Step 3: Metrics Collection

Add Prometheus metrics:

```python
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('request_count', 'Total requests', ['method', 'endpoint'])
REQUEST_LATENCY = Histogram('request_latency', 'Request latency', ['method', 'endpoint'])

@app.route('/metrics')
def metrics():
    return generate_latest()

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    latency = time.time() - request.start_time
    REQUEST_COUNT.labels(request.method, request.path).inc()
    REQUEST_LATENCY.labels(request.method, request.path).observe(latency)
    return response
```

## Scaling Strategies

### Horizontal Scaling

Scale pods based on CPU utilization:

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: data-testing-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: data-testing-platform
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Database Scaling

Use read replicas for reporting workloads:

```python
class ReadWriteDatabaseConnector(DatabaseConnector):
    def __init__(self, read_url: str, write_url: str):
        self.read_engine = create_engine(read_url)
        self.write_engine = create_engine(write_url)

    def fetch(self, config: dict) -> pd.DataFrame:
        # Use read replica for SELECT queries
        return pd.read_sql(config['query'], self.read_engine)

    def execute_query(self, config: dict, query: str):
        # Use write instance for modifications
        with self.write_engine.connect() as conn:
            return conn.execute(text(query))
```

## Backup and Recovery

### Automated Backups

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/$DATE"

mkdir -p $BACKUP_DIR

# Backup configurations
cp -r /app/config $BACKUP_DIR/

# Backup reports
cp -r /app/reports $BACKUP_DIR/

# Backup database
pg_dump $DATABASE_URL > $BACKUP_DIR/database.sql

# Compress and upload to cloud storage
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
gsutil cp $BACKUP_DIR.tar.gz gs://backups/

# Cleanup old backups (keep last 30 days)
gsutil ls gs://backups/ | head -n -30 | xargs gsutil rm
```

### Disaster Recovery

Create recovery procedures:

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: data-testing-restore
spec:
  template:
    spec:
      containers:
      - name: restore
        image: postgres:15
        command:
        - /bin/sh
        - -c
        - |
          gsutil cp gs://backups/latest.tar.gz /tmp/
          tar -xzf /tmp/latest.tar.gz -C /tmp/
          psql $DATABASE_URL < /tmp/latest/database.sql
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: url
      restartPolicy: Never
```

This deployment guide provides comprehensive instructions for deploying the Data Testing Platform in various environments, from simple Docker setups to complex production Kubernetes deployments with monitoring, security, and scaling considerations.