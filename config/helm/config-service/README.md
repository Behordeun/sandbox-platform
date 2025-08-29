# Config Service Helm Chart

This Helm chart deploys the Sandbox Platform Configuration Service on a Kubernetes cluster.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.8+
- Redis instance (for configuration storage)

## Installing the Chart

To install the chart with the release name `config-service`:

```bash
helm install config-service ./config-service
```

## Uninstalling the Chart

To uninstall/delete the `config-service` deployment:

```bash
helm uninstall config-service
```

## Configuration

The following table lists the configurable parameters of the Config Service chart and their default values.

### Image Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `image.repository` | Config Service image repository | `sandbox-config-service` |
| `image.tag` | Config Service image tag | `1.0.0` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |

### Deployment Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `2` |
| `nameOverride` | Override the name of the chart | `""` |
| `fullnameOverride` | Override the fullname of the chart | `""` |

### Service Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `service.type` | Kubernetes service type | `ClusterIP` |
| `service.port` | Service port | `8000` |
| `service.targetPort` | Container port | `8000` |

### Ingress Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ingress.enabled` | Enable ingress | `false` |
| `ingress.className` | Ingress class name | `""` |
| `ingress.annotations` | Ingress annotations | `{}` |
| `ingress.hosts` | Ingress hosts configuration | `[{host: config-service.local, paths: [{path: /, pathType: Prefix}]}]` |
| `ingress.tls` | Ingress TLS configuration | `[]` |

### Resource Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `resources.limits.cpu` | CPU limit | `500m` |
| `resources.limits.memory` | Memory limit | `512Mi` |
| `resources.requests.cpu` | CPU request | `250m` |
| `resources.requests.memory` | Memory request | `256Mi` |

### Autoscaling Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `autoscaling.enabled` | Enable horizontal pod autoscaler | `false` |
| `autoscaling.minReplicas` | Minimum number of replicas | `2` |
| `autoscaling.maxReplicas` | Maximum number of replicas | `5` |
| `autoscaling.targetCPUUtilizationPercentage` | Target CPU utilization | `70` |
| `autoscaling.targetMemoryUtilizationPercentage` | Target memory utilization | `80` |

### Environment Variables

| Parameter | Description | Default |
|-----------|-------------|---------|
| `env[].name` | Environment variable name | Various |
| `env[].value` | Environment variable value | Various |

### Security Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `secrets.encryptionKey` | Configuration encryption key | `your-encryption-key-change-in-production` |
| `secrets.jwtSecretKey` | JWT secret key | `your-jwt-secret-key-change-in-production` |
| `podSecurityContext.fsGroup` | Pod security context fsGroup | `2000` |
| `podSecurityContext.runAsNonRoot` | Run as non-root user | `true` |
| `podSecurityContext.runAsUser` | User ID to run as | `1000` |

### Storage Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `persistence.enabled` | Enable persistent storage | `false` |
| `persistence.storageClass` | Storage class name | `""` |
| `persistence.accessMode` | Access mode | `ReadWriteOnce` |
| `persistence.size` | Storage size | `1Gi` |
| `persistence.mountPath` | Mount path for storage | `/app/configs` |

### Health Check Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `healthCheck.enabled` | Enable liveness probe | `true` |
| `healthCheck.path` | Health check path | `/health` |
| `healthCheck.initialDelaySeconds` | Initial delay for liveness probe | `30` |
| `readinessCheck.enabled` | Enable readiness probe | `true` |
| `readinessCheck.path` | Readiness check path | `/health` |

### Monitoring Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `serviceMonitor.enabled` | Enable Prometheus ServiceMonitor | `false` |
| `serviceMonitor.namespace` | ServiceMonitor namespace | `monitoring` |
| `serviceMonitor.interval` | Scrape interval | `30s` |
| `serviceMonitor.path` | Metrics path | `/metrics` |

### Network Policy Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `networkPolicy.enabled` | Enable network policy | `false` |
| `networkPolicy.ingress` | Ingress rules | See values.yaml |
| `networkPolicy.egress` | Egress rules | See values.yaml |

## Examples

### Basic Installation

```bash
helm install config-service ./config-service \
  --set image.repository=myregistry/sandbox-config-service \
  --set image.tag=v1.0.0
```

### Production Installation with Persistence

```bash
helm install config-service ./config-service \
  --set image.repository=myregistry/sandbox-config-service \
  --set image.tag=v1.0.0 \
  --set persistence.enabled=true \
  --set persistence.size=10Gi \
  --set secrets.encryptionKey=my-secure-encryption-key \
  --set secrets.jwtSecretKey=my-secure-jwt-secret
```

### High Availability Setup

```bash
helm install config-service ./config-service \
  --set replicaCount=3 \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=3 \
  --set autoscaling.maxReplicas=10 \
  --set podDisruptionBudget.enabled=true \
  --set podDisruptionBudget.minAvailable=2
```

### With Monitoring

```bash
helm install config-service ./config-service \
  --set serviceMonitor.enabled=true \
  --set serviceMonitor.namespace=monitoring
```

### File Storage Backend

```bash
helm install config-service ./config-service \
  --set env[0].name=CONFIG_STORAGE_TYPE \
  --set env[0].value=file \
  --set persistence.enabled=true \
  --set persistence.size=5Gi \
  --set fileStorage.enabled=true
```

## Dependencies

This chart requires the following services to be available:

1. **Redis** - For configuration storage (default backend)
   ```bash
   helm install redis bitnami/redis
   ```

## Storage Backends

The Config Service supports multiple storage backends:

### Redis Backend (Default)
```yaml
env:
  - name: CONFIG_STORAGE_TYPE
    value: "redis"
  - name: REDIS_URL
    value: "redis://redis-master:6379/1"
```

### File Backend
```yaml
env:
  - name: CONFIG_STORAGE_TYPE
    value: "file"
  - name: FILE_STORAGE_PATH
    value: "/app/configs"
persistence:
  enabled: true
  size: 5Gi
```

### Memory Backend (Development Only)
```yaml
env:
  - name: CONFIG_STORAGE_TYPE
    value: "memory"
```

## Configuration Features

### Environment Support
The service supports multiple environments:
- development
- staging  
- production

### Encryption
Sensitive configuration values are automatically encrypted using the provided encryption key.

### Versioning
Configuration changes are versioned with configurable retention:
```yaml
env:
  - name: VERSIONING_ENABLED
    value: "true"
  - name: MAX_VERSIONS
    value: "10"
```

### Hot Reload
Configuration changes can be automatically detected and reloaded:
```yaml
env:
  - name: HOT_RELOAD_ENABLED
    value: "true"
  - name: RELOAD_CHECK_INTERVAL
    value: "30"
```

## Upgrading

To upgrade the Config Service deployment:

```bash
helm upgrade config-service ./config-service
```

## Troubleshooting

### Common Issues

1. **Pod not starting**
   ```bash
   kubectl describe pod -l app.kubernetes.io/name=config-service
   kubectl logs -l app.kubernetes.io/name=config-service
   ```

2. **Storage issues**
   ```bash
   kubectl get pvc
   kubectl describe pvc config-service-storage
   ```

3. **Redis connection issues**
   ```bash
   kubectl run redis-client --image=redis:7 -it --rm --restart=Never -- redis-cli -h redis-master ping
   ```

### Health Checks

```bash
# Check if the service is healthy
kubectl port-forward svc/config-service 8000:8000
curl http://127.0.0.1:8000/health

# Check metrics
curl http://127.0.0.1:8000/metrics

# Test configuration API
curl http://127.0.0.1:8000/api/v1/configs
```

## Values File Examples

### Development Environment

```yaml
# values-dev.yaml
replicaCount: 1
autoscaling:
  enabled: false
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
  - name: DEFAULT_ENVIRONMENT
    value: "development"
persistence:
  enabled: false
```

### Production Environment

```yaml
# values-prod.yaml
replicaCount: 3
autoscaling:
  enabled: true
  minReplicas: 3
  maxReplicas: 10
persistence:
  enabled: true
  size: 20Gi
  storageClass: fast-ssd
serviceMonitor:
  enabled: true
networkPolicy:
  enabled: true
env:
  - name: DEFAULT_ENVIRONMENT
    value: "production"
  - name: VERSIONING_ENABLED
    value: "true"
  - name: AUDIT_LOGGING_ENABLED
    value: "true"
```

## API Usage Examples

### Create Configuration
```bash
curl -X POST http://config-service:8000/api/v1/configs \
  -H "Content-Type: application/json" \
  -d '{
    "key": "database.url",
    "value": "postgresql://user:pass@host:5432/db",
    "environment": "production",
    "encrypted": true
  }'
```

### Get Configuration
```bash
curl http://config-service:8000/api/v1/configs/database.url?environment=production
```

### Update Configuration
```bash
curl -X PUT http://config-service:8000/api/v1/configs/database.url \
  -H "Content-Type: application/json" \
  -d '{
    "value": "postgresql://user:newpass@host:5432/db",
    "environment": "production"
  }'
```

### List Configurations
```bash
curl http://config-service:8000/api/v1/configs?environment=production
```

