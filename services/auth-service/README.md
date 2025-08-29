# Sandbox Auth Service

A FastAPI-based authentication and authorization service for the Sandbox Platform. This service provides secure JWT token management, OAuth2 authentication, and user management with advanced security features.

## Features

- **Nigerian Phone Validation**: Automatic validation and formatting of +234 numbers
- **Dynamic JWT Tokens**: Cryptographically secure tokens with unique identifiers (JTI)
- **Token Blacklist System**: Token revocation and logout capabilities
- **Password Reset**: Secure token-based password reset functionality
- **Enhanced Security**: Audience/issuer validation, comprehensive claim checking
- **Flexible Authentication**: Login with email or username
- **OAuth2 Support**: Full OAuth2 authorization code flow implementation
- **User Management**: Registration, authentication, and profile management
- **Rich User Activity Logging**: Comprehensive tracking of user interactions
- **Security Event Monitoring**: Real-time detection of authentication anomalies
- **Usage Analytics**: User engagement patterns and service usage metrics
- **Audit Logging**: Security event logging for compliance
- **Standardized Responses**: Consistent API responses with helpful error messages
- **SQLite Development**: Easy local development with SQLite database
- **Docker Support**: Containerized deployment ready
- **Kubernetes Ready**: Helm charts for production deployment

## Quick Start

### Local Development (via sandbox root recommended)

From the repository root, the sandbox scripts will set up the database, ensure tables exist, and start all services:

```bash
./scripts/start-sandbox.sh
```

Access the API:

   - API Documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - Health Check: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
   - OpenID Configuration: [http://127.0.0.1:8000/.well-known/openid_configuration](http://127.0.0.1:8000/.well-known/openid_configuration)

### Docker Deployment

1. **Build the image**:

```bash
docker build -t your-dockerhub-username/sandbox-auth-service:1.0.0 .
```

2. **Run with Docker**:

```bash
docker run -p 8000:8000 \
   -e DATABASE_URL="postgresql://user:pass@host:5432/db" \
   -e JWT_SECRET_KEY="your-secret-key" \
   your-dockerhub-username/sandbox-auth-service:1.0.0
```

### Kubernetes Deployment

1. **Install with Helm**:

```bash
cd helm/auth-service
helm install auth-service . \
   --set secrets.jwtSecretKey="your-secure-jwt-secret" \
   --set ingress.enabled=true \
   --set ingress.hosts[0].host=auth.yourdomain.com
```

## API Endpoints

### Authentication

- `POST /api/v1/auth/register` - User registration with Nigerian phone validation
- `POST /api/v1/auth/login` - OAuth2 compatible login (email/username)
- `POST /api/v1/auth/login/json` - JSON login (email/username)
- `GET /api/v1/auth/userinfo` - Get user information
- `GET /api/v1/auth/me` - Get current user
- `POST /api/v1/auth/logout` - Logout and blacklist token
- `POST /api/v1/auth/revoke-token` - Revoke specific token
- `POST /api/v1/auth/password-reset/request` - Request password reset
- `POST /api/v1/auth/password-reset/confirm` - Confirm password reset

### OAuth2

- `GET /api/v1/oauth2/authorize` - OAuth2 authorization endpoint
- `POST /api/v1/oauth2/token` - OAuth2 token endpoint
- `POST /api/v1/oauth2/clients` - Create OAuth2 client
- `GET /api/v1/oauth2/clients/{client_id}` - Get OAuth2 client

### System

- `GET /health` - Health check
- `GET /.well-known/openid_configuration` - OpenID Connect discovery
- `GET /.well-known/jwks.json` - JSON Web Key Set

## Configuration

The service uses environment variables for configuration. The authoritative file is the repository root `.env`.

### Key Configuration Options

| Variable | Description | Notes |
|----------|-------------|-------|
| `DATABASE_URL` | Database connection string | Required (PostgreSQL) |
| `JWT_SECRET_KEY` | Secret key for JWT signing | Required |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | Access token expiry | Default `30` if unset |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token expiry | Default `7` if unset |
| `OAUTH2_ISSUER_URL` | OAuth2 issuer URL | Default `http://127.0.0.1:8000` |
| `CORS_ORIGINS` | Allowed CORS origins | JSON array or comma‑separated |
| `DEBUG` | Enable debug mode | Default `false` |

## Database Schema

The service uses SQLite for development (PostgreSQL for production) with the following main tables:

- **users**: User accounts and profile information
- **oauth_clients**: OAuth2 client applications
- **oauth_tokens**: OAuth2 tokens and authorization codes
- **token_blacklist**: Revoked/blacklisted tokens for security

Tables are created via Alembic migrations or the sandbox migration script.

### Table Naming

- Auth tables are prefixed: `auth_users`, `auth_oauth_clients`, `auth_oauth_tokens`.
- Related tables: `auth_token_blacklist`, `auth_password_reset_tokens`.

### Migrations

Run from repository root:

```bash
./scripts/migrate-db.py
```

This script loads `.env`, exports `MIGRATIONS=1`, and runs Alembic for auth-service. It also includes safe rename/data copy/cleanup for legacy unprefixed tables.

Verify schema:

```bash
python3 scripts/verify-auth-db.py
```

## Security Features

- **Dynamic JWT Tokens**: Unique token identifiers (JTI) with cryptographic security
- **Token Blacklist**: Revocation system for compromised or logged-out tokens
- **Enhanced Validation**: Audience/issuer claims, comprehensive token verification
- **Password Hashing**: Bcrypt for secure password storage
- **Flexible Authentication**: Login with email or username
- **CORS Protection**: Configurable cross-origin policies
- **Input Validation**: Pydantic models for request validation

## Development

### Project Structure

```plain text
app/
├── api/v1/           # API endpoints
├── core/             # Core utilities (config, security, database)
├── crud/             # Database operations
├── dependencies/     # FastAPI dependencies
├── models/           # SQLAlchemy models
├── schemas/          # Pydantic schemas
└── main.py          # FastAPI application
```

### Running Tests

```bash
pytest tests/
```

### Code Quality

```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

## Deployment

### Docker Hub

1. **Build and push**:

```bash
docker build -t your-dockerhub-username/sandbox-auth-service:1.0.0 .
docker push your-dockerhub-username/sandbox-auth-service:1.0.0
```

### Kubernetes

The service includes comprehensive Helm charts for Kubernetes deployment:

- **PostgreSQL**: Optional managed database
- **Ingress**: External access configuration
- **Secrets**: Secure credential management
- **Health Checks**: Liveness and readiness probes
- **Monitoring**: Prometheus ServiceMonitor support

See `helm/auth-service/README.md` for detailed deployment instructions.

## Monitoring & Analytics

### User Activity Tracking

```bash
# Analyze user authentication patterns
python ../../analyze-logs.py --user-activity

# Monitor security events
python ../../analyze-logs.py --security

# Real-time activity monitoring
tail -f ../logs/user_activity.log

# View security events
tail -f ../logs/security_events.log
```

### Log Categories & Audits

- **User Activities**: Registration, login, profile access, password resets
- **Security Events**: Failed logins, suspicious activities, token violations
- **OAuth2 Flows**: Authorization codes, token exchanges, client interactions
- **Identity Verification**: NIN/BVN verification attempts and results

Database persistence:

- Correlation header: `X-Request-ID` present in responses and logs
- Audit table: `auth_audit_logs` stores structured activity/security events

### Analytics Capabilities

- **User Engagement**: Track individual user activity patterns
- **Authentication Success Rates**: Monitor login success/failure ratios
- **Security Monitoring**: Detect brute force attacks and suspicious IPs
- **Service Usage**: Popular endpoints and peak usage times
- **Performance Metrics**: Response times and error rates

## Integration

### OAuth2 Flow

1. **Client Registration**: Create OAuth2 client via API
2. **Authorization**: Redirect user to `/oauth2/authorize`
3. **Token Exchange**: Exchange authorization code for tokens
4. **API Access**: Use access token for authenticated requests

### Authentication Flow

1. **User Registration**: Create account with email/username
2. **Login**: Authenticate with email or username + password
3. **Token Usage**: Use JWT access token for API requests
4. **Token Refresh**: Use refresh token to get new access tokens
5. **Logout**: Revoke tokens via blacklist system

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

- Create an issue in the repository
- Contact the Sandbox Platform team
- Check the API documentation at `/docs`
