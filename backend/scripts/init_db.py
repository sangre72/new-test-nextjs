#!/usr/bin/env python
"""
Database initialization script
Run migrations and seed initial data
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.db.session import engine, SessionLocal
from app.db.base import Base
from app.db.init_seed import init_db


def main():
    """Initialize database"""
    print("Starting database initialization...")

    try:
        # Create all tables
        print("Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("✓ Tables created successfully")

        # Seed initial data
        print("Seeding initial data...")
        db = SessionLocal()
        try:
            init_db(db)
            print("✓ Initial data seeded successfully")
        finally:
            db.close()

        print("\nDatabase initialization complete!")
        print("\nDefault credentials:")
        print("  - Username: superadmin")
        print("  - Password: superadmin123")
        print("  - Email: superadmin@localhost.com")

    except Exception as e:
        print(f"✗ Error during initialization: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
