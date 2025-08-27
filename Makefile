# DPI Sandbox Platform Makefile
# Nigerian Digital Public Infrastructure Sandbox

.PHONY: help setup dev test build deploy clean logs health

# Default target
.DEFAULT_GOAL := help

# Variables
REGISTRY ?= your-registry
TAG ?= latest
ENV ?= development

# Colors for output
RED := \033[31m
GREEN := \033[32m
YELLOW := \033[33m
BLUE := \033[34m
RESET := \033[0m

help: ## Show this help message
	@echo "$(BLUE)DPI Sandbox Platform - Nigerian Digital Public Infrastructure$(RESET)"
	@echo ""
	@echo "$(GREEN)Available commands:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-20s$(RESET) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# =============================================================================
# SETUP & INITIALIZATION
# =============================================================================

setup: ## Complete platform setup (database, admin user, dependencies)
	@echo "$(GREEN)Setting up DPI Sandbox Platform...$(RESET)"
	@cp .env.template .env || echo ".env already exists"
	@chmod +x scripts/*.sh
	@./scripts/setup-db.sh
	@./scripts/create-admin-user.py
	@echo "$(GREEN)✅ Platform setup complete!$(RESET)"

init-env: ## Initialize environment file from template
	@echo "$(YELLOW)Initializing environment configuration...$(RESET)"
	@cp .env.template .env
	@echo "$(GREEN)✅ Please edit .env with your actual values$(RESET)"

install-deps: ## Install Python dependencies for all services
	@echo "$(YELLOW)Installing dependencies...$(RESET)"
	@cd services/auth-service && pip install -r requirements.txt
	@cd services/api-gateway && pip install -r requirements.txt
	@cd config && pip install -r requirements.txt
	@echo "$(GREEN)✅ Dependencies installed$(RESET)"

# =============================================================================
# DEVELOPMENT
# =============================================================================

dev: ## Start development environment
	@echo "$(GREEN)Starting development environment...$(RESET)"
	@./scripts/start-sandbox.sh
	@echo "$(GREEN)✅ Development environment running$(RESET)"

dev-stop: ## Stop development environment
	@echo "$(YELLOW)Stopping development environment...$(RESET)"
	@./scripts/stop-sandbox.sh
	@echo "$(GREEN)✅ Development environment stopped$(RESET)"

dev-restart: dev-stop dev ## Restart development environment

dev-logs: ## Show development logs
	@echo "$(BLUE)Showing development logs...$(RESET)"
	@tail -f services/logs/*.log sandbox/logs/*.log

# =============================================================================
# TESTING
# =============================================================================

test: ## Run all tests
	@echo "$(YELLOW)Running tests...$(RESET)"
	@./scripts/test-dpi-apis.sh
	@echo "$(GREEN)✅ Tests completed$(RESET)"

test-unit: ## Run unit tests
	@echo "$(YELLOW)Running unit tests...$(RESET)"
	@cd services/auth-service && python -m pytest tests/ -v
	@cd services/api-gateway && python -m pytest tests/ -v
	@echo "$(GREEN)✅ Unit tests completed$(RESET)"

test-integration: ## Run integration tests
	@echo "$(YELLOW)Running integration tests...$(RESET)"
	@./scripts/test-dpi-apis.sh
	@echo "$(GREEN)✅ Integration tests completed$(RESET)"

mock-data: ## Generate Nigerian test data
	@echo "$(YELLOW)Generating mock data...$(RESET)"
	@./scripts/mock-data.py
	@echo "$(GREEN)✅ Mock data generated$(RESET)"

# =============================================================================
# HEALTH & MONITORING
# =============================================================================

health: ## Check all services health
	@echo "$(BLUE)Checking services health...$(RESET)"
	@./scripts/check-services.sh

logs: ## Show all service logs
	@echo "$(BLUE)Showing service logs...$(RESET)"
	@tail -f services/logs/user_activity.log

logs-security: ## Show security logs
	@echo "$(BLUE)Showing security logs...$(RESET)"
	@tail -f services/logs/security_events.log

analyze-logs: ## Analyze user activity and usage
	@echo "$(BLUE)Analyzing logs...$(RESET)"
	@./scripts/analyze-logs.py --all

analyze-logs-security: ## Analyze security events in logs
	@echo "$(BLUE)Analyzing security events...$(RESET)"
	@./scripts/analyze-logs.py --security

analyze-logs-performance: ## Analyze API performance from logs
	@echo "$(BLUE)Analyzing API performance...$(RESET)"
	@./scripts/analyze-logs.py --performance

# =============================================================================
# DOCKER & CONTAINERIZATION
# =============================================================================

build: ## Build all Docker images
	@echo "$(YELLOW)Building Docker images...$(RESET)"
	@./deployment/scripts/build-images.sh -r $(REGISTRY) -t $(TAG)
	@echo "$(GREEN)✅ Images built successfully$(RESET)"

push: ## Push Docker images to registry
	@echo "$(YELLOW)Pushing images to registry...$(RESET)"
	@./deployment/scripts/push-images.sh -r $(REGISTRY) -t $(TAG)
	@echo "$(GREEN)✅ Images pushed successfully$(RESET)"

docker-dev: ## Start with Docker Compose (development)
	@echo "$(GREEN)Starting Docker development environment...$(RESET)"
	@docker-compose -f deployment/docker-compose/docker-compose.dev.yml up -d
	@echo "$(GREEN)✅ Docker development environment running$(RESET)"

docker-stop: ## Stop Docker containers
	@echo "$(YELLOW)Stopping Docker containers...$(RESET)"
	@docker-compose -f deployment/docker-compose/docker-compose.dev.yml down
	@echo "$(GREEN)✅ Docker containers stopped$(RESET)"

# =============================================================================
# KUBERNETES DEPLOYMENT
# =============================================================================

deploy-dev: ## Deploy to development environment
	@echo "$(GREEN)Deploying to development...$(RESET)"
	@cd deployment/helmfile && helmfile -e dev apply
	@echo "$(GREEN)✅ Deployed to development$(RESET)"

deploy-staging: ## Deploy to staging environment
	@echo "$(GREEN)Deploying to staging...$(RESET)"
	@cd deployment/helmfile && helmfile -e staging apply
	@echo "$(GREEN)✅ Deployed to staging$(RESET)"

deploy-prod: ## Deploy to production environment
	@echo "$(RED)Deploying to production...$(RESET)"
	@read -p "Are you sure you want to deploy to production? [y/N] " confirm && [ "$$confirm" = "y" ]
	@cd deployment/helmfile && helmfile -e prod apply
	@echo "$(GREEN)✅ Deployed to production$(RESET)"

k8s-status: ## Check Kubernetes deployment status
	@echo "$(BLUE)Checking Kubernetes status...$(RESET)"
	@kubectl get pods -n sandbox-$(ENV)
	@kubectl get services -n sandbox-$(ENV)

k8s-logs: ## Show Kubernetes logs
	@echo "$(BLUE)Showing Kubernetes logs...$(RESET)"
	@kubectl logs -f deployment/auth-service -n sandbox-$(ENV)

# =============================================================================
# DATABASE OPERATIONS
# =============================================================================

db-setup: ## Setup database and run migrations
	@echo "$(YELLOW)Setting up database...$(RESET)"
	@./scripts/setup-db.sh
	@echo "$(GREEN)✅ Database setup complete$(RESET)"

db-migrate: ## Run database migrations
	@echo "$(YELLOW)Running database migrations...$(RESET)"
	@./scripts/migrate-db.py
	@echo "$(GREEN)✅ Database migrations complete$(RESET)"

db-reset: ## Reset database (WARNING: Destructive)
	@echo "$(RED)Resetting database...$(RESET)"
	@read -p "This will delete all data. Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ]
	@./scripts/setup-db.sh --reset
	@echo "$(GREEN)✅ Database reset complete$(RESET)"

# =============================================================================
# USER MANAGEMENT
# =============================================================================

create-admin: ## Create admin user
	@echo "$(YELLOW)Creating admin user...$(RESET)"
	@./scripts/create-admin-user.py
	@echo "$(GREEN)✅ Admin user created$(RESET)"

create-user: ## Create startup user (interactive)
	@echo "$(YELLOW)Creating startup user...$(RESET)"
	@./scripts/create-admin-user.py --interactive
	@echo "$(GREEN)✅ Startup user created$(RESET)"

# =============================================================================
# MAINTENANCE & CLEANUP
# =============================================================================

clean: ## Clean up temporary files and containers
	@echo "$(YELLOW)Cleaning up...$(RESET)"
	@docker system prune -f
	@find . -type f -name "*.pyc" -delete
	@find . -type d -name "__pycache__" -delete
	@rm -rf .pytest_cache
	@echo "$(GREEN)✅ Cleanup complete$(RESET)"

# =============================================================================
# LOG MANAGEMENT & ROTATION
# =============================================================================

rotate-logs: ## Rotate and compress log files
	@echo "$(YELLOW)Rotating log files...$(RESET)"
	@python scripts/log-rotation-manager.py --rotate
	@echo "$(GREEN)✅ Log rotation complete$(RESET)"

rotate-logs-force: ## Force rotate all log files
	@echo "$(YELLOW)Force rotating all log files...$(RESET)"
	@python scripts/log-rotation-manager.py --rotate --force
	@echo "$(GREEN)✅ Force rotation complete$(RESET)"

log-stats: ## Show log statistics and usage
	@echo "$(BLUE)Log Statistics:$(RESET)"
	@python scripts/log-rotation-manager.py --stats

log-cleanup: ## Clean up old archived logs (1 year retention)
	@echo "$(YELLOW)Cleaning up old archived logs...$(RESET)"
	@python scripts/log-rotation-manager.py --cleanup 365
	@echo "$(GREEN)✅ Log cleanup complete$(RESET)"

log-cleanup-aggressive: ## Aggressive cleanup (6 months retention)
	@echo "$(RED)Aggressive log cleanup (6 months retention)...$(RESET)"
	@read -p "This will delete logs older than 6 months. Continue? [y/N] " confirm && [ "$$confirm" = "y" ]
	@python scripts/log-rotation-manager.py --cleanup 180
	@echo "$(GREEN)✅ Aggressive cleanup complete$(RESET)"

clean-logs: ## Clean current log files (WARNING: Destructive)
	@echo "$(RED)Cleaning current log files...$(RESET)"
	@read -p "This will delete current logs. Continue? [y/N] " confirm && [ "$$confirm" = "y" ]
	@rm -f services/logs/*.log
	@rm -f sandbox/logs/*.log
	@echo "$(GREEN)✅ Current log files cleaned$(RESET)"

backup: ## Backup database and configuration
	@echo "$(YELLOW)Creating backup...$(RESET)"
	@mkdir -p backups
	@pg_dump $(DATABASE_URL) > backups/backup_$(shell date +%Y%m%d_%H%M%S).sql
	@cp .env backups/env_$(shell date +%Y%m%d_%H%M%S).backup
	@echo "$(GREEN)✅ Backup created$(RESET)"

# =============================================================================
# SECURITY & COMPLIANCE
# =============================================================================

security-scan: ## Run security scans
	@echo "$(YELLOW)Running security scans...$(RESET)"
	@bandit -r services/ sandbox/ -f json -o security_report.json || true
	@safety check --json --output safety_report.json || true
	@echo "$(GREEN)✅ Security scan complete$(RESET)"

lint: ## Run code linting
	@echo "$(YELLOW)Running linters...$(RESET)"
	@flake8 services/ sandbox/ --max-line-length=88
	@black --check services/ sandbox/
	@echo "$(GREEN)✅ Linting complete$(RESET)"

format: ## Format code
	@echo "$(YELLOW)Formatting code...$(RESET)"
	@black services/ sandbox/
	@isort services/ sandbox/
	@echo "$(GREEN)✅ Code formatted$(RESET)"

# =============================================================================
# DOCUMENTATION
# =============================================================================

docs: ## Generate API documentation
	@echo "$(YELLOW)Generating documentation...$(RESET)"
	@echo "API Documentation available at:"
	@echo "  Auth Service: http://localhost:8000/docs"
	@echo "  API Gateway: http://localhost:8080/docs"
	@echo "  Config Service: http://localhost:8001/docs"

api-docs: ## Open API documentation in browser
	@echo "$(BLUE)Opening API documentation...$(RESET)"
	@open http://localhost:8080/docs

# =============================================================================
# QUICK COMMANDS
# =============================================================================

quick-start: setup dev ## Quick start: setup and run development environment

quick-test: mock-data test ## Quick test: generate data and run tests

quick-deploy: build push deploy-dev ## Quick deploy: build, push, and deploy to dev

status: health k8s-status ## Show overall system status

# =============================================================================
# ENVIRONMENT SPECIFIC
# =============================================================================

prod-check: ## Pre-production checklist
	@echo "$(BLUE)Running pre-production checks...$(RESET)"
	@echo "✓ Checking environment variables..."
	@test -f .env || (echo "$(RED)❌ .env file missing$(RESET)" && exit 1)
	@echo "✓ Checking database connection..."
	@./scripts/check-services.sh
	@echo "✓ Running security scan..."
	@make security-scan
	@echo "$(GREEN)✅ Pre-production checks complete$(RESET)"

# =============================================================================
# MONITORING
# =============================================================================

metrics: ## Show system metrics
	@echo "$(BLUE)System Metrics:$(RESET)"
	@echo "Prometheus: http://localhost:9090"
	@echo "Grafana: http://localhost:3001"
	@echo "Service Health: http://localhost:8080/health"