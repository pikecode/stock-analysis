from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    print("Dropping role column...")
    db.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS role"))
    
    print("Dropping userrole enum type...")
    db.execute(text("DROP TYPE IF EXISTS userrole CASCADE"))
    
    print("Creating userrole enum type with correct values...")
    db.execute(text("CREATE TYPE userrole AS ENUM ('admin', 'vip', 'normal')"))
    
    print("Adding role column with correct ENUM type...")
    db.execute(text("ALTER TABLE users ADD COLUMN role userrole DEFAULT 'normal' NOT NULL"))
    
    db.commit()
    print("✅ Fixed successfully!")
    
    # Verify
    result = db.execute(text("SELECT enum_range(NULL::userrole)"))
    for row in result:
        print(f"userrole ENUM values: {row[0]}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
