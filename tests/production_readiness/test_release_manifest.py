from __future__ import annotations

from app.deployment.models import DeploymentIdentity
from app.deployment.release_manifest import ProductionReleaseManifest


def test_release_manifest_fingerprint_deterministic():
    identity1 = DeploymentIdentity(
        application_version="1.0.0",
        deployment_version="5.65",
        build_identifier="build-101",
        git_revision="git-abc1234",
        environment="STAGING",
        image_tag="enterprise-ai-platform:5.65",
        image_digest="sha256:29069a7755b4e7fb2cb2087977de57c745c28ecf636026be9c6b32e23d251762",
    )

    manifest1 = ProductionReleaseManifest.create_from_identity(identity1, configuration_fingerprint="cfg-99")
    manifest2 = ProductionReleaseManifest.create_from_identity(identity1, configuration_fingerprint="cfg-99")

    # Change volatile timestamp in manifest2
    manifest2.release_timestamp = "2099-01-01T00:00:00Z"

    assert manifest1.canonical_fingerprint() == manifest2.canonical_fingerprint()


def test_forbidden_image_tag_validation():
    identity = DeploymentIdentity(
        application_version="1.0.0",
        deployment_version="5.65",
        build_identifier="build-101",
        git_revision="git-abc1234",
        environment="PRODUCTION",
        image_tag="latest",
        image_digest="sha256:29069a7755b4e7fb2cb2087977de57c745c28ecf636026be9c6b32e23d251762",
    )

    manifest = ProductionReleaseManifest.create_from_identity(identity)
    valid, errors = manifest.validate_manifest()

    assert valid is False
    assert any("forbidden image tag" in err.lower() or "rejected" in err.lower() for err in errors)
