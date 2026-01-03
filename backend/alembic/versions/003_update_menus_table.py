"""Update menus table for enhanced menu management

Revision ID: 003_update_menus_table
Revises: 002_create_categories_table
Create Date: 2026-01-03 10:00:00.000000

This migration updates the menus table to support:
- Menu types (user, site, admin)
- Permission-based access control
- Link behavior types
- Hierarchical structure with depth and path
- Visibility and metadata
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_update_menus_table'
down_revision = '002_create_categories_table'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Apply schema changes"""

    # Create enum types
    menu_type_enum = postgresql.ENUM('user', 'site', 'admin', name='menutypeenum', create_type=True)
    menu_type_enum.create(op.get_bind(), checkfirst=True)

    menu_permission_type_enum = postgresql.ENUM(
        'public', 'authenticated', 'role_based', 'permission_based',
        name='menupermissiontypeenum',
        create_type=True
    )
    menu_permission_type_enum.create(op.get_bind(), checkfirst=True)

    menu_link_type_enum = postgresql.ENUM(
        'internal', 'external', 'new_tab', 'modal', 'none',
        name='menulinktypeenum',
        create_type=True
    )
    menu_link_type_enum.create(op.get_bind(), checkfirst=True)

    # Add new columns to menus table
    op.add_column('menus', sa.Column(
        'menu_type',
        sa.Enum('user', 'site', 'admin', name='menutypeenum'),
        nullable=False,
        server_default='user',
        comment='Menu type: user, site, admin'
    ))

    op.add_column('menus', sa.Column(
        'link_type',
        sa.Enum('internal', 'external', 'new_tab', 'modal', 'none', name='menulinktypeenum'),
        nullable=False,
        server_default='internal',
        comment='How the link should be opened'
    ))

    op.add_column('menus', sa.Column(
        'depth',
        sa.BigInteger(),
        nullable=False,
        server_default='0',
        comment='Depth level in hierarchy (0=root)'
    ))

    op.add_column('menus', sa.Column(
        'path',
        sa.String(500),
        nullable=True,
        comment='Materialized path (e.g., /1/3/5)'
    ))

    op.add_column('menus', sa.Column(
        'permission_type',
        sa.Enum('public', 'authenticated', 'role_based', 'permission_based', name='menupermissiontypeenum'),
        nullable=False,
        server_default='public',
        comment='Permission requirement type'
    ))

    op.add_column('menus', sa.Column(
        'is_visible',
        sa.Boolean(),
        nullable=False,
        server_default='true',
        comment='Whether menu is visible'
    ))

    op.add_column('menus', sa.Column(
        'metadata',
        postgresql.JSON(astext_type=sa.Text()),
        nullable=True,
        comment='Additional metadata (badge, tooltip, etc.)'
    ))

    # Add foreign key constraint for parent_id (self-referencing)
    op.create_foreign_key(
        'fk_menus_parent_id',
        'menus',
        'menus',
        ['parent_id'],
        ['id'],
        ondelete='CASCADE'
    )

    # Add new indexes
    op.create_index('idx_menu_type', 'menus', ['menu_type'])
    op.create_index('idx_parent_id', 'menus', ['parent_id'])
    op.create_index('idx_tenant_type_parent', 'menus', ['tenant_id', 'menu_type', 'parent_id'])

    # Add comments to existing columns
    op.alter_column('menus', 'tenant_id', comment='Tenant ID for multi-tenancy')
    op.alter_column('menus', 'menu_name', comment='Menu display name')
    op.alter_column('menus', 'menu_code', comment='Unique menu code within tenant')
    op.alter_column('menus', 'menu_url', comment='Menu URL or route path')
    op.alter_column('menus', 'menu_icon', comment='Icon class or name (e.g., fa-home)')
    op.alter_column('menus', 'display_order', comment='Display order within same parent')
    op.alter_column('menus', 'parent_id', comment='Parent menu ID for hierarchical structure')


def downgrade() -> None:
    """Revert schema changes"""

    # Drop new indexes
    op.drop_index('idx_tenant_type_parent', 'menus')
    op.drop_index('idx_parent_id', 'menus')
    op.drop_index('idx_menu_type', 'menus')

    # Drop foreign key constraint
    op.drop_constraint('fk_menus_parent_id', 'menus', type_='foreignkey')

    # Drop new columns
    op.drop_column('menus', 'metadata')
    op.drop_column('menus', 'is_visible')
    op.drop_column('menus', 'permission_type')
    op.drop_column('menus', 'path')
    op.drop_column('menus', 'depth')
    op.drop_column('menus', 'link_type')
    op.drop_column('menus', 'menu_type')

    # Drop enum types
    sa.Enum(name='menulinktypeenum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='menupermissiontypeenum').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='menutypeenum').drop(op.get_bind(), checkfirst=True)
