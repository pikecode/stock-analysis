from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    print("Fixing role column...")
    # Drop the wrong column
    db.execute(text("ALTER TABLE users DROP COLUMN role"))
    print("Dropped old role column")
    
    # Add correct column with ENUM type
    db.execute(text("ALTER TABLE users ADD COLUMN role userrole DEFAULT 'normal'::userrole NOT NULL"))
    print("Added role column with correct ENUM type")
    
    db.commit()
    print("✅ Fixed successfully!")
    
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()
