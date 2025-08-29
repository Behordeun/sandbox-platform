# Grafana Dashboards (Importable JSON)

This folder contains starter Grafana dashboard JSON files for the Sandbox Platform.

- gateway_access.json — shows recent gateway access logs with filters by service, status code, and request_id.
- auth_audit.json — shows auth audit events with filters by user_id, activity_type, and success.

Usage
- Create a PostgreSQL data source in Grafana pointing at the same DATABASE_URL.
- Import the JSON dashboards.
- If needed, update the data source UID in the JSON or select the correct data source after import.

Notes
- These dashboards assume public schema.
- For large datasets, add retention policies and rollups as needed.
