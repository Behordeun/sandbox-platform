# SMS Service Helm Chart

Deploys the SMS service.

## Values

- image.repository: Docker image (default: docker.io/your-org/sandbox-sms-service)
- image.tag: Image tag (default: 1.0.0)
- global.imageRegistry: Optional global registry prefix (e.g., docker.io/your-org)
- secrets.databaseUrl: PostgreSQL URL (REQUIRED)
- secrets.smsApiKey: Service API key (optional)
- ingress.enabled: Expose via Ingress (default: false)
- ingress.className: IngressClass (e.g., nginx)
- ingress.clusterIssuer: cert-manager ClusterIssuer (optional)
- networkPolicy.enabled: Enable NetworkPolicy (default: false)
- networkPolicy.gatewayOnly: Allow only API Gateway to reach this service (default: true)

## Quickstart

```
helm install sms ./sandbox/sms/helm/sms   --set secrets.databaseUrl="postgresql://user:pass@postgres:5432/db" \
  --set secrets.smsApiKey="YOUR_SMS_KEY"
```

Enable Ingress with TLS:

```
--set ingress.enabled=true --set ingress.className=nginx --set ingress.clusterIssuer=letsencrypt-prod --set ingress.hosts[0].host=sms.example.com
```

Use a global registry prefix:

```
--set global.imageRegistry=docker.io/your-org
```
