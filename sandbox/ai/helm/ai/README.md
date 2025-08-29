# AI Service Helm Chart

Deploys the AI service.

## Values

- image.repository: Docker image (default: docker.io/your-org/sandbox-ai-service)
- image.tag: Image tag (default: 1.0.0)
- global.imageRegistry: Optional global registry prefix (e.g., docker.io/your-org)
- secrets.databaseUrl: PostgreSQL URL (REQUIRED)
- secrets.aiApiKey: Service API key (optional)
- ingress.enabled: Expose via Ingress (default: false)
- ingress.className: IngressClass (e.g., nginx)
- ingress.clusterIssuer: cert-manager ClusterIssuer (optional)
- networkPolicy.enabled: Enable NetworkPolicy (default: false)
- networkPolicy.gatewayOnly: Allow only API Gateway to reach this service (default: true)

## Quickstart

```
helm install ai ./sandbox/ai/helm/ai   --set secrets.databaseUrl="postgresql://user:pass@postgres:5432/db" \
  --set secrets.aiApiKey="YOUR_AI_KEY"
```

Enable Ingress with TLS:

```
--set ingress.enabled=true --set ingress.className=nginx --set ingress.clusterIssuer=letsencrypt-prod --set ingress.hosts[0].host=ai.example.com
```

Use a global registry prefix:

```
--set global.imageRegistry=docker.io/your-org
```
