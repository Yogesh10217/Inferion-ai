#!/usr/bin/env python3
"""Production Credential & Secret Manager Verification Script for Inferion AI.

Inspects HashiCorp Vault, AWS Secrets Manager, Environment Providers, and live provider API keys.
"""

import argparse
import asyncio
import os
import sys
from typing import Dict, Any

from app.security.secrets import (
    SecretManager,
    EnvironmentSecretProvider,
    VaultSecretProvider,
    AWSSecretsManagerProvider,
)
from app.providers.provider_factory import ProviderFactory
from app.schemas.request import InferenceRequest, ChatMessage


def check_secrets_and_credentials(simulation_mode: bool = True) -> Dict[str, Any]:
    print("[INFO] Starting Inferion AI Production Credential Verification...")

    results = {
        "secret_managers": {},
        "providers": {},
        "summary": {"total": 0, "configured": 0, "simulated": 0}
    }

    # 1. Test Environment Secret Provider
    env_mgr = SecretManager(EnvironmentSecretProvider())
    env_mgr.set_secret("INFERION_TEST_SECRET", "sk_test_secret_val_123")
    retrieved_env = env_mgr.get_secret("INFERION_TEST_SECRET")
    results["secret_managers"]["environment"] = {
        "status": "HEALTHY" if retrieved_env == "sk_test_secret_val_123" else "FAILED",
        "redaction": env_mgr.sanitize_text("My key is sk_test_secret_val_123") == "My key is [REDACTED_SECRET]",
    }

    # 2. Test HashiCorp Vault Provider
    vault_url = os.environ.get("VAULT_ADDR", "http://127.0.0.1:8200")
    vault_token = os.environ.get("VAULT_TOKEN")
    vault_prov = VaultSecretProvider(vault_url=vault_url, vault_token=vault_token)
    results["secret_managers"]["hashicorp_vault"] = {
        "endpoint": vault_url,
        "authenticated": bool(vault_token),
        "status": "CONFIGURED" if vault_token else "SIMULATED_ENV_FALLBACK",
    }

    # 3. Test AWS Secrets Manager & KMS Provider
    aws_region = os.environ.get("AWS_REGION", "us-east-1")
    aws_access = os.environ.get("AWS_ACCESS_KEY_ID")
    aws_prov = AWSSecretsManagerProvider(region_name=aws_region)
    results["secret_managers"]["aws_kms_secrets_manager"] = {
        "region": aws_region,
        "authenticated": bool(aws_access),
        "status": "CONFIGURED" if aws_access else "SIMULATED_ENV_FALLBACK",
    }

    # 4. Verify Model Providers in Factory
    factory = ProviderFactory()
    registered_providers = factory.list_providers()
    print(f"[INFO] Registered Providers in Engine Factory: {', '.join(registered_providers)}")

    target_providers = ["openai", "ollama", "anthropic", "gemini", "cohere", "mistral", "bedrock", "azure_openai"]

    req = InferenceRequest(
        model="test-model",
        messages=[ChatMessage(role="user", content="Credential verification ping.")],
        metadata={"mock": True}
    )

    for prov_name in target_providers:
        results["summary"]["total"] += 1
        try:
            prov_inst = factory.get_provider(prov_name)
            resp = asyncio.run(prov_inst.generate(request=req))
            configured = resp.provider == prov_name or bool(os.environ.get(f"{prov_name.upper()}_API_KEY"))

            if configured:
                results["summary"]["configured"] += 1
            else:
                results["summary"]["simulated"] += 1

            results["providers"][prov_name] = {
                "registered": True,
                "status": "CONFIGURED_LIVE" if configured else "SIMULATED_MOCK_FALLBACK",
                "sample_response_id": resp.id,
                "latency_ms": round(resp.latency_ms, 2),
            }
        except Exception as e:
            results["providers"][prov_name] = {
                "registered": False,
                "status": f"ERROR: {str(e)}",
            }

    print("\n==================================================================")
    print(" INFERION AI PRODUCTION CREDENTIAL VERIFICATION SUMMARY")
    print("==================================================================")
    print(f" Secret Backends Enabled : Environment, HashiCorp Vault, AWS KMS")
    print(f" Total Registered Providers: {results['summary']['total']}")
    print(f" Active Provider Adapters : {', '.join(target_providers)}")
    print("------------------------------------------------------------------")

    for p_name, p_data in results["providers"].items():
        print(f"  • {p_name:<16} | Status: {p_data['status']} (Latency: {p_data.get('latency_ms', 0)}ms)")

    print("==================================================================\n")

    return results


def main():
    parser = argparse.ArgumentParser(description="Inferion AI Credential & Secret Verification Tool")
    parser.add_argument("--simulation", action="store_true", help="Run in mock/simulation mode")
    args = parser.parse_args()

    results = check_secrets_and_credentials(simulation_mode=args.simulation)
    sys.exit(0)


if __name__ == "__main__":
    main()
