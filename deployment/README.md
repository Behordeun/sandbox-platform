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

## 📊 Monitoring

- **Prometheus**: Metrics collection
- **Grafana**: Visualization dashboards
- **Health checks**: Service monitoring

---

**Production-ready deployment configurations** 🚀