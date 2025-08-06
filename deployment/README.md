# Sandbox Platform Deployment Guide

This comprehensive guide covers the deployment of the Sandbox Platform, a modular microservices architecture designed for Nigerian startups. The platform follows cloud-native principles with Docker containerization, Kubernetes orchestration, and Helm-based automation.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Local Development Setup](#local-development-setup)
4. [Docker Hub Setup](#docker-hub-setup)
5. [Kubernetes Deployment](#kubernetes-deployment)
6. [Helm Charts](#helm-charts)
7. [Environment Configuration](#environment-configuration)
8. [Monitoring and Observability](#monitoring-and-observability)
9. [Security Considerations](#security-considerations)
10. [Troubleshooting](#troubleshooting)
11. [Scaling and Performance](#scaling-and-performance)
12. [Backup and Recovery](#backup-and-recovery)

## Architecture Overview

The Sandbox Platform consists of three core microservices designed for modularity and independent scaling:

### Core Services

1. **Auth Service** - Authentication and authorization service
   - OAuth2 implementation with JWT tokens
   - Nigerian identity verification (NIN/BVN)
   - User management and profile handling
   - Port: 8000

2. **API Gateway** - Central entry point for all requests
   - Request routing and load balancing
   - Rate limiting and circuit breaking
   - Authentication middleware
   - Metrics collection
   - Port: 8080

3. **Config Service** - Centralized configuration management
   - Environment-specific configurations
   - Encrypted sensitive data storage
   - Configuration versioning
   - Hot reload capabilities
   - Port: 8000

### Supporting Infrastructure

- **PostgreSQL** - Primary database for persistent data
- **Redis** - Caching and session storage
- **Prometheus** - Metrics collection and monitoring
- **Grafana** - Visualization and dashboards

## Prerequisites

### Development Environment

- Docker Desktop 4.0+ with Kubernetes enabled
- kubectl 1.25+
- Helm 3.8+
- Python 3.11+
- Node.js 18+ (for frontend development)
- Git

### Production Environment

- Kubernetes cluster 1.25+
- Helm 3.8+
- Docker Hub account or private registry
- PostgreSQL 14+ (managed or self-hosted)
- Redis 7+ (managed or self-hosted)
- SSL certificates for HTTPS
- Domain names for services

### Resource Requirements

#### Minimum (Development)
- 4 CPU cores
- 8GB RAM
- 50GB storage

#### Recommended (Production)
- 8 CPU cores
- 16GB RAM
- 200GB storage
- Load balancer
- Backup storage

## Local Development Setup

### 1. Clone and Setup

```bash
# Clone the repository
git clone <repository-url>
cd sandbox-platform

# Create environment files
cp services/auth-service/.env.example services/auth-service/.env
cp services/api-gateway/.env.example services/api-gateway/.env
cp services/config-service/.env.example services/config-service/.env
```

### 2. Start Infrastructure Services

```bash
# Start PostgreSQL and Redis
docker-compose -f deployment/docker-compose.dev.yml up -d postgres redis

# Wait for services to be ready
sleep 10
```

### 3. Start Application Services

```bash
# Terminal 1 - Auth Service
cd services/auth-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Config Service  
cd services/config-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001

# Terminal 3 - API Gateway
cd services/api-gateway
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

### 4. Verify Setup

```bash
# Check service health
curl http://localhost:8000/health  # Auth Service
curl http://localhost:8001/health  # Config Service
curl http://localhost:8080/health  # API Gateway

# Check API Gateway routing
curl http://localhost:8080/api/v1/auth/health
curl http://localhost:8080/api/v1/configs/health
```

## Docker Hub Setup

### 1. Build and Tag Images

```bash
# Build all service images
./deployment/scripts/build-images.sh

# Or build individually
docker build -t your-username/sandbox-auth-service:1.0.0 services/auth-service/
docker build -t your-username/sandbox-api-gateway:1.0.0 services/api-gateway/
docker build -t your-username/sandbox-config-service:1.0.0 services/config-service/
```

### 2. Push to Docker Hub

```bash
# Login to Docker Hub
docker login

# Push all images
./deployment/scripts/push-images.sh

# Or push individually
docker push your-username/sandbox-auth-service:1.0.0
docker push your-username/sandbox-api-gateway:1.0.0
docker push your-username/sandbox-config-service:1.0.0
```

### 3. Automated CI/CD Pipeline

Create `.github/workflows/build-and-deploy.yml`:

```yaml
name: Build and Deploy

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v2
    
    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}
    
    - name: Build and push images
      run: |
        ./deployment/scripts/build-and-push.sh
```

## Kubernetes Deployment

### 1. Cluster Setup

```bash
# For local development (Docker Desktop)
kubectl config use-context docker-desktop

# For cloud providers
# AWS EKS
eksctl create cluster --name sandbox-platform --region us-west-2

# Google GKE  
gcloud container clusters create sandbox-platform --zone us-central1-a

# Azure AKS
az aks create --resource-group myResourceGroup --name sandbox-platform
```

### 2. Namespace Creation

```bash
# Create namespaces
kubectl create namespace sandbox-dev
kubectl create namespace sandbox-staging  
kubectl create namespace sandbox-prod

# Set default namespace
kubectl config set-context --current --namespace=sandbox-dev
```

### 3. Install Dependencies

```bash
# Add Helm repositories
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install PostgreSQL
helm install postgres bitnami/postgresql \
  --namespace sandbox-dev \
  --set auth.postgresPassword=postgres123 \
  --set auth.database=sandbox

# Install Redis
helm install redis bitnami/redis \
  --namespace sandbox-dev \
  --set auth.password=redis123

# Install Prometheus (optional)
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace
```

### 4. Deploy Application Services

```bash
# Deploy using Helm charts
helm install auth-service ./services/auth-service/helm/auth-service \
  --namespace sandbox-dev \
  --set image.repository=your-username/sandbox-auth-service \
  --set image.tag=1.0.0

helm install config-service ./services/config-service/helm/config-service \
  --namespace sandbox-dev \
  --set image.repository=your-username/sandbox-config-service \
  --set image.tag=1.0.0

helm install api-gateway ./services/api-gateway/helm/api-gateway \
  --namespace sandbox-dev \
  --set image.repository=your-username/sandbox-api-gateway \
  --set image.tag=1.0.0
```

## Helm Charts

### Chart Structure

Each service includes a comprehensive Helm chart:

```
helm/
├── Chart.yaml           # Chart metadata
├── values.yaml          # Default configuration values
├── templates/
│   ├── deployment.yaml  # Kubernetes deployment
│   ├── service.yaml     # Kubernetes service
│   ├── ingress.yaml     # Ingress configuration
│   ├── secret.yaml      # Secrets management
│   ├── configmap.yaml   # Configuration maps
│   └── hpa.yaml         # Horizontal Pod Autoscaler
└── README.md           # Chart documentation
```

### Customization

#### values.yaml Configuration

```yaml
# Image configuration
image:
  repository: your-username/sandbox-auth-service
  tag: "1.0.0"
  pullPolicy: IfNotPresent

# Replica configuration
replicaCount: 3

# Resource limits
resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

# Environment variables
env:
  - name: DATABASE_URL
    value: "postgresql://user:pass@postgres:5432/sandbox"
  - name: REDIS_URL
    value: "redis://redis:6379/0"

# Ingress configuration
ingress:
  enabled: true
  className: "nginx"
  hosts:
    - host: auth.sandbox.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: auth-tls
      hosts:
        - auth.sandbox.example.com
```

#### Environment-Specific Values

```bash
# Development
helm install auth-service ./helm/auth-service \
  --values ./helm/auth-service/values-dev.yaml

# Staging
helm install auth-service ./helm/auth-service \
  --values ./helm/auth-service/values-staging.yaml

# Production
helm install auth-service ./helm/auth-service \
  --values ./helm/auth-service/values-prod.yaml
```

### Helmfile Integration

Create `helmfile.yaml` for coordinated deployments:

```yaml
repositories:
  - name: bitnami
    url: https://charts.bitnami.com/bitnami

releases:
  - name: postgres
    namespace: sandbox-{{ .Environment.Name }}
    chart: bitnami/postgresql
    values:
      - auth:
          postgresPassword: {{ .Environment.Values.postgres.password }}
          database: sandbox

  - name: redis
    namespace: sandbox-{{ .Environment.Name }}
    chart: bitnami/redis
    values:
      - auth:
          password: {{ .Environment.Values.redis.password }}

  - name: auth-service
    namespace: sandbox-{{ .Environment.Name }}
    chart: ./services/auth-service/helm/auth-service
    values:
      - image:
          tag: {{ .Environment.Values.image.tag }}
      - secrets:
          jwtSecretKey: {{ .Environment.Values.auth.jwtSecret }}

environments:
  dev:
    values:
      - postgres:
          password: dev-postgres-123
      - redis:
          password: dev-redis-123
      - image:
          tag: "dev-latest"
      - auth:
          jwtSecret: "dev-jwt-secret"

  prod:
    values:
      - postgres:
          password: {{ requiredEnv "PROD_POSTGRES_PASSWORD" }}
      - redis:
          password: {{ requiredEnv "PROD_REDIS_PASSWORD" }}
      - image:
          tag: "1.0.0"
      - auth:
          jwtSecret: {{ requiredEnv "PROD_JWT_SECRET" }}
```

Deploy with Helmfile:

```bash
# Install helmfile
curl -L https://github.com/roboll/helmfile/releases/download/v0.157.0/helmfile_linux_amd64 -o helmfile
chmod +x helmfile && sudo mv helmfile /usr/local/bin/

# Deploy to development
helmfile -e dev apply

# Deploy to production
helmfile -e prod apply
```

## Environment Configuration

### Development Environment

```yaml
# values-dev.yaml
replicaCount: 1

resources:
  limits:
    cpu: 200m
    memory: 256Mi
  requests:
    cpu: 100m
    memory: 128Mi

env:
  - name: DEBUG
    value: "true"
  - name: LOG_LEVEL
    value: "DEBUG"

ingress:
  enabled: false

autoscaling:
  enabled: false
```

### Staging Environment

```yaml
# values-staging.yaml
replicaCount: 2

resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 250m
    memory: 256Mi

env:
  - name: DEBUG
    value: "false"
  - name: LOG_LEVEL
    value: "INFO"

ingress:
  enabled: true
  hosts:
    - host: staging-auth.sandbox.example.com

autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 5
```

### Production Environment

```yaml
# values-prod.yaml
replicaCount: 3

resources:
  limits:
    cpu: 1000m
    memory: 1Gi
  requests:
    cpu: 500m
    memory: 512Mi

env:
  - name: DEBUG
    value: "false"
  - name: LOG_LEVEL
    value: "WARN"

ingress:
  enabled: true
  hosts:
    - host: auth.sandbox.example.com
  tls:
    - secretName: auth-tls
      hosts:
        - auth.sandbox.example.com

autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
  targetCPUUtilizationPercentage: 70

podDisruptionBudget:
  enabled: true
  minAvailable: 2
```

## Monitoring and Observability

### Prometheus Metrics

Each service exposes metrics at `/metrics`:

```yaml
# ServiceMonitor for Prometheus
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: sandbox-services
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: sandbox
  endpoints:
  - port: http
    path: /metrics
    interval: 30s
```

### Grafana Dashboards

Import pre-built dashboards:

```bash
# Import dashboard JSON
kubectl create configmap grafana-dashboard-sandbox \
  --from-file=deployment/monitoring/grafana-dashboard.json \
  --namespace monitoring
```

### Logging

Configure structured logging:

```yaml
# Fluentd configuration
apiVersion: v1
kind: ConfigMap
metadata:
  name: fluentd-config
data:
  fluent.conf: |
    <source>
      @type tail
      path /var/log/containers/sandbox-*.log
      pos_file /var/log/fluentd-containers.log.pos
      tag kubernetes.*
      format json
    </source>
    
    <match kubernetes.**>
      @type elasticsearch
      host elasticsearch.logging.svc.cluster.local
      port 9200
      index_name sandbox-logs
    </match>
```

### Health Checks

Configure comprehensive health checks:

```yaml
# Deployment with health checks
spec:
  template:
    spec:
      containers:
      - name: auth-service
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
```

## Security Considerations

### Network Policies

```yaml
# Network policy for auth service
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: auth-service-netpol
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/name: auth-service
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app.kubernetes.io/name: api-gateway
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app.kubernetes.io/name: postgres
    ports:
    - protocol: TCP
      port: 5432
```

### Secret Management

```yaml
# Sealed secrets for production
apiVersion: bitnami.com/v1alpha1
kind: SealedSecret
metadata:
  name: auth-secrets
spec:
  encryptedData:
    jwt-secret-key: AgBy3i4OJSWK+PiTySYZZA9rO43cGDEQAx...
    database-password: AgBy3i4OJSWK+PiTySYZZA9rO43cGDEQAx...
```

### RBAC Configuration

```yaml
# Service account and RBAC
apiVersion: v1
kind: ServiceAccount
metadata:
  name: sandbox-service-account
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: sandbox-role
rules:
- apiGroups: [""]
  resources: ["configmaps", "secrets"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: sandbox-role-binding
subjects:
- kind: ServiceAccount
  name: sandbox-service-account
roleRef:
  kind: Role
  name: sandbox-role
  apiGroup: rbac.authorization.k8s.io
```

### Pod Security Standards

```yaml
# Pod security context
spec:
  template:
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
        fsGroup: 2000
      containers:
      - name: auth-service
        securityContext:
          allowPrivilegeEscalation: false
          readOnlyRootFilesystem: true
          capabilities:
            drop:
            - ALL
```

## Troubleshooting

### Common Issues

#### 1. Pod Startup Failures

```bash
# Check pod status
kubectl get pods -n sandbox-dev

# View pod logs
kubectl logs -f deployment/auth-service -n sandbox-dev

# Describe pod for events
kubectl describe pod <pod-name> -n sandbox-dev
```

#### 2. Service Discovery Issues

```bash
# Check service endpoints
kubectl get endpoints -n sandbox-dev

# Test service connectivity
kubectl run debug --image=busybox -it --rm --restart=Never -- nslookup auth-service.sandbox-dev.svc.cluster.local
```

#### 3. Database Connection Issues

```bash
# Check database pod
kubectl logs -f deployment/postgres -n sandbox-dev

# Test database connectivity
kubectl run postgres-client --image=postgres:14 -it --rm --restart=Never -- psql -h postgres.sandbox-dev.svc.cluster.local -U postgres
```

#### 4. Ingress Issues

```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# View ingress configuration
kubectl describe ingress auth-service-ingress -n sandbox-dev

# Check ingress logs
kubectl logs -f deployment/ingress-nginx-controller -n ingress-nginx
```

### Debugging Commands

```bash
# Port forward for local access
kubectl port-forward service/auth-service 8000:8000 -n sandbox-dev

# Execute commands in pod
kubectl exec -it deployment/auth-service -n sandbox-dev -- /bin/bash

# View resource usage
kubectl top pods -n sandbox-dev
kubectl top nodes

# Check cluster events
kubectl get events --sort-by=.metadata.creationTimestamp -n sandbox-dev
```

### Performance Troubleshooting

```bash
# Check resource limits
kubectl describe pod <pod-name> -n sandbox-dev | grep -A 5 "Limits\|Requests"

# Monitor resource usage
kubectl top pod <pod-name> -n sandbox-dev --containers

# Check HPA status
kubectl get hpa -n sandbox-dev
kubectl describe hpa auth-service-hpa -n sandbox-dev
```

## Scaling and Performance

### Horizontal Pod Autoscaling

```yaml
# HPA configuration
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: auth-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: auth-service
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 100
        periodSeconds: 15
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
```

### Vertical Pod Autoscaling

```yaml
# VPA configuration
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: auth-service-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: auth-service
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: auth-service
      maxAllowed:
        cpu: 1
        memory: 2Gi
      minAllowed:
        cpu: 100m
        memory: 128Mi
```

### Load Testing

```bash
# Install k6 for load testing
kubectl apply -f https://raw.githubusercontent.com/grafana/k6-operator/main/bundle.yaml

# Create load test
cat <<EOF | kubectl apply -f -
apiVersion: k6.io/v1alpha1
kind: K6
metadata:
  name: auth-service-load-test
spec:
  parallelism: 4
  script:
    configMap:
      name: auth-load-test-script
      file: test.js
EOF
```

Load test script:

```javascript
// test.js
import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 100 },
    { duration: '2m', target: 200 },
    { duration: '5m', target: 200 },
    { duration: '2m', target: 0 },
  ],
};

export default function () {
  let response = http.get('http://auth-service.sandbox-dev.svc.cluster.local:8000/health');
  check(response, {
    'status is 200': (r) => r.status === 200,
    'response time < 500ms': (r) => r.timings.duration < 500,
  });
  sleep(1);
}
```

## Backup and Recovery

### Database Backup

```yaml
# CronJob for database backup
apiVersion: batch/v1
kind: CronJob
metadata:
  name: postgres-backup
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: postgres-backup
            image: postgres:14
            command:
            - /bin/bash
            - -c
            - |
              pg_dump -h postgres.sandbox-prod.svc.cluster.local \
                      -U postgres \
                      -d sandbox \
                      --no-password \
                      | gzip > /backup/sandbox-$(date +%Y%m%d-%H%M%S).sql.gz
            env:
            - name: PGPASSWORD
              valueFrom:
                secretKeyRef:
                  name: postgres-secret
                  key: password
            volumeMounts:
            - name: backup-storage
              mountPath: /backup
          volumes:
          - name: backup-storage
            persistentVolumeClaim:
              claimName: backup-pvc
          restartPolicy: OnFailure
```

### Configuration Backup

```bash
# Backup Kubernetes configurations
kubectl get all,configmaps,secrets,ingress,pvc -n sandbox-prod -o yaml > backup/k8s-config-$(date +%Y%m%d).yaml

# Backup Helm releases
helm list -n sandbox-prod -o yaml > backup/helm-releases-$(date +%Y%m%d).yaml
```

### Disaster Recovery Plan

1. **Data Recovery**:
   ```bash
   # Restore database from backup
   kubectl exec -it postgres-0 -n sandbox-prod -- psql -U postgres -c "DROP DATABASE IF EXISTS sandbox;"
   kubectl exec -it postgres-0 -n sandbox-prod -- psql -U postgres -c "CREATE DATABASE sandbox;"
   gunzip -c backup/sandbox-20240101-020000.sql.gz | kubectl exec -i postgres-0 -n sandbox-prod -- psql -U postgres -d sandbox
   ```

2. **Service Recovery**:
   ```bash
   # Redeploy services
   helmfile -e prod apply
   
   # Verify service health
   kubectl get pods -n sandbox-prod
   kubectl get ingress -n sandbox-prod
   ```

3. **Data Validation**:
   ```bash
   # Run health checks
   curl -f https://auth.sandbox.example.com/health
   curl -f https://api.sandbox.example.com/health
   
   # Verify database connectivity
   kubectl exec -it deployment/auth-service -n sandbox-prod -- python -c "
   import asyncpg
   import asyncio
   async def test():
       conn = await asyncpg.connect('postgresql://user:pass@postgres:5432/sandbox')
       result = await conn.fetchval('SELECT COUNT(*) FROM users')
       print(f'User count: {result}')
       await conn.close()
   asyncio.run(test())
   "
   ```

This deployment guide provides a comprehensive foundation for deploying and managing the Sandbox Platform in various environments, from local development to production Kubernetes clusters. The modular architecture and Helm-based automation ensure consistent, repeatable deployments while maintaining the flexibility needed for startup environments.

