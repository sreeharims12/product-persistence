import os
import sys

# Add current directory to python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import engine, Base
from app.models import User, MonitoringRequest, ProductSnapshot, PriceHistory, Notification

def clean_database():
    print("Dropping all tables to clean up schema...")
    # Drop all tables and custom enums cascade
    Base.metadata.drop_all(bind=engine)
    with engine.connect() as conn:
        # Direct SQL to ensure custom type is dropped in Postgres
        try:
            conn.execute("DROP TYPE IF EXISTS notificationchannel CASCADE;")
            conn.execute("DROP TYPE IF EXISTS notificationtype CASCADE;")
            conn.execute("DROP TYPE IF EXISTS notificationstatus CASCADE;")
        except Exception:
            pass
    
    print("Re-creating all tables with updated schema...")
    Base.metadata.create_all(bind=engine)
    print("Database cleaned and reset successfully ✓")

if __name__ == "__main__":
    clean_database()
