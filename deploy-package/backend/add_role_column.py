from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    print("Adding role column...")
    db.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'normal' NOT NULL"))
    db.commit()
    print("✅ Column added successfully!")
    
    # Verify
    result = db.execute(text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name='users' AND column_name='role'"
    ))
    if result.fetchone():
        print("✅ Verified: role column exists!")
    else:
        print("❌ Error: column still not found!")
except Exception as e:
    print(f"Error: {e}")
    db.rollback()
finally:
    db.close()
