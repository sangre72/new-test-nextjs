"""
Create Default Tenant Script
Run this script to create the first tenant for testing authentication

Usage:
    python create_tenant.py
"""
from app.db.session import SessionLocal
from app.models.shared import Tenant, TenantStatusEnum


def create_default_tenant():
    """Create default tenant if it doesn't exist"""
    db = SessionLocal()
    try:
        # Check if tenant already exists
        existing = db.query(Tenant).filter(
            Tenant.tenant_code == "default"
        ).first()

        if existing:
            print(f"✅ Default tenant already exists (ID: {existing.id})")
            return existing

        # Create new tenant
        tenant = Tenant(
            tenant_code="default",
            tenant_name="Default Tenant",
            description="Default tenant for testing",
            status=TenantStatusEnum.ACTIVE,
            admin_email="admin@example.com",
            admin_name="Admin",
            created_by="system"
        )

        db.add(tenant)
        db.commit()
        db.refresh(tenant)

        print(f"✅ Default tenant created successfully!")
        print(f"   - ID: {tenant.id}")
        print(f"   - Code: {tenant.tenant_code}")
        print(f"   - Name: {tenant.tenant_name}")

        return tenant

    except Exception as e:
        db.rollback()
        print(f"❌ Error creating tenant: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    create_default_tenant()
