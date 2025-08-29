# API Gateway Helm Chart

This Helm chart deploys the Sandbox Platform API Gateway service on a Kubernetes cluster.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.8+
- Redis instance (for rate limiting and caching)
- Auth Service and Config Service deployed

## Installing the Chart

To install the chart with the release name `api-gateway`:

```bash
helm install api-gateway ./api-gateway
```

## Uninstalling the Chart

To uninstall/delete the `api-gateway` deployment:

```bash
helm uninstall api-gateway
```

## Configuration

The following table lists the configurable parameters of the API Gateway chart and their default values.

### Image Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `image.repository` | API Gateway image repository | `sandbox-api-gateway` |
| `image.tag` | API Gateway image tag | `1.0.0` |
| `image.pullPolicy` | Image pull policy | `IfNotPresent` |

### Deployment Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `replicaCount` | Number of replicas | `3` |
| `nameOverride` | Override the name of the chart | `""` |
| `fullnameOverride` | Override the fullname of the chart | `""` |

### Service Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `service.type` | Kubernetes service type | `ClusterIP` |
| `service.port` | Service port | `8080` |
| `service.targetPort` | Container port | `8080` |

### Ingress Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `ingress.enabled` | Enable ingress | `false` |
| `ingress.className` | Ingress class name | `""` |
| `ingress.annotations` | Ingress annotations | `{}` |
| `ingress.hosts` | Ingress hosts configuration | `[{host: api-gateway.local, paths: [{path: /, pathType: Prefix}]}]` |
| `ingress.tls` | Ingress TLS configuration | `[]` |

### Resource Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `resources.limits.cpu` | CPU limit | `1000m` |
| `resources.limits.memory` | Memory limit | `1Gi` |
| `resources.requests.cpu` | CPU request | `500m` |
| `resources.requests.memory` | Memory request | `512Mi` |

### Autoscaling Configuration

| Parameter | Description | Default |
|-----------|-------------|---------|
| `autoscaling.enabled` | Enable horizontal pod autoscaler | `true` |
| `autoscaling.minReplicas` | Minimum number of replicas | `3` |
| `autoscaling.maxReplicas` | Maximum number of replicas | `10` |
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
| `secrets.jwtSecretKey` | JWT secret key | `your-jwt-secret-key-change-in-production` |
| `podSecurityContext.fsGroup` | Pod security context fsGroup | `2000` |
| `podSecurityContext.runAsNonRoot` | Run as non-root user | `true` |
| `podSecurityContext.runAsUser` | User ID to run as | `1000` |

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
helm install api-gateway ./api-gateway \
  --set image.repository=myregistry/sandbox-api-gateway \
  --set image.tag=v1.0.0
```

### Production Installation with Ingress

```bash
helm install api-gateway ./api-gateway \
  --set image.repository=myregistry/sandbox-api-gateway \
  --set image.tag=v1.0.0 \
  --set ingress.enabled=true \
  --set ingress.className=nginx \
  --set ingress.hosts[0].host=api.example.com \
  --set ingress.hosts[0].paths[0].path=/ \
  --set ingress.hosts[0].paths[0].pathType=Prefix \
  --set secrets.jwtSecretKey=my-secure-jwt-secret
```

### High Availability Setup

```bash
helm install api-gateway ./api-gateway \
  --set replicaCount=5 \
  --set autoscaling.enabled=true \
  --set autoscaling.minReplicas=5 \
  --set autoscaling.maxReplicas=20 \
  --set podDisruptionBudget.enabled=true \
  --set podDisruptionBudget.minAvailable=3
```

### With Monitoring

```bash
helm install api-gateway ./api-gateway \
  --set serviceMonitor.enabled=true \
  --set serviceMonitor.namespace=monitoring
```

## Dependencies

This chart requires the following services to be available:

1. **Redis** - For rate limiting and caching
   ```bash
   helm install redis bitnami/redis
   ```

2. **Auth Service** - For authentication
   ```bash
   helm install auth-service ../auth-service/helm/auth-service
   ```

3. **Config Service** - For configuration management
   ```bash
   helm install config-service ../config-service/helm/config-service
   ```

## Upgrading

To upgrade the API Gateway deployment:

```bash
helm upgrade api-gateway ./api-gateway
```

## Troubleshooting

### Common Issues

1. **Pod not starting**
   ```bash
   kubectl describe pod -l app.kubernetes.io/name=api-gateway
   kubectl logs -l app.kubernetes.io/name=api-gateway
   ```

2. **Service not accessible**
   ```bash
   kubectl get svc api-gateway
   kubectl describe svc api-gateway
   ```

3. **Ingress not working**
   ```bash
   kubectl get ingress
   kubectl describe ingress api-gateway
   ```

### Health Checks

```bash
# Check if the service is healthy
kubectl port-forward svc/api-gateway 8080:8080
curl http://127.0.0.1:8080/health

# Check metrics
curl http://127.0.0.1:8080/metrics
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
```

### Production Environment

```yaml
# values-prod.yaml
replicaCount: 5
autoscaling:
  enabled: true
  minReplicas: 5
  maxReplicas: 20
ingress:
  enabled: true
  className: nginx
  hosts:
    - host: api.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: api-tls
      hosts:
        - api.example.com
serviceMonitor:
  enabled: true
networkPolicy:
  enabled: true
```

