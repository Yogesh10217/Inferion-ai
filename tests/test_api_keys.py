import pytest
from app.auth.api_key_service import APIKeyService

def test_api_key_generation():
    raw_key, prefix, hashed_key = APIKeyService.generate_api_key()
    
    assert prefix == "sk"
    assert raw_key.startswith("sk_")
    assert len(raw_key) > 10
    
    # Hashed key should not be plaintext
    assert raw_key != hashed_key

def test_api_key_verification():
    raw_key, prefix, hashed_key = APIKeyService.generate_api_key()
    
    # Correct key
    assert APIKeyService.verify_api_key(raw_key, hashed_key) is True
    
    # Incorrect key
    assert APIKeyService.verify_api_key("sk_invalid123", hashed_key) is False
    
    # Different prefix
    assert APIKeyService.verify_api_key(raw_key.replace("sk_", "pk_"), hashed_key) is False
