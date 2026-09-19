"""
Unit tests for Phase 6 — Enterprise & AI/ML Platform.
"""

import pytest

from app.sso.oidc import get_oidc_manager
from app.providers.provider_factory import ProviderFactory
from app.mlops.experiments import ExperimentManager
from app.cache.semantic_cache import SemanticCache
from app.compliance_platform.phi_detector import PHIDetector
from app.compliance_platform.gdpr import GDPRService
from app.mlops.fine_tuning.job_service import FineTuningService
from app.mlops.drift import DriftDetector
from app.schemas.inference_response import InferenceResponse, Usage
from app.schemas.request import InferenceRequest, ChatMessage


def test_oidc_sso_manager():
    manager = get_oidc_manager()
    url = manager.generate_authorize_url("google", "test-state")
    assert "https://accounts.google.com" in url
    assert "test-state" in url

    config = manager.get_provider("google")
    assert config is not None
    assert manager.map_groups_to_role(config, ["Admins"]) == "admin"


@pytest.mark.asyncio
async def test_all_llm_providers_instantiation_and_generation():
    factory = ProviderFactory()
    assert factory.provider_exists("anthropic")
    assert factory.provider_exists("gemini")
    assert factory.provider_exists("cohere")
    assert factory.provider_exists("mistral")

    req = InferenceRequest(
        model="claude-3-5-sonnet",
        messages=[ChatMessage(role="user", content="Test prompt")],
    )

    anthropic = factory.get_provider("anthropic")
    res_anthropic = await anthropic.generate(request=req)
    assert "anthropic" in res_anthropic.text.lower()

    gemini = factory.get_provider("gemini")
    res_gemini = await gemini.generate(request=req)
    assert "gemini" in res_gemini.text.lower()

    cohere = factory.get_provider("cohere")
    res_cohere = await cohere.generate(request=req)
    assert "cohere" in res_cohere.text.lower()

    mistral = factory.get_provider("mistral")
    res_mistral = await mistral.generate(request=req)
    assert "mistral" in res_mistral.text.lower()


def test_ab_testing_deterministic_traffic_splitting():
    exp_mgr = ExperimentManager()
    exp = exp_mgr.create_experiment("Headline Test")
    exp_mgr.add_variant(
        exp.experiment_id, "V1", "asset_1", "1.0", traffic_weight=50.0
    )
    exp_mgr.add_variant(
        exp.experiment_id, "V2", "asset_1", "2.0", traffic_weight=50.0
    )
    exp_mgr.start_experiment(exp.experiment_id)

    selected_1 = exp_mgr.select_variant_for_request(
        exp.experiment_id, "user-123"
    )
    selected_2 = exp_mgr.select_variant_for_request(
        exp.experiment_id, "user-123"
    )
    assert selected_1 is not None
    assert selected_1.variant_id == selected_2.variant_id  # Deterministic


def test_semantic_cache_hit_and_miss():
    cache = SemanticCache(similarity_threshold=0.90)
    resp = InferenceResponse(
        id="1",
        provider="openai",
        model="gpt-4o-mini",
        text="Cached output",
        usage=Usage(),
    )

    prompt = "Explain quantum computing in simple terms"
    cache.put(prompt, "gpt-4o-mini", resp)

    # High similarity lookup
    lookup = cache.get(prompt, "gpt-4o-mini")
    assert lookup is not None
    hit_resp, sim = lookup
    assert hit_resp.text == "Cached output"
    assert sim >= 0.90

    # Model mismatch lookup -> Miss
    assert cache.get(prompt, "claude-3-5-sonnet") is None


def test_phi_detector_scanning_and_redaction():
    detector = PHIDetector()
    text = "Patient SSN is 123-45-6789 and email is doctor@hospital.org"
    result = detector.scan(text)

    assert result.contains_phi is True
    assert len(result.matches) == 2
    assert "[REDACTED_SSN]" in result.sanitized_text
    assert "[REDACTED_EMAIL]" in result.sanitized_text


@pytest.mark.asyncio
async def test_gdpr_service_erasure():
    gdpr = GDPRService()
    record = await gdpr.erase_user_data("user-999")
    assert record.user_id == "user-999"
    assert record.records_deleted["users"] == 1
    assert record.records_deleted["api_keys"] == 3


def test_fine_tuning_service_lifecycle():
    ft = FineTuningService()
    job = ft.create_job("llama3.1", "s3://dataset/train.jsonl")
    assert job.status == "PENDING"

    updated = ft.update_job_status(
        job.job_id, "COMPLETED", fine_tuned_model_id="ft-llama3.1-v1"
    )
    assert updated.status == "COMPLETED"
    assert updated.fine_tuned_model_id == "ft-llama3.1-v1"


def test_drift_psi_divergence_computation():
    detector = DriftDetector()
    b_dist = [0.1, 0.4, 0.5]
    c_dist = [0.1, 0.4, 0.5]
    psi_identical = detector.compute_psi_divergence(b_dist, c_dist)
    assert psi_identical == 0.0

    c_dist_shifted = [0.6, 0.3, 0.1]
    psi_shifted = detector.compute_psi_divergence(b_dist, c_dist_shifted)
    assert psi_shifted > 0.1


@pytest.mark.asyncio
async def test_phase6_api_endpoints(get_client, admin_token_headers):
    async with get_client() as client:
        # SSO authorize endpoint
        sso_resp = await client.get(
            "/v1/auth/sso/authorize?provider_id=google",
            headers=admin_token_headers,
        )
        assert sso_resp.status_code == 200
        assert "authorization_url" in sso_resp.json()

        # SSO callback endpoint
        cb_resp = await client.get(
            "/v1/auth/sso/callback?code=mock_code&provider_id=google",
            headers=admin_token_headers,
        )
        assert cb_resp.status_code == 200
        assert "access_token" in cb_resp.json()

        # GDPR erasure endpoint
        gdpr_resp = await client.delete(
            "/v1/compliance/users/user_123/data",
            headers=admin_token_headers,
        )
        assert gdpr_resp.status_code == 200
        assert gdpr_resp.json()["user_id"] == "user_123"

        # Fine-tuning job endpoint
        ft_resp = await client.post(
            "/v1/mlops/fine-tuning/jobs",
            json={
                "model": "llama3.1",
                "dataset_uri": "s3://bucket/data.jsonl",
            },
            headers=admin_token_headers,
        )
        assert ft_resp.status_code == 200
        assert ft_resp.json()["model"] == "llama3.1"

        # GraphQL query endpoint
        gql_resp = await client.post(
            "/graphql",
            json={"query": "{ models { id provider status } }"},
            headers=admin_token_headers,
        )
        assert gql_resp.status_code == 200
        assert "data" in gql_resp.json()
