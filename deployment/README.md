# 🚀 Deployment Guide

**Docker and Kubernetes deployment configurations.**

## 📁 Structure

```
deployment/
├── docker-compose/
│   └── docker-compose.dev.yml    # Development environment
├── helmfile/
│   └── helmfile.yaml             # Kubernetes deployment
├── scripts/
│   ├── build-images.sh           # Build Docker images
│   └── push-images.sh            # Push to registry
└── monitoring/
    └── prometheus.yml            # Monitoring configuration
```

## 🐳 Docker Development

```bash
# Start development environment
docker-compose -f deployment/docker-compose/docker-compose.dev.yml up -d

# Build all images
./deployment/scripts/build-images.sh

# Push to registry
./deployment/scripts/push-images.sh -r your-registry/
```

## ☸️ Kubernetes Deployment

```bash
# Deploy with Helmfile
cd deployment/helmfile
helmfile -e dev apply
```

### Service Charts Quickstart

Each service has a Helm chart under `sandbox/<service>/helm/<service>` that uses Secrets for DATABASE_URL and service API keys. Example (NIN):

```
helm install nin ./sandbox/nin/helm/nin   --set secrets.databaseUrl="postgresql://user:pass@postgres:5432/sandbox_platform"   --set secrets.dojahApiKey="YOUR_DOJAH_KEY"   --set global.imageRegistry=docker.io/your-org
```

- Enable Ingress with TLS (cert‑manager):

```
--set ingress.enabled=true --set ingress.className=nginx --set ingress.clusterIssuer=letsencrypt-prod --set ingress.hosts[0].host=nin.example.com
```

- NetworkPolicy (default gatewayOnly):

```
--set networkPolicy.enabled=true
```

Repeat for BVN (`secrets.dojahApiKey`), SMS (`secrets.smsApiKey`), and AI (`secrets.aiApiKey`).


## 📊 Monitoring

- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **Health checks**: Service monitoring

---

**Production-ready deployment configurations** 🚀