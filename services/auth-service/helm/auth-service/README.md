# Auth Service Helm Chart

This Helm chart deploys the Sandbox Auth Service, a FastAPI-based authentication and authorization service with OAuth2 support and NIN/BVN verification capabilities.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.2.0+
- PostgreSQL (can be deployed as a dependency)

## Installing the Chart

To install the chart with the release name `auth-service`:

```bash
helm install auth-service ./auth-service
```

The command deploys the auth service on the Kubernetes cluster with the default configuration. The [Parameters](#parameters) section lists the parameters that can be configured during installation.

## Uninstalling the Chart

To uninstall/delete the `auth-service` deployment:

```bash
helm delete auth-service
```

## Parameters

### Global parameters

| Name                      | Description                                     | Value |
| ------------------------- | ----------------------------------------------- | ----- |
| `nameOverride`            | String to partially override auth-service.fullname | `""` |
| `fullnameOverride`        | String to fully override auth-service.fullname | `""` |

### Image parameters

| Name                | Description                                        | Value                                    |
| ------------------- | -------------------------------------------------- | ---------------------------------------- |
| `image.repository`  | Auth service image repository                      | `your-dockerhub-username/sandbox-auth-service` |
| `image.tag`         | Auth service image tag (immutable tags are recommended) | `1.0.0` |
| `image.pullPolicy`  | Auth service image pull policy                     | `IfNotPresent` |

### Deployment parameters

| Name                                    | Description                                               | Value   |
| --------------------------------------- | --------------------------------------------------------- | ------- |
| `replicaCount`                          | Number of auth service replicas to deploy                | `1`     |
| `resources.limits.cpu`                  | The CPU limit for the auth service containers            | `500m`  |
| `resources.limits.memory`               | The memory limit for the auth service containers         | `512Mi` |
| `resources.requests.cpu`                | The requested CPU for the auth service containers        | `250m`  |
| `resources.requests.memory`             | The requested memory for the auth service containers     | `256Mi` |

### Service parameters

| Name                  | Description                                          | Value       |
| --------------------- | ---------------------------------------------------- | ----------- |
| `service.type`        | Auth service service type                            | `ClusterIP` |
| `service.port`        | Auth service service HTTP port                       | `80`        |
| `service.targetPort`  | Auth service container HTTP port                     | `8000`      |

### Ingress parameters

| Name                  | Description                                          | Value                    |
| --------------------- | ---------------------------------------------------- | ------------------------ |
| `ingress.enabled`     | Enable ingress record generation for auth service   | `false`                  |
| `ingress.hosts[0].host` | Default host for the ingress record               | `auth.sandbox.local`     |

### Application configuration

| Name                                    | Description                                    | Value                                |
| --------------------------------------- | ---------------------------------------------- | ------------------------------------ |
| `config.appName`                        | Application name                               | `"Sandbox Auth Service"`             |
| `config.debug`                          | Enable debug mode                             | `false`                              |
| `config.jwtAccessTokenExpireMinutes`    | JWT access token expiration in minutes        | `30`                                 |
| `config.oauth2IssuerUrl`                | OAuth2 issuer URL                             | `"http://auth.sandbox.local"`        |

### Database parameters

| Name                            | Description                                    | Value                                                              |
| ------------------------------- | ---------------------------------------------- | ------------------------------------------------------------------ |
| `postgresql.enabled`            | Switch to enable or disable PostgreSQL helm chart | `true`                                                        |
| `postgresql.auth.username`      | Name for a custom user to create              | `sandbox_user`                                                     |
| `postgresql.auth.password`      | Password for the custom user to create        | `changeme`                                                         |
| `postgresql.auth.database`      | Name for a custom database to create          | `sandbox_auth`                                                     |

### Secrets

| Name                      | Description                                    | Value                                      |
| ------------------------- | ---------------------------------------------- | ------------------------------------------ |
| `secrets.jwtSecretKey`    | JWT secret key for token signing              | `"your-secret-key-change-in-production"`   |
| `secrets.dojaApiKey`      | Doja API key for NIN/BVN verification         | `""`                                       |

## Configuration and installation details

### External database

To use an external database instead of the included PostgreSQL:

1. Set `postgresql.enabled` to `false`
2. Set `secrets.databaseUrl` to your external database URL

### NIN/BVN Verification

To enable NIN/BVN verification:

1. Obtain an API key from Doja (https://dojah.io)
2. Set `secrets.dojaApiKey` to your API key

### Ingress

To enable ingress:

1. Set `ingress.enabled` to `true`
2. Configure `ingress.hosts` with your domain
3. Optionally configure TLS with `ingress.tls`

### Monitoring

To enable Prometheus monitoring:

1. Set `monitoring.enabled` to `true`
2. Set `monitoring.serviceMonitor.enabled` to `true`
3. Ensure Prometheus Operator is installed in your cluster

## Examples

### Basic installation with external access

```bash
helm install auth-service ./auth-service \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=auth.yourdomain.com \
  --set secrets.jwtSecretKey="your-secure-jwt-secret"
```

### Production installation with external database

```bash
helm install auth-service ./auth-service \
  --set postgresql.enabled=false \
  --set secrets.databaseUrl="postgresql://user:pass@db.example.com:5432/authdb" \
  --set secrets.jwtSecretKey="your-secure-jwt-secret" \
  --set secrets.dojaApiKey="your-dojah-api-key" \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=auth.yourdomain.com \
  --set ingress.tls[0].secretName=auth-tls \
  --set ingress.tls[0].hosts[0]=auth.yourdomain.com
```

