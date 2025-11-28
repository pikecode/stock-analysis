from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    result = db.execute(text(
        "SELECT column_name, data_type FROM information_schema.columns "
        "WHERE table_name='users' ORDER BY ordinal_position"
    ))
    
    print("Users table columns:")
    for row in result:
        print(f"  - {row[0]}: {row[1]}")
        
finally:
    db.close()
