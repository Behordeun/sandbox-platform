#!/bin/zsh

# Deployment
mv deployment/docker-compose/* ../dpi_sandbox/deployment/docker-compose/
mv deployment/helmfile/* ../dpi_sandbox/deployment/helmfile/
mv deployment/scripts/* ../dpi_sandbox/deployment/scripts/
mv deployment/monitoring ../dpi_sandbox/deployment/
mv deployment/README.md ../dpi_sandbox/deployment/

# Services
mv services/api-gateway ../dpi_sandbox/services/
mv services/auth-service ../dpi_sandbox/services/
mv services/config-service ../dpi_sandbox/services/
mv services/sms ../dpi_sandbox/services/

# Service subfolders (move all relevant files)
for service in api-gateway auth-service config-service sms; do
  mv services/$service/.env ../dpi_sandbox/services/$service/
  mv services/$service/.env.example ../dpi_sandbox/services/$service/
  mv services/$service/Dockerfile ../dpi_sandbox/services/$service/
  mv services/$service/README.md ../dpi_sandbox/services/$service/
  mv services/$service/app ../dpi_sandbox/services/$service/
  mv services/$service/helm ../dpi_sandbox/services/$service/
  mv services/$service/requirements.txt ../dpi_sandbox/services/$service/
  mv services/$service/tests ../dpi_sandbox/services/$service/
  # Add other folders/files as needed
done

# .github (CI/CD, instructions, workflows)
mv .github ../dpi_sandbox/

# Docs
mv docs ../dpi_sandbox/

# Root files
mv README.md ../dpi_sandbox/
mv .env.example ../dpi_sandbox/
mv .env ../dpi_sandbox/
mv LICENSE ../dpi_sandbox/
mv .gitignore ../dpi_sandbox/
mv start-dev.sh ../dpi_sandbox/

# Config (centralized config)
# If you have global config files, move them here
# mv <config_files> ../dpi_sandbox/config/

# If you have Postgres/Mongo configs, move them to sandbox/datastores
# mv <postgres_files> ../dpi_sandbox/sandbox/datastores/postgres/
# mv <mongo_files> ../dpi_sandbox/sandbox/datastores/mongo/

# Remove .DS_Store and other unnecessary files
rm -f ../dpi_sandbox/.DS_Store

echo "Migration complete. Please review the new structure in ../dpi_sandbox."
