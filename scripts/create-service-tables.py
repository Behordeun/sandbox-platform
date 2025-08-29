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
    "postgresql://postgres:MUhammad__1234@127.0.0.1:5432/sandbox_platform",
)


def create_service_tables():
    """Create basic tables for all sandbox services."""
    engine = create_engine(DATABASE_URL)

    # SQL to create basic tables for each service
    sql_commands = [
        # NIN Service Tables
        """
        CREATE TABLE IF NOT EXISTS nin_verifications (
            id SERIAL PRIMARY KEY,
            nin VARCHAR(11) NOT NULL,
            nin_hash VARCHAR(255) NOT NULL,
            status VARCHAR(50) DEFAULT 'pending',
            verification_data JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_nin_verifications_nin_hash ON nin_verifications(nin_hash);
        CREATE INDEX IF NOT EXISTS idx_nin_verifications_status ON nin_verifications(status);
        """,
        # BVN Service Tables
        """
        CREATE TABLE IF NOT EXISTS bvn_verifications (
            id SERIAL PRIMARY KEY,
            bvn VARCHAR(11) NOT NULL,
            bvn_hash VARCHAR(255) NOT NULL,
            status VARCHAR(50) DEFAULT 'pending',
            verification_data JSONB,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_bvn_verifications_bvn_hash ON bvn_verifications(bvn_hash);
        CREATE INDEX IF NOT EXISTS idx_bvn_verifications_status ON bvn_verifications(status);
        """,
        # SMS Service Tables
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
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_sms_messages_to_number ON sms_messages(to_number);
        CREATE INDEX IF NOT EXISTS idx_sms_messages_status ON sms_messages(status);
        CREATE INDEX IF NOT EXISTS idx_sms_messages_message_id ON sms_messages(message_id);
        """,
        # AI Service Tables
        """
        CREATE TABLE IF NOT EXISTS ai_conversations (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(255) NOT NULL,
            user_message TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            model VARCHAR(100),
            tokens_used INTEGER,
            response_time_ms INTEGER,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_ai_conversations_session_id ON ai_conversations(session_id);
        CREATE INDEX IF NOT EXISTS idx_ai_conversations_created_at ON ai_conversations(created_at);
        """,
        # Config Service Tables
        """
        CREATE TABLE IF NOT EXISTS config_settings (
            id SERIAL PRIMARY KEY,
            key VARCHAR(255) NOT NULL UNIQUE,
            value JSONB NOT NULL,
            description TEXT,
            is_encrypted BOOLEAN DEFAULT FALSE,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_config_settings_key ON config_settings(key);
        """,
        # API Gateway Tables (for metrics and logs)
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
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_gateway_requests_created_at ON gateway_requests(created_at);
        CREATE INDEX IF NOT EXISTS idx_gateway_requests_service_name ON gateway_requests(service_name);
        CREATE INDEX IF NOT EXISTS idx_gateway_requests_status_code ON gateway_requests(status_code);
        """,
    ]

    print("🗄️  Creating service tables...")

    with engine.connect() as conn:
        for i, sql in enumerate(sql_commands, 1):
            try:
                conn.execute(text(sql))
                conn.commit()
                service_names = ["NIN", "BVN", "SMS", "AI", "Config", "API Gateway"]
                print(f"✅ {service_names[i-1]} service tables created")
            except Exception as e:
                print(f"❌ Error creating tables for service {i}: {e}")

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
