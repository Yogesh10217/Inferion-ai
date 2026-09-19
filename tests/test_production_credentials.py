"""Pytest Suite for Production Credentials, Vault, AWS KMS, and LLM Providers."""

import pytest
from app.security.secrets import (
    SecretManager,
    EnvironmentSecretProvider,
    VaultSecretProvider,
    AWSSecretsManagerProvider,
)
from app.providers.provider_factory import ProviderFactory
from app.providers.bedrock_provider import BedrockProvider
from app.providers.azure_openai_provider import AzureOpenAIProvider
from app.schemas.request import InferenceRequest, ChatMessage


def test_environment_secret_provider():
    provider = EnvironmentSecretProvider()
    provider.set_secret("TEST_KEY", "secret_val_123")
    assert provider.get_secret("TEST_KEY") == "secret_val_123"
    assert provider.delete_secret("TEST_KEY") is True
    assert provider.get_secret("TEST_KEY") is None


def test_vault_secret_provider_fallback(monkeypatch):
    monkeypatch.setenv("TEST_VAULT_KEY", "vault_fallback_value")
    provider = VaultSecretProvider()
    val = provider.get_secret("TEST_VAULT_KEY")
    assert val == "vault_fallback_value"


def test_aws_secrets_manager_provider_fallback(monkeypatch):
    monkeypatch.setenv("TEST_AWS_KEY", "aws_fallback_value")
    provider = AWSSecretsManagerProvider()
    val = provider.get_secret("TEST_AWS_KEY")
    assert val == "aws_fallback_value"


def test_secret_manager_redaction():
    manager = SecretManager()
    manager.set_secret("API_KEY", "sk_live_super_secret_key_99")

    text = "User authorized with sk_live_super_secret_key_99."
    sanitized = manager.sanitize_text(text)
    assert "sk_live_super_secret_key_99" not in sanitized
    assert "[REDACTED_SECRET]" in sanitized


@pytest.mark.asyncio
async def test_bedrock_provider_mock_generate():
    provider = BedrockProvider()
    request = InferenceRequest(
        model="anthropic.claude-3-5-sonnet-20240620-v1:0",
        messages=[ChatMessage(role="user", content="Test Bedrock")],
        metadata={"mock": True}
    )
    response = await provider.generate(request)
    assert response.provider == "bedrock"
    assert "[Bedrock Mock Response]" in response.text
    assert response.usage.total_tokens > 0


@pytest.mark.asyncio
async def test_azure_openai_provider_mock_generate():
    provider = AzureOpenAIProvider()
    request = InferenceRequest(
        model="gpt-4o",
        messages=[ChatMessage(role="user", content="Test Azure OpenAI")],
        metadata={"mock": True}
    )
    response = await provider.generate(request)
    assert response.provider == "azure_openai"
    assert "[Azure OpenAI Mock Response]" in response.text
    assert response.usage.total_tokens > 0


def test_provider_factory_registers_bedrock_and_azure():
    factory = ProviderFactory()
    assert factory.provider_exists("bedrock") is True
    assert factory.provider_exists("azure_openai") is True

    bedrock_inst = factory.get_provider("bedrock")
    assert isinstance(bedrock_inst, BedrockProvider)

    azure_inst = factory.get_provider("azure_openai")
    assert isinstance(azure_inst, AzureOpenAIProvider)
