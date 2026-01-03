"""Create shared schema tables

Revision ID: 001_create_shared_schema
Revises:
Create Date: 2024-01-03 08:00:00.000000

This migration creates the shared database schema for multi-tenant architecture,
including tables for tenants, users, roles, permissions, and user groups.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_create_shared_schema'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create shared schema tables"""

    # Create tenants table
    op.create_table(
        'tenants',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('tenant_code', sa.String(50), nullable=False),
        sa.Column('tenant_name', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('domain', sa.String(255), nullable=True),
        sa.Column('subdomain', sa.String(100), nullable=True),
        sa.Column('settings', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('admin_email', sa.String(255), nullable=True),
        sa.Column('admin_name', sa.String(100), nullable=True),
        sa.Column('status', sa.Enum('active', 'suspended', 'inactive', name='tenantstatusenum'), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.String(100), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_by', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_code', name='uq_tenants_tenant_code'),
        sa.UniqueConstraint('domain', name='uq_tenants_domain'),
        sa.UniqueConstraint('subdomain', name='uq_tenants_subdomain'),
    )
    op.create_index('idx_tenant_code', 'tenants', ['tenant_code'])
    op.create_index('idx_domain', 'tenants', ['domain'])
    op.create_index('idx_subdomain', 'tenants', ['subdomain'])
    op.create_index('idx_status', 'tenants', ['status'])

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(100), nullable=True),
        sa.Column('phone', sa.String(20), nullable=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('profile_image_url', sa.String(500), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('status', sa.Enum('active', 'inactive', 'suspended', 'deleted', name='userstatusenum'), nullable=False, server_default='active'),
        sa.Column('is_email_verified', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('email_verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.String(100), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_by', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'username', name='uk_tenant_username'),
        sa.UniqueConstraint('tenant_id', 'email', name='uk_tenant_email'),
    )
    op.create_index('idx_tenant_id', 'users', ['tenant_id'])
    op.create_index('idx_email', 'users', ['email'])
    op.create_index('idx_status', 'users', ['status'])

    # Create user_groups table
    op.create_table(
        'user_groups',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('tenant_id', sa.BigInteger(), nullable=True),
        sa.Column('group_name', sa.String(100), nullable=False),
        sa.Column('group_code', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('priority', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('group_type', sa.Enum('system', 'custom', name='usergrouptypeenum'), nullable=False, server_default='custom'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.String(100), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_by', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'group_code', name='uk_tenant_group_code'),
    )
    op.create_index('idx_tenant_id', 'user_groups', ['tenant_id'])
    op.create_index('idx_group_code', 'user_groups', ['group_code'])
    op.create_index('idx_priority', 'user_groups', ['priority'])

    # Create user_group_members table
    op.create_table(
        'user_group_members',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('group_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.String(100), nullable=True),
        sa.ForeignKeyConstraint(['group_id'], ['user_groups.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'group_id', name='uk_user_group'),
    )
    op.create_index('idx_user_id', 'user_group_members', ['user_id'])
    op.create_index('idx_group_id', 'user_group_members', ['group_id'])

    # Create roles table
    op.create_table(
        'roles',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('role_name', sa.String(100), nullable=False),
        sa.Column('role_code', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('priority', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('role_type', sa.Enum('admin', 'user', 'both', name='roletypeenum'), nullable=False, server_default='both'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.String(100), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_by', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('role_code', name='uq_roles_role_code'),
    )
    op.create_index('idx_role_code', 'roles', ['role_code'])
    op.create_index('idx_priority', 'roles', ['priority'])

    # Create user_roles table
    op.create_table(
        'user_roles',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('user_id', sa.BigInteger(), nullable=False),
        sa.Column('role_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.String(100), nullable=True),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'role_id', name='uk_user_role'),
    )
    op.create_index('idx_user_id', 'user_roles', ['user_id'])
    op.create_index('idx_role_id', 'user_roles', ['role_id'])

    # Create permissions table
    op.create_table(
        'permissions',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('permission_name', sa.String(100), nullable=False),
        sa.Column('permission_code', sa.String(100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('resource', sa.Enum('tenant', 'user', 'menu', 'board', 'category', 'role', 'permission', name='permissionresourceenum'), nullable=False),
        sa.Column('action', sa.Enum('create', 'read', 'update', 'delete', 'manage', name='permissionactionenum'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.String(100), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_by', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('permission_code', name='uq_permissions_permission_code'),
    )
    op.create_index('idx_permission_code', 'permissions', ['permission_code'])
    op.create_index('idx_resource_action', 'permissions', ['resource', 'action'])

    # Create role_permissions table
    op.create_table(
        'role_permissions',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('role_id', sa.BigInteger(), nullable=False),
        sa.Column('permission_id', sa.BigInteger(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.String(100), nullable=True),
        sa.ForeignKeyConstraint(['permission_id'], ['permissions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('role_id', 'permission_id', name='uk_role_permission'),
    )
    op.create_index('idx_role_id', 'role_permissions', ['role_id'])
    op.create_index('idx_permission_id', 'role_permissions', ['permission_id'])

    # Create menus table
    op.create_table(
        'menus',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False),
        sa.Column('menu_name', sa.String(100), nullable=False),
        sa.Column('menu_code', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('menu_url', sa.String(500), nullable=True),
        sa.Column('menu_icon', sa.String(100), nullable=True),
        sa.Column('display_order', sa.BigInteger(), nullable=False, server_default='0'),
        sa.Column('parent_id', sa.BigInteger(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.String(100), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_by', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'menu_code', name='uk_tenant_menu_code'),
    )
    op.create_index('idx_tenant_id', 'menus', ['tenant_id'])
    op.create_index('idx_menu_code', 'menus', ['menu_code'])
    op.create_index('idx_display_order', 'menus', ['display_order'])

    # Create boards table
    op.create_table(
        'boards',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('tenant_id', sa.BigInteger(), nullable=False),
        sa.Column('board_name', sa.String(100), nullable=False),
        sa.Column('board_code', sa.String(50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('created_by', sa.String(100), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_by', sa.String(100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'board_code', name='uk_tenant_board_code'),
    )
    op.create_index('idx_tenant_id', 'boards', ['tenant_id'])
    op.create_index('idx_board_code', 'boards', ['board_code'])


def downgrade() -> None:
    """Drop shared schema tables"""
    op.drop_table('boards')
    op.drop_table('menus')
    op.drop_table('role_permissions')
    op.drop_table('permissions')
    op.drop_table('user_roles')
    op.drop_table('roles')
    op.drop_table('user_group_members')
    op.drop_table('user_groups')
    op.drop_table('users')
    op.drop_table('tenants')
