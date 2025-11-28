from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    # Recreate users from non-role defaults (avoiding the processing issue)
    print("Updating existing enum values in users table...")
    # Don't process the enum, just update the raw values
    db.execute(text("""
        UPDATE users SET role = 'NORMAL'::userrole 
        WHERE role IS NOT NULL
    """))
    
    # Now recreate the enum with uppercase values
    print("Dropping users role column...")
    db.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS role"))
    
    print("Dropping userrole enum type...")
    db.execute(text("DROP TYPE IF EXISTS userrole CASCADE"))
    
    print("Creating userrole enum type with UPPERCASE values...")
    db.execute(text("CREATE TYPE userrole AS ENUM ('ADMIN', 'VIP', 'NORMAL')"))
    
    print("Adding role column with UPPERCASE enum...")
    db.execute(text("ALTER TABLE users ADD COLUMN role userrole DEFAULT 'NORMAL'::userrole NOT NULL"))
    
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
