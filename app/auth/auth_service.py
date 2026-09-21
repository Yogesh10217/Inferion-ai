from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.exceptions import InvalidCredentialsException
from app.auth.jwt_service import JWTService
from app.auth.models import AuditEvent, Session, User
from app.auth.password_service import PasswordService


class AuthService:
    @staticmethod
    async def log_audit_event(
        db: AsyncSession,
        action: str,
        organization_id: Optional[str] = None,
        actor_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[str] = None,
    ) -> None:
        """Log an audit event to the database."""
        event = AuditEvent(
            action=action,
            organization_id=organization_id or "system",
            actor_id=actor_id,
            workspace_id=workspace_id,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            details=details,
        )
        db.add(event)
        await db.commit()

    @staticmethod
    async def authenticate_user(
        db: AsyncSession, username: str, password: str, ip_address: Optional[str] = None
    ) -> User:
        """Authenticate a user using username and password."""
        stmt = select(User).where(User.username == username)
        result = await db.execute(stmt)
        user = result.scalar_one_or_none()

        if not user or not PasswordService.verify_password(password, user.password_hash):
            await AuthService.log_audit_event(
                db,
                "failed_authentication",
                actor_id=user.id if user else None,
                ip_address=ip_address,
                details=f"Failed login for {username}",
            )
            raise InvalidCredentialsException()

        # If user has no default_organization_id, we can't fully login unless we do it without org
        # But we must log the audit event.
        # We will use the user's default org for the session if available, else require selection later.
        org_id = user.default_organization_id
        if not org_id:
            # Find first available org for audit log
            from app.tenant.models import Membership

            stmt_mem = select(Membership).where(Membership.user_id == user.id)
            res_mem = await db.execute(stmt_mem)
            mem = res_mem.scalars().first()
            org_id = mem.organization_id if mem else "SYSTEM"

        await AuthService.log_audit_event(db, "login", organization_id=org_id, actor_id=user.id, ip_address=ip_address)
        return user

    @staticmethod
    async def create_user_session(db: AsyncSession, user: User, organization_id: str) -> Session:
        """Create a new session (refresh token) for the user within an organization context."""
        token_data = {"sub": user.id}
        refresh_token = JWTService.create_refresh_token(token_data)

        # We store a hash of the refresh token in the DB to allow revoking it
        # without storing the plaintext token
        refresh_token_hash = PasswordService.get_password_hash(refresh_token)

        session = Session(
            user_id=user.id,
            organization_id=organization_id,
            refresh_token_hash=refresh_token_hash,
            expires_at=datetime.now(timezone.utc),
            # In a real app we'd calculate expires_at properly based on the refresh token expiry
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)

        # We need to return both the DB model and the raw token for the client
        session.raw_token = refresh_token
        return session
