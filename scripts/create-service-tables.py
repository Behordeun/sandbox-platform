#!/usr/bin/env python3
"""
Create basic tables for all sandbox services
"""

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "",
)


def create_service_tables():
    """Create basic tables for all sandbox services."""
    if not DATABASE_URL:
        print("❌ DATABASE_URL is not set. Add it to .env or export it.")
        return
    engine = create_engine(DATABASE_URL)

    # SQL to create basic tables for each service
    table_specs = [
        (
            "NIN",
            """
            CREATE TABLE IF NOT EXISTS nin_verifications (
                id SERIAL PRIMARY KEY,
                nin VARCHAR(11) NOT NULL,
                nin_hash VARCHAR(255) NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                verification_data JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                is_deleted BOOLEAN DEFAULT FALSE,
                deleted_at TIMESTAMP WITH TIME ZONE
            );
            CREATE INDEX IF NOT EXISTS idx_nin_verifications_nin_hash ON nin_verifications(nin_hash);
            CREATE INDEX IF NOT EXISTS idx_nin_verifications_status ON nin_verifications(status);
            """,
        ),
        (
            "BVN",
            """
            CREATE TABLE IF NOT EXISTS bvn_verifications (
                id SERIAL PRIMARY KEY,
                bvn VARCHAR(11) NOT NULL,
                bvn_hash VARCHAR(255) NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                verification_data JSONB,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                is_deleted BOOLEAN DEFAULT FALSE,
                deleted_at TIMESTAMP WITH TIME ZONE
            );
            CREATE INDEX IF NOT EXISTS idx_bvn_verifications_bvn_hash ON bvn_verifications(bvn_hash);
            CREATE INDEX IF NOT EXISTS idx_bvn_verifications_status ON bvn_verifications(status);
            """,
        ),
        (
            "SMS",
            """
            CREATE TABLE IF NOT EXISTS sms_messages (
                id SERIAL PRIMARY KEY,
                to_number VARCHAR(20) NOT NULL,
                from_number VARCHAR(20),
                message TEXT NOT NULL,
                status VARCHAR(50) DEFAULT 'pending',
                message_id VARCHAR(255),
                provider_response JSONB,
                sent_at TIMESTAMP WITH TIME ZONE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                is_deleted BOOLEAN DEFAULT FALSE,
                deleted_at TIMESTAMP WITH TIME ZONE
            );
            CREATE INDEX IF NOT EXISTS idx_sms_messages_to_number ON sms_messages(to_number);
            CREATE INDEX IF NOT EXISTS idx_sms_messages_status ON sms_messages(status);
            CREATE INDEX IF NOT EXISTS idx_sms_messages_message_id ON sms_messages(message_id);
            """,
        ),
        (
            "AI",
            """
            CREATE TABLE IF NOT EXISTS ai_conversations (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(255) NOT NULL,
                user_message TEXT NOT NULL,
                ai_response TEXT NOT NULL,
                model VARCHAR(100),
                tokens_used INTEGER,
                response_time_ms INTEGER,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                is_deleted BOOLEAN DEFAULT FALSE,
                deleted_at TIMESTAMP WITH TIME ZONE
            );
            CREATE INDEX IF NOT EXISTS idx_ai_conversations_session_id ON ai_conversations(session_id);
            CREATE INDEX IF NOT EXISTS idx_ai_conversations_created_at ON ai_conversations(created_at);
            """,
        ),
        (
            "Config",
            """
            CREATE TABLE IF NOT EXISTS config_settings (
                id SERIAL PRIMARY KEY,
                key VARCHAR(255) NOT NULL UNIQUE,
                value JSONB NOT NULL,
                description TEXT,
                is_encrypted BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                is_deleted BOOLEAN DEFAULT FALSE,
                deleted_at TIMESTAMP WITH TIME ZONE
            );
            CREATE INDEX IF NOT EXISTS idx_config_settings_key ON config_settings(key);
            """,
        ),
        (
            "Gateway Core",
            """
            CREATE TABLE IF NOT EXISTS gateway_requests (
                id SERIAL PRIMARY KEY,
                method VARCHAR(10) NOT NULL,
                path VARCHAR(500) NOT NULL,
                status_code INTEGER NOT NULL,
                response_time_ms INTEGER,
                user_agent TEXT,
                client_ip VARCHAR(45),
                service_name VARCHAR(100),
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                is_deleted BOOLEAN DEFAULT FALSE,
                deleted_at TIMESTAMP WITH TIME ZONE
            );
            CREATE INDEX IF NOT EXISTS idx_gateway_requests_created_at ON gateway_requests(created_at);
            CREATE INDEX IF NOT EXISTS idx_gateway_requests_service_name ON gateway_requests(service_name);
            CREATE INDEX IF NOT EXISTS idx_gateway_requests_status_code ON gateway_requests(status_code);
            """,
        ),
        (
            "Gateway Access Logs",
            """
            CREATE TABLE IF NOT EXISTS gateway_access_logs (
                id SERIAL PRIMARY KEY,
                request_id VARCHAR(64),
                user_id VARCHAR(64),
                auth_method VARCHAR(50),
                service_name VARCHAR(100),
                method VARCHAR(10) NOT NULL,
                path VARCHAR(500) NOT NULL,
                status_code INTEGER NOT NULL,
                duration_ms INTEGER,
                client_ip VARCHAR(45),
                user_agent TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                is_deleted BOOLEAN DEFAULT FALSE,
                deleted_at TIMESTAMP WITH TIME ZONE
            );
            CREATE INDEX IF NOT EXISTS idx_gateway_access_logs_created_at ON gateway_access_logs(created_at);
            CREATE INDEX IF NOT EXISTS idx_gateway_access_logs_service ON gateway_access_logs(service_name);
            CREATE INDEX IF NOT EXISTS idx_gateway_access_logs_status ON gateway_access_logs(status_code);
            CREATE INDEX IF NOT EXISTS idx_gateway_access_logs_request_id ON gateway_access_logs(request_id);
            -- Forensics fields
            ALTER TABLE gateway_access_logs ADD COLUMN IF NOT EXISTS req_size INTEGER;
            ALTER TABLE gateway_access_logs ADD COLUMN IF NOT EXISTS res_size INTEGER;
            """,
        ),
        (
            "Auth Audit Logs",
            """
            CREATE TABLE IF NOT EXISTS auth_audit_logs (
                id SERIAL PRIMARY KEY,
                request_id VARCHAR(64),
                user_id INTEGER,
                activity_type VARCHAR(100),
                success BOOLEAN,
                method VARCHAR(10) NOT NULL,
                path VARCHAR(500) NOT NULL,
                status_code INTEGER NOT NULL,
                client_ip VARCHAR(45),
                user_agent TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                is_deleted BOOLEAN DEFAULT FALSE,
                deleted_at TIMESTAMP WITH TIME ZONE
            );
            CREATE INDEX IF NOT EXISTS idx_auth_audit_logs_created_at ON auth_audit_logs(created_at);
            CREATE INDEX IF NOT EXISTS idx_auth_audit_logs_user_id ON auth_audit_logs(user_id);
            CREATE INDEX IF NOT EXISTS idx_auth_audit_logs_activity ON auth_audit_logs(activity_type);
            """,
        ),
        (
            "NIN Access Logs",
            """
            CREATE TABLE IF NOT EXISTS nin_access_logs (
                id SERIAL PRIMARY KEY,
                request_id VARCHAR(64),
                user_id VARCHAR(64),
                method VARCHAR(10) NOT NULL,
                path VARCHAR(500) NOT NULL,
                status_code INTEGER NOT NULL,
                duration_ms INTEGER,
                client_ip VARCHAR(45),
                user_agent TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                is_deleted BOOLEAN DEFAULT FALSE,
                deleted_at TIMESTAMP WITH TIME ZONE
            );
            CREATE INDEX IF NOT EXISTS idx_nin_access_logs_created_at ON nin_access_logs(created_at);
            CREATE INDEX IF NOT EXISTS idx_nin_access_logs_status ON nin_access_logs(status_code);
            CREATE INDEX IF NOT EXISTS idx_nin_access_logs_request_id ON nin_access_logs(request_id);
            ALTER TABLE nin_access_logs ADD COLUMN IF NOT EXISTS req_size INTEGER;
            ALTER TABLE nin_access_logs ADD COLUMN IF NOT EXISTS res_size INTEGER;
            """,
        ),
        (
            "BVN Access Logs",
            """
            CREATE TABLE IF NOT EXISTS bvn_access_logs (
                id SERIAL PRIMARY KEY,
                request_id VARCHAR(64),
                user_id VARCHAR(64),
                method VARCHAR(10) NOT NULL,
                path VARCHAR(500) NOT NULL,
                status_code INTEGER NOT NULL,
                duration_ms INTEGER,
                client_ip VARCHAR(45),
                user_agent TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                is_deleted BOOLEAN DEFAULT FALSE,
                deleted_at TIMESTAMP WITH TIME ZONE
            );
            CREATE INDEX IF NOT EXISTS idx_bvn_access_logs_created_at ON bvn_access_logs(created_at);
            CREATE INDEX IF NOT EXISTS idx_bvn_access_logs_status ON bvn_access_logs(status_code);
            CREATE INDEX IF NOT EXISTS idx_bvn_access_logs_request_id ON bvn_access_logs(request_id);
            ALTER TABLE bvn_access_logs ADD COLUMN IF NOT EXISTS req_size INTEGER;
            ALTER TABLE bvn_access_logs ADD COLUMN IF NOT EXISTS res_size INTEGER;
            """,
        ),
        (
            "SMS Access Logs",
            """
            CREATE TABLE IF NOT EXISTS sms_access_logs (
                id SERIAL PRIMARY KEY,
                request_id VARCHAR(64),
                user_id VARCHAR(64),
                method VARCHAR(10) NOT NULL,
                path VARCHAR(500) NOT NULL,
                status_code INTEGER NOT NULL,
                duration_ms INTEGER,
                client_ip VARCHAR(45),
                user_agent TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                is_deleted BOOLEAN DEFAULT FALSE,
                deleted_at TIMESTAMP WITH TIME ZONE
            );
            CREATE INDEX IF NOT EXISTS idx_sms_access_logs_created_at ON sms_access_logs(created_at);
            CREATE INDEX IF NOT EXISTS idx_sms_access_logs_status ON sms_access_logs(status_code);
            CREATE INDEX IF NOT EXISTS idx_sms_access_logs_request_id ON sms_access_logs(request_id);
            ALTER TABLE sms_access_logs ADD COLUMN IF NOT EXISTS req_size INTEGER;
            ALTER TABLE sms_access_logs ADD COLUMN IF NOT EXISTS res_size INTEGER;
            """,
        ),
        (
            "AI Access Logs",
            """
            CREATE TABLE IF NOT EXISTS ai_access_logs (
                id SERIAL PRIMARY KEY,
                request_id VARCHAR(64),
                user_id VARCHAR(64),
                method VARCHAR(10) NOT NULL,
                path VARCHAR(500) NOT NULL,
                status_code INTEGER NOT NULL,
                duration_ms INTEGER,
                client_ip VARCHAR(45),
                user_agent TEXT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                is_deleted BOOLEAN DEFAULT FALSE,
                deleted_at TIMESTAMP WITH TIME ZONE
            );
            CREATE INDEX IF NOT EXISTS idx_ai_access_logs_created_at ON ai_access_logs(created_at);
            CREATE INDEX IF NOT EXISTS idx_ai_access_logs_status ON ai_access_logs(status_code);
            CREATE INDEX IF NOT EXISTS idx_ai_access_logs_request_id ON ai_access_logs(request_id);
            ALTER TABLE ai_access_logs ADD COLUMN IF NOT EXISTS req_size INTEGER;
            ALTER TABLE ai_access_logs ADD COLUMN IF NOT EXISTS res_size INTEGER;
            """,
        ),
    ]

    print("🗄️  Creating service tables...")

    with engine.connect() as conn:
        for label, sql in table_specs:
            try:
                conn.execute(text(sql))
                conn.commit()
                print(f"✅ {label} tables created")
            except Exception as e:
                print(f"❌ Error creating tables for {label}: {e}")

    # Create/replace helpful SQL views for analytics
    views = [
        (
            "Gateway Access Summary",
            """
            CREATE OR REPLACE VIEW v_gateway_access_summary AS
            SELECT
              date_trunc('hour', created_at) AS bucket,
              service_name,
              COUNT(*) AS total,
              SUM(CASE WHEN status_code BETWEEN 200 AND 299 THEN 1 ELSE 0 END) AS ok,
              SUM(CASE WHEN status_code BETWEEN 400 AND 499 THEN 1 ELSE 0 END) AS client_err,
              SUM(CASE WHEN status_code BETWEEN 500 AND 599 THEN 1 ELSE 0 END) AS server_err,
              AVG(duration_ms) AS avg_ms
            FROM gateway_access_logs
            GROUP BY 1,2
            ORDER BY 1 DESC, 2;
            """,
        ),
        (
            "Gateway Latency Percentiles",
            """
            CREATE OR REPLACE VIEW v_gateway_latency_pcts AS
            SELECT
              date_trunc('hour', created_at) AS bucket,
              service_name,
              percentile_cont(0.50) WITHIN GROUP (ORDER BY duration_ms) AS p50_ms,
              percentile_cont(0.95) WITHIN GROUP (ORDER BY duration_ms) AS p95_ms,
              percentile_cont(0.99) WITHIN GROUP (ORDER BY duration_ms) AS p99_ms
            FROM gateway_access_logs
            GROUP BY 1,2
            ORDER BY 1 DESC, 2;
            """,
        ),
        (
            "Gateway Top Endpoints",
            """
            CREATE OR REPLACE VIEW v_gateway_top_endpoints AS
            SELECT
              path,
              service_name,
              COUNT(*) AS hits,
              AVG(duration_ms) AS avg_ms,
              SUM(CASE WHEN status_code >= 500 THEN 1 ELSE 0 END) AS errors
            FROM gateway_access_logs
            WHERE created_at > now() - interval '7 days'
            GROUP BY 1,2
            ORDER BY hits DESC;
            """,
        ),
        (
            "Auth Audit Summary",
            """
            CREATE OR REPLACE VIEW v_auth_audit_summary AS
            SELECT
              date_trunc('hour', created_at) AS bucket,
              activity_type,
              COUNT(*) AS total,
              SUM(CASE WHEN success THEN 1 ELSE 0 END) AS success_count,
              SUM(CASE WHEN success THEN 0 ELSE 1 END) AS failure_count
            FROM auth_audit_logs
            GROUP BY 1,2
            ORDER BY 1 DESC, 2;
            """,
        ),
        (
            "Service Access Summary",
            """
            CREATE OR REPLACE VIEW v_service_access_summary AS
            SELECT * FROM (
              SELECT 'nin' AS service, created_at, status_code, duration_ms FROM nin_access_logs
              UNION ALL
              SELECT 'bvn' AS service, created_at, status_code, duration_ms FROM bvn_access_logs
              UNION ALL
              SELECT 'sms' AS service, created_at, status_code, duration_ms FROM sms_access_logs
              UNION ALL
              SELECT 'ai'  AS service, created_at, status_code, duration_ms FROM ai_access_logs
            ) t;
            """,
        ),
        (
            "Service Error Rate",
            """
            CREATE OR REPLACE VIEW v_service_error_rate AS
            SELECT
              date_trunc('hour', created_at) AS bucket,
              service,
              COUNT(*) AS total,
              SUM(CASE WHEN status_code >= 500 THEN 1 ELSE 0 END) AS server_err,
              ROUND(100.0 * SUM(CASE WHEN status_code >= 500 THEN 1 ELSE 0 END) / NULLIF(COUNT(*),0), 2) AS server_err_pct
            FROM v_service_access_summary
            GROUP BY 1,2
            ORDER BY 1 DESC, 2;
            """,
        ),
        (
            "Service Latency Summary",
            """
            CREATE OR REPLACE VIEW v_service_latency_summary AS
            SELECT
              date_trunc('hour', created_at) AS bucket,
              service,
              AVG(duration_ms) AS avg_ms,
              MAX(duration_ms) AS p100_ms
            FROM v_service_access_summary
            GROUP BY 1,2
            ORDER BY 1 DESC, 2;
            """,
        ),
        (
            "Service Latency Percentiles",
            """
            CREATE OR REPLACE VIEW v_service_latency_pcts AS
            SELECT
              date_trunc('hour', created_at) AS bucket,
              service,
              percentile_cont(0.50) WITHIN GROUP (ORDER BY duration_ms) AS p50_ms,
              percentile_cont(0.95) WITHIN GROUP (ORDER BY duration_ms) AS p95_ms,
              percentile_cont(0.99) WITHIN GROUP (ORDER BY duration_ms) AS p99_ms
            FROM v_service_access_summary
            GROUP BY 1,2
            ORDER BY 1 DESC, 2;
            """,
        ),
    ]

    with engine.connect() as conn:
        for label, sql in views:
            try:
                conn.execute(text(sql))
                conn.commit()
                print(f"✅ View created/updated: {label}")
            except Exception as e:
                print(f"❌ Error creating view {label}: {e}")

    # Optionally seed a read-only role for analytics/Grafana
    ro_user = os.getenv("GRAFANA_RO_USER") or os.getenv("READONLY_DB_USER")
    ro_pass = os.getenv("GRAFANA_RO_PASSWORD") or os.getenv("READONLY_DB_PASSWORD")
    if ro_user and ro_pass:
        with engine.connect() as conn:
            try:
                # Create role if not exists
                exists = conn.execute(
                    text("SELECT 1 FROM pg_roles WHERE rolname=:u"), {"u": ro_user}
                ).scalar()
                if not exists:
                    conn.execute(
                        text(f'CREATE ROLE "{ro_user}" LOGIN PASSWORD :p'),
                        {"p": ro_pass},
                    )
                # Grant permissions
                conn.execute(text(f'GRANT USAGE ON SCHEMA public TO "{ro_user}"'))
                conn.execute(
                    text(f'GRANT SELECT ON ALL TABLES IN SCHEMA public TO "{ro_user}"')
                )
                conn.execute(
                    text(
                        f'GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO "{ro_user}"'
                    )
                )
                # Ensure future tables/sequences are granted
                conn.execute(
                    text(
                        f'ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO "{ro_user}"'
                    )
                )
                conn.execute(
                    text(
                        f'ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON SEQUENCES TO "{ro_user}"'
                    )
                )
                conn.commit()
                print(f"✅ Read-only role ensured: {ro_user}")
            except Exception as e:
                print(f"⚠️  Could not ensure read-only role '{ro_user}': {e}")

    # Verify tables were created
    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name NOT LIKE 'alembic%'
            ORDER BY table_name
        """
            )
        )
        tables = [row[0] for row in result]

        print(f"\n📊 Total tables created: {len(tables)}")
        for table in tables:
            print(f"  ✅ {table}")


if __name__ == "__main__":
    create_service_tables()
    print("\n🎉 All service tables created successfully!")
