"""
Seed Menu Data
Create sample menu data for testing
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.shared import Menu, Tenant, User, MenuTypeEnum, MenuPermissionTypeEnum, MenuLinkTypeEnum
from app.core.security import get_password_hash


def create_sample_menus(db: Session, tenant_id: int, user_id: int, username: str):
    """Create sample menu structure"""

    print(f"\n🌲 Creating sample menus for tenant {tenant_id}...")

    # User Menus (Frontend)
    user_menus = [
        {
            "menu_name": "Home",
            "menu_code": "home",
            "menu_type": MenuTypeEnum.USER,
            "menu_url": "/",
            "menu_icon": "fa-home",
            "link_type": MenuLinkTypeEnum.INTERNAL,
            "permission_type": MenuPermissionTypeEnum.PUBLIC,
            "display_order": 1,
            "description": "Home page",
        },
        {
            "menu_name": "Products",
            "menu_code": "products",
            "menu_type": MenuTypeEnum.USER,
            "menu_url": "/products",
            "menu_icon": "fa-shopping-bag",
            "link_type": MenuLinkTypeEnum.INTERNAL,
            "permission_type": MenuPermissionTypeEnum.PUBLIC,
            "display_order": 2,
            "description": "Product catalog",
            "children": [
                {
                    "menu_name": "All Products",
                    "menu_code": "all-products",
                    "menu_url": "/products/all",
                    "display_order": 1,
                },
                {
                    "menu_name": "New Arrivals",
                    "menu_code": "new-arrivals",
                    "menu_url": "/products/new",
                    "display_order": 2,
                    "metadata": {"badge": "New"},
                },
                {
                    "menu_name": "Sale",
                    "menu_code": "sale",
                    "menu_url": "/products/sale",
                    "display_order": 3,
                    "metadata": {"badge": "Hot", "color": "red"},
                },
            ]
        },
        {
            "menu_name": "About",
            "menu_code": "about",
            "menu_type": MenuTypeEnum.USER,
            "menu_url": "/about",
            "menu_icon": "fa-info-circle",
            "link_type": MenuLinkTypeEnum.INTERNAL,
            "permission_type": MenuPermissionTypeEnum.PUBLIC,
            "display_order": 3,
            "description": "About us",
        },
        {
            "menu_name": "My Account",
            "menu_code": "my-account",
            "menu_type": MenuTypeEnum.USER,
            "menu_url": "/account",
            "menu_icon": "fa-user",
            "link_type": MenuLinkTypeEnum.INTERNAL,
            "permission_type": MenuPermissionTypeEnum.AUTHENTICATED,
            "display_order": 4,
            "description": "User account",
            "children": [
                {
                    "menu_name": "Profile",
                    "menu_code": "profile",
                    "menu_url": "/account/profile",
                    "display_order": 1,
                },
                {
                    "menu_name": "Orders",
                    "menu_code": "orders",
                    "menu_url": "/account/orders",
                    "display_order": 2,
                },
                {
                    "menu_name": "Wishlist",
                    "menu_code": "wishlist",
                    "menu_url": "/account/wishlist",
                    "display_order": 3,
                },
            ]
        },
    ]

    # Admin Menus (Backend)
    admin_menus = [
        {
            "menu_name": "Dashboard",
            "menu_code": "admin-dashboard",
            "menu_type": MenuTypeEnum.ADMIN,
            "menu_url": "/admin/dashboard",
            "menu_icon": "fa-dashboard",
            "link_type": MenuLinkTypeEnum.INTERNAL,
            "permission_type": MenuPermissionTypeEnum.ROLE_BASED,
            "display_order": 1,
            "description": "Admin dashboard",
        },
        {
            "menu_name": "Content",
            "menu_code": "admin-content",
            "menu_type": MenuTypeEnum.ADMIN,
            "menu_icon": "fa-file-text",
            "link_type": MenuLinkTypeEnum.NONE,
            "permission_type": MenuPermissionTypeEnum.ROLE_BASED,
            "display_order": 2,
            "description": "Content management",
            "children": [
                {
                    "menu_name": "Posts",
                    "menu_code": "admin-posts",
                    "menu_url": "/admin/posts",
                    "menu_icon": "fa-file",
                    "display_order": 1,
                },
                {
                    "menu_name": "Categories",
                    "menu_code": "admin-categories",
                    "menu_url": "/admin/categories",
                    "menu_icon": "fa-folder",
                    "display_order": 2,
                },
                {
                    "menu_name": "Tags",
                    "menu_code": "admin-tags",
                    "menu_url": "/admin/tags",
                    "menu_icon": "fa-tags",
                    "display_order": 3,
                },
            ]
        },
        {
            "menu_name": "Users",
            "menu_code": "admin-users",
            "menu_type": MenuTypeEnum.ADMIN,
            "menu_icon": "fa-users",
            "link_type": MenuLinkTypeEnum.NONE,
            "permission_type": MenuPermissionTypeEnum.ROLE_BASED,
            "display_order": 3,
            "description": "User management",
            "children": [
                {
                    "menu_name": "All Users",
                    "menu_code": "admin-all-users",
                    "menu_url": "/admin/users",
                    "display_order": 1,
                },
                {
                    "menu_name": "Roles",
                    "menu_code": "admin-roles",
                    "menu_url": "/admin/roles",
                    "display_order": 2,
                },
                {
                    "menu_name": "Permissions",
                    "menu_code": "admin-permissions",
                    "menu_url": "/admin/permissions",
                    "display_order": 3,
                },
            ]
        },
        {
            "menu_name": "Settings",
            "menu_code": "admin-settings",
            "menu_type": MenuTypeEnum.ADMIN,
            "menu_icon": "fa-cog",
            "link_type": MenuLinkTypeEnum.NONE,
            "permission_type": MenuPermissionTypeEnum.ROLE_BASED,
            "display_order": 4,
            "description": "System settings",
            "children": [
                {
                    "menu_name": "General",
                    "menu_code": "admin-settings-general",
                    "menu_url": "/admin/settings/general",
                    "display_order": 1,
                },
                {
                    "menu_name": "Menus",
                    "menu_code": "admin-settings-menus",
                    "menu_url": "/admin/settings/menus",
                    "display_order": 2,
                },
                {
                    "menu_name": "SEO",
                    "menu_code": "admin-settings-seo",
                    "menu_url": "/admin/settings/seo",
                    "display_order": 3,
                },
            ]
        },
    ]

    # Site Menus (Header/Footer utilities)
    site_menus = [
        {
            "menu_name": "Help",
            "menu_code": "help",
            "menu_type": MenuTypeEnum.SITE,
            "menu_url": "/help",
            "menu_icon": "fa-question-circle",
            "link_type": MenuLinkTypeEnum.INTERNAL,
            "permission_type": MenuPermissionTypeEnum.PUBLIC,
            "display_order": 1,
        },
        {
            "menu_name": "Contact",
            "menu_code": "contact",
            "menu_type": MenuTypeEnum.SITE,
            "menu_url": "/contact",
            "menu_icon": "fa-envelope",
            "link_type": MenuLinkTypeEnum.INTERNAL,
            "permission_type": MenuPermissionTypeEnum.PUBLIC,
            "display_order": 2,
        },
        {
            "menu_name": "Privacy",
            "menu_code": "privacy",
            "menu_type": MenuTypeEnum.SITE,
            "menu_url": "/privacy",
            "menu_icon": "fa-lock",
            "link_type": MenuLinkTypeEnum.INTERNAL,
            "permission_type": MenuPermissionTypeEnum.PUBLIC,
            "display_order": 3,
        },
    ]

    def create_menu_recursive(menu_data, parent_id=None, depth=0):
        """Recursively create menu and its children"""

        # Calculate path
        if parent_id:
            parent = db.query(Menu).filter(Menu.id == parent_id).first()
            parent_path = parent.path if parent else f"/{parent_id}"
        else:
            parent_path = ""

        # Create menu
        menu = Menu(
            tenant_id=tenant_id,
            parent_id=parent_id,
            menu_name=menu_data["menu_name"],
            menu_code=menu_data["menu_code"],
            menu_type=menu_data.get("menu_type", MenuTypeEnum.USER),
            menu_url=menu_data.get("menu_url"),
            menu_icon=menu_data.get("menu_icon"),
            link_type=menu_data.get("link_type", MenuLinkTypeEnum.INTERNAL),
            permission_type=menu_data.get("permission_type", MenuPermissionTypeEnum.PUBLIC),
            description=menu_data.get("description"),
            display_order=menu_data.get("display_order", 0),
            depth=depth,
            metadata=menu_data.get("metadata"),
            is_visible=True,
            is_active=True,
            created_by=username,
            updated_by=username,
        )

        db.add(menu)
        db.flush()  # Get ID

        # Update path with actual ID
        menu.path = f"{parent_path}/{menu.id}"

        print(f"  {'  ' * depth}✓ Created: {menu.menu_name} (ID: {menu.id}, Type: {menu.menu_type})")

        # Create children
        if "children" in menu_data:
            for child_data in menu_data["children"]:
                # Inherit parent's menu_type, link_type, permission_type if not specified
                if "menu_type" not in child_data:
                    child_data["menu_type"] = menu.menu_type
                if "link_type" not in child_data:
                    child_data["link_type"] = MenuLinkTypeEnum.INTERNAL
                if "permission_type" not in child_data:
                    child_data["permission_type"] = menu.permission_type

                create_menu_recursive(child_data, menu.id, depth + 1)

        return menu

    # Create all menu types
    print("\n📱 User Menus:")
    for menu_data in user_menus:
        create_menu_recursive(menu_data)

    print("\n⚙️  Admin Menus:")
    for menu_data in admin_menus:
        create_menu_recursive(menu_data)

    print("\n🔗 Site Menus:")
    for menu_data in site_menus:
        create_menu_recursive(menu_data)

    db.commit()
    print("\n✅ Sample menus created successfully!")


def main():
    """Main function"""
    db = SessionLocal()

    try:
        # Get or create default tenant
        tenant = db.query(Tenant).filter(Tenant.tenant_code == "default").first()
        if not tenant:
            print("Creating default tenant...")
            tenant = Tenant(
                tenant_code="default",
                tenant_name="Default Tenant",
                description="Default tenant for testing",
                admin_email="admin@example.com",
                admin_name="Admin",
                is_active=True,
                created_by="system",
                updated_by="system",
            )
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
            print(f"✅ Created tenant: {tenant.tenant_name} (ID: {tenant.id})")

        # Get or create admin user
        user = db.query(User).filter(
            User.tenant_id == tenant.id,
            User.username == "admin"
        ).first()

        if not user:
            print("Creating admin user...")
            user = User(
                tenant_id=tenant.id,
                username="admin",
                email="admin@example.com",
                full_name="System Administrator",
                hashed_password=get_password_hash("admin123"),
                is_superuser=True,
                is_active=True,
                created_by="system",
                updated_by="system",
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"✅ Created user: {user.username} (ID: {user.id})")

        # Delete existing menus (optional - for clean slate)
        existing_count = db.query(Menu).filter(Menu.tenant_id == tenant.id).count()
        if existing_count > 0:
            print(f"\n⚠️  Found {existing_count} existing menus. Delete them? (y/n)")
            response = input().strip().lower()
            if response == 'y':
                db.query(Menu).filter(Menu.tenant_id == tenant.id).delete()
                db.commit()
                print("✅ Deleted existing menus")

        # Create sample menus
        create_sample_menus(db, tenant.id, user.id, user.username)

        # Print summary
        user_count = db.query(Menu).filter(
            Menu.tenant_id == tenant.id,
            Menu.menu_type == MenuTypeEnum.USER
        ).count()
        admin_count = db.query(Menu).filter(
            Menu.tenant_id == tenant.id,
            Menu.menu_type == MenuTypeEnum.ADMIN
        ).count()
        site_count = db.query(Menu).filter(
            Menu.tenant_id == tenant.id,
            Menu.menu_type == MenuTypeEnum.SITE
        ).count()

        print("\n" + "="*60)
        print("📊 Summary")
        print("="*60)
        print(f"User Menus:  {user_count}")
        print(f"Admin Menus: {admin_count}")
        print(f"Site Menus:  {site_count}")
        print(f"Total:       {user_count + admin_count + site_count}")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
