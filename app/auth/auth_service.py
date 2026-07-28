from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.auth.models import User, Session, AuditEvent, APIKey
from app.auth.password_service import PasswordService
from app.auth.jwt_service import JWTService
from app.auth.api_key_service import APIKeyService
from app.auth.exceptions import InvalidCredentialsException, UserInactiveException


class AuthService:
    @staticmethod
    async def log_audit_event(
        db: AsyncSession,
        event_type: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[str] = None,
    ) -> None:
        """Log an audit event to the database."""
        event = AuditEvent(
            event_type=event_type,
            user_id=user_id,
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
                db, "failed_authentication", user_id=user.id if user else None, ip_address=ip_address, details=f"Failed login for {username}"
            )
            raise InvalidCredentialsException()

        if not user.is_active:
            raise UserInactiveException()

        await AuthService.log_audit_event(db, "login", user_id=user.id, ip_address=ip_address)
        return user

    @staticmethod
    async def create_user_session(db: AsyncSession, user: User) -> Session:
        """Create a new session (refresh token) for the user."""
        token_data = {"sub": user.id}
        refresh_token = JWTService.create_refresh_token(token_data)
        
        # We store a hash of the refresh token in the DB to allow revoking it
        # without storing the plaintext token
        refresh_token_hash = PasswordService.get_password_hash(refresh_token)
        
        session = Session(
            user_id=user.id,
            refresh_token_hash=refresh_token_hash,
            expires_at=datetime.now(timezone.utc)
            # In a real app we'd calculate expires_at properly based on the refresh token expiry
        )
        db.add(session)
        await db.commit()
        await db.refresh(session)
        
        # We need to return both the DB model and the raw token for the client
        session.raw_token = refresh_token
        return session
