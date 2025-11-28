#!/usr/bin/env python
"""Migrate from multiple roles to single role enum."""
import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Get database URL from environment
DATABASE_URL = "sqlite:///./data.db"

def migrate():
    """Perform the migration."""
    engine = create_engine(DATABASE_URL, echo=True)

    with engine.begin() as conn:
        # 1. Check if users table has role column, if not add it
        result = conn.execute(text("""
            PRAGMA table_info(users)
        """)).fetchall()

        column_names = [col[1] for col in result]

        if 'role' not in column_names:
            print("Adding 'role' column to users table...")
            conn.execute(text("""
                ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'normal' NOT NULL
            """))
            print("✅ 'role' column added")
        else:
            print("ℹ️  'role' column already exists")

        # 2. Migrate data from user_roles to users.role
        print("\nMigrating data from roles to single role field...")

        # Get all users with their roles
        users = conn.execute(text("""
            SELECT u.id, u.username, GROUP_CONCAT(r.name) as roles
            FROM users u
            LEFT JOIN user_roles ur ON u.id = ur.user_id
            LEFT JOIN roles r ON ur.role_id = r.id
            GROUP BY u.id
        """)).fetchall()

        for user_id, username, roles_str in users:
            if roles_str:
                roles_list = roles_str.split(',')
                # Determine the role: admin > vip > normal
                if 'admin' in roles_list:
                    new_role = 'admin'
                elif 'vip' in roles_list or 'customer' in roles_list:
                    new_role = 'vip'
                else:
                    new_role = 'normal'

                print(f"  User {username}: {roles_str} → {new_role}")

                conn.execute(text("""
                    UPDATE users SET role = :role WHERE id = :user_id
                """), {"role": new_role, "user_id": user_id})
            else:
                print(f"  User {username}: (no roles) → normal")
                conn.execute(text("""
                    UPDATE users SET role = :role WHERE id = :user_id
                """), {"role": "normal", "user_id": user_id})

        print("✅ Data migration completed")

        # 3. Optional: Drop old tables (commented out for safety)
        # print("\nDropping old tables...")
        # conn.execute(text("DROP TABLE IF EXISTS user_roles"))
        # conn.execute(text("DROP TABLE IF EXISTS role_permissions"))
        # conn.execute(text("DROP TABLE IF EXISTS roles"))
        # conn.execute(text("DROP TABLE IF EXISTS permissions"))
        # print("✅ Old tables dropped")

        print("\n✅ Migration completed successfully!")
        print("\nNext steps:")
        print("1. Restart the backend server")
        print("2. Test the login functionality")
        print("3. Verify user management works with the new role system")

if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)
