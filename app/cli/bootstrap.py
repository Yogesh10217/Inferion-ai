import argparse
import asyncio
import os
import sys

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import Permission, Role, User
from app.auth.password_service import PasswordService
from app.auth.permissions import SystemPermissions, SystemRoles
from app.core.database import Base, engine
from app.tenant.models import Membership, Organization

# Ensure app is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


async def bootstrap(admin_username: str, admin_email: str, admin_password: str):
    print("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("Database tables created.")
    print("Provisioning initial roles and permissions...")

    async with AsyncSession(engine) as session:
        # Create permissions
        all_perms = SystemPermissions.all()
        for perm_name in all_perms:
            result = await session.execute(select(Permission).where(Permission.name == perm_name))
            if not result.scalar_one_or_none():
                session.add(Permission(name=perm_name, description=f"Permission for {perm_name}"))

        await session.flush()

        # Create roles
        roles = [
            (SystemRoles.ADMIN, all_perms),
            (SystemRoles.DEVELOPER, SystemPermissions.developer_permissions()),
            (SystemRoles.VIEWER, SystemPermissions.viewer_permissions()),
        ]

        role_objs = {}
        for role_name, perms in roles:
            result = await session.execute(select(Role).where(Role.name == role_name))
            role = result.scalar_one_or_none()
            if not role:
                role = Role(name=role_name, description=f"{role_name} role")
                session.add(role)

            # Fetch permission objects
            perm_objs = []
            for p_name in perms:
                res = await session.execute(select(Permission).where(Permission.name == p_name))
                p = res.scalar_one_or_none()
                if p:
                    perm_objs.append(p)

            role.permissions = perm_objs
            role_objs[role_name] = role

        await session.flush()

        # Create personal org for admin if it doesn't exist
        result = await session.execute(select(Organization).where(Organization.slug == "admin-org"))
        org = result.scalar_one_or_none()
        if not org:
            org = Organization(name="Admin Organization", slug="admin-org")
            session.add(org)
            await session.flush()

        # Create admin user
        result = await session.execute(select(User).where(User.username == admin_username))
        admin = result.scalar_one_or_none()
        if not admin:
            admin = User(
                username=admin_username,
                email=admin_email,
                password_hash=PasswordService.get_password_hash(admin_password),
                is_admin=True,
                is_active=True,
                default_organization_id=org.id,
            )
            admin.roles.append(role_objs[SystemRoles.ADMIN])
            session.add(admin)
            await session.flush()

            # Add membership
            mem = Membership(
                organization_id=org.id, user_id=admin.id, role_id=role_objs[SystemRoles.ADMIN].id, status="active"
            )
            session.add(mem)
            print(f"Created admin user: {admin_username} in organization: {org.name}")
        else:
            print(f"Admin user {admin_username} already exists.")

        await session.commit()

    print("Bootstrap complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bootstrap LLM Inference Engine Auth DB")
    parser.add_argument("--username", default="admin", help="Admin username")
    parser.add_argument("--email", default="admin@example.com", help="Admin email")
    parser.add_argument("--password", required=True, help="Admin password")

    args = parser.parse_args()
    asyncio.run(bootstrap(args.username, args.email, args.password))
