"""
Migration script to add role column to users table
"""
from app.core.database import SessionLocal
from sqlalchemy import text

def migrate():
    db = SessionLocal()
    try:
        # Check if role column exists
        result = db.execute(text(
            "SELECT column_name FROM information_schema.columns "
            "WHERE table_name='users' AND column_name='role'"
        ))
        
        if result.fetchone():
            print("Role column already exists, skipping...")
            return
        
        # Add role column
        print("Adding role column to users table...")
        db.execute(text(
            "ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'normal' NOT NULL"
        ))
        
        # Create the enum type if it doesn't exist
        print("Creating userrole enum type...")
        try:
            db.execute(text(
                "CREATE TYPE userrole AS ENUM ('admin', 'vip', 'normal')"
            ))
        except:
            print("Enum type already exists, continuing...")
        
        db.commit()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
