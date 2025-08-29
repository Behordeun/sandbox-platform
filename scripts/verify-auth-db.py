#!/usr/bin/env python3
"""
Verify Auth DB Tables & FKs

Reads DATABASE_URL from .env/env and prints:
- Presence of auth_* tables
- Row counts per table
- Presence of key foreign keys
- Optional check for admin users
"""

import os
import sys
from pathlib import Path


def load_env():
    try:
        from dotenv import load_dotenv  # type: ignore

        root = Path(__file__).resolve().parent.parent
        env_path = root / ".env"
        if env_path.exists():
            load_dotenv(env_path.as_posix())
    except Exception:
        pass


def main():
    load_env()
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("❌ DATABASE_URL is not set. Add it to .env or export it.")
        sys.exit(1)

    from sqlalchemy import create_engine, text
    from sqlalchemy.engine import reflection

    engine = create_engine(db_url)
    insp = reflection.Inspector.from_engine(engine)

    # Expected tables (auth_ prefix)
    tables = {
        "auth_users": ["id"],
        "auth_oauth_clients": ["client_id"],
        "auth_oauth_tokens": ["id"],
        "auth_token_blacklist": ["id"],
        "auth_password_reset_tokens": ["id"],
    }

    print("\n📋 Tables present & row counts:")
    existing = set(insp.get_table_names())
    with engine.connect() as conn:
        for tbl, keys in tables.items():
            if tbl in existing:
                cnt = conn.execute(text(f'SELECT COUNT(*) FROM "{tbl}"')).scalar()
                print(f"  • {tbl}: {cnt}")
            else:
                print(f"  • {tbl}: MISSING")

        # Check FKs
        print("\n🔗 Foreign keys:")
        def list_fks(tname: str):
            if tname not in existing:
                return []
            return insp.get_foreign_keys(tname)

        tb_fks = list_fks("auth_token_blacklist")
        pr_fks = list_fks("auth_password_reset_tokens")

        def has_fk(fks, col, ref_table, ref_col):
            for fk in fks:
                if fk.get("constrained_columns") == [col] and fk.get("referred_table") == ref_table and fk.get("referred_columns") == [ref_col]:
                    return True
            return False

        tblacklist_ok = has_fk(tb_fks, "user_id", "auth_users", "id") if tb_fks else False
        preset_ok = has_fk(pr_fks, "user_id", "auth_users", "id") if pr_fks else False

        print(f"  • auth_token_blacklist.user_id → auth_users.id: {'OK' if tblacklist_ok else 'MISSING'}")
        print(f"  • auth_password_reset_tokens.user_id → auth_users.id: {'OK' if preset_ok else 'MISSING or N/A'}")

        # Optional: check for admin user by email
        admin_email = os.getenv("ADMIN_EMAIL", "admin@dpi-sandbox.ng")
        if "auth_users" in existing:
            res = conn.execute(text('SELECT id, email, username FROM "auth_users" WHERE email = :e'), {"e": admin_email}).fetchone()
            if res:
                print(f"\n✅ Admin user found: id={res.id}, email={res.email}, username={res.username}")
            else:
                print(f"\nℹ️  Admin user not found for email {admin_email}. You can run ./scripts/create-admin-user.py")


if __name__ == "__main__":
    main()

