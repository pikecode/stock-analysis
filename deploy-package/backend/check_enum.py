from app.core.database import SessionLocal
from sqlalchemy import text

db = SessionLocal()
try:
    result = db.execute(text(
        "SELECT enum_range(NULL::userrole) as enum_values"
    ))
    
    for row in result:
        print(f"userrole ENUM values: {row[0]}")
        
finally:
    db.close()
