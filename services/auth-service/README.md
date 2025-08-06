# Sandbox Auth Service

A FastAPI-based authentication and authorization service designed for the Sandbox Platform. This service provides OAuth2 authentication, JWT token management, and Nigerian identity verification (NIN/BVN) capabilities.

## Features

- **OAuth2 Authentication**: Full OAuth2 authorization code flow implementation
- **JWT Token Management**: Access and refresh token generation and validation
- **Nigerian Identity Verification**: NIN and BVN verification via Doja API
- **User Management**: User registration, authentication, and profile management
- **Modular Architecture**: Clean separation of concerns with CRUD operations
- **Docker Support**: Containerized deployment with Docker Hub integration
- **Kubernetes Ready**: Helm charts for easy Kubernetes deployment
- **Health Checks**: Built-in health monitoring endpoints
- **CORS Support**: Cross-origin resource sharing for web applications

## Quick Start

### Local Development

1. **Clone and setup**:
   ```bash
   cd auth-service
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the service**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Access the API**:
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health
   - OpenID Configuration: http://localhost:8000/.well-known/openid_configuration

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
- `POST /api/v1/auth/register` - User registration
- `POST /api/v1/auth/login` - User login (OAuth2 compatible)
- `POST /api/v1/auth/login/json` - User login (JSON payload)
- `GET /api/v1/auth/userinfo` - Get user information
- `GET /api/v1/auth/me` - Get current user

### OAuth2
- `GET /api/v1/oauth2/authorize` - OAuth2 authorization endpoint
- `POST /api/v1/oauth2/token` - OAuth2 token endpoint
- `POST /api/v1/oauth2/clients` - Create OAuth2 client
- `GET /api/v1/oauth2/clients/{client_id}` - Get OAuth2 client

### Identity Verification
- `POST /api/v1/identity/verify-nin-bvn` - Verify NIN/BVN
- `GET /api/v1/identity/verification-status` - Get verification status

### System
- `GET /health` - Health check
- `GET /.well-known/openid_configuration` - OpenID Connect discovery
- `GET /.well-known/jwks.json` - JSON Web Key Set

## Configuration

The service uses environment variables for configuration. See `.env.example` for all available options.

### Key Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `JWT_SECRET_KEY` | Secret key for JWT signing | Required |
| `DOJA_API_KEY` | Doja API key for NIN/BVN verification | Optional |
| `CORS_ORIGINS` | Allowed CORS origins | `["*"]` |
| `DEBUG` | Enable debug mode | `false` |

## Database Schema

The service uses PostgreSQL with the following main tables:

- **users**: User accounts and profile information
- **oauth_clients**: OAuth2 client applications
- **oauth_tokens**: OAuth2 tokens and authorization codes

Database migrations are handled by Alembic (setup in `alembic/` directory).

## Security Features

- **Password Hashing**: Bcrypt for secure password storage
- **JWT Tokens**: Signed tokens with configurable expiration
- **Identity Verification**: NIN/BVN hashing for privacy
- **CORS Protection**: Configurable cross-origin policies
- **Input Validation**: Pydantic models for request validation

## Development

### Project Structure

```
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

## Integration

### OAuth2 Flow

1. **Client Registration**: Create OAuth2 client via API
2. **Authorization**: Redirect user to `/oauth2/authorize`
3. **Token Exchange**: Exchange authorization code for tokens
4. **API Access**: Use access token for authenticated requests

### NIN/BVN Verification

1. **User Registration**: Create user account
2. **Identity Verification**: Submit NIN/BVN for verification
3. **Verification Status**: Check verification status
4. **Enhanced Access**: Verified users get additional privileges

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

