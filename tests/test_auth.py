import pytest
from datetime import timedelta
import jwt

from app.auth.jwt_service import JWTService
from app.auth.password_service import PasswordService
from app.auth.exceptions import ExpiredTokenException
from app.core.config import get_settings

settings = get_settings()

def test_password_hashing():
    password = "test_user_password_456"
    hashed = PasswordService.get_password_hash(password)
    
    assert password != hashed
    assert PasswordService.verify_password(password, hashed)
    assert not PasswordService.verify_password("wrongpassword", hashed)

def test_jwt_creation_and_verification():
    data = {"sub": "user123"}
    token = JWTService.create_access_token(data)
    
    payload = JWTService.verify_token(token)
    assert payload["sub"] == "user123"
    assert "exp" in payload

def test_jwt_expiry():
    data = {"sub": "user123"}
    # Create token that expires immediately
    token = JWTService.create_access_token(data, expires_delta=timedelta(seconds=-1))
    
    with pytest.raises(ExpiredTokenException):
        JWTService.verify_token(token)

def test_refresh_token_creation():
    data = {"sub": "user123"}
    token = JWTService.create_refresh_token(data)
    
    payload = JWTService.verify_token(token)
    assert payload["sub"] == "user123"
    assert payload["type"] == "refresh"
