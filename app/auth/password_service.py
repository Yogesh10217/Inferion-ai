import bcrypt

# Passlib 1.7.4 compatibility patch for bcrypt 4.0+
_orig_hashpw = bcrypt.hashpw


def _safe_hashpw(password: bytes, salt: bytes) -> bytes:
    if len(password) > 72:
        password = password[:72]
    return _orig_hashpw(password, salt)


bcrypt.hashpw = _safe_hashpw

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plaintext password against a hashed password."""
        return pwd_context.verify(plain_password[:72], hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a plaintext password using bcrypt."""
        return pwd_context.hash(password[:72])
