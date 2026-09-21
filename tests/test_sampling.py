from app.tracing.sampling import (
    AlwaysOffSampler,
    AlwaysOnSampler,
    OrganizationOverrideSampler,
    TraceIdRatioBasedSampler,
)


def test_sampling_decisions():
    always_on = AlwaysOnSampler()
    assert always_on.should_sample(None, "id1", "span1").decision is True

    always_off = AlwaysOffSampler()
    assert always_off.should_sample(None, "id1", "span1").decision is False

    ratio_sampler = TraceIdRatioBasedSampler(0.0)
    assert ratio_sampler.should_sample(None, "id1", "span1").decision is False

    org_sampler = OrganizationOverrideSampler(always_off, {"org_vip": 1.0})
    res_vip = org_sampler.should_sample(None, "id1", "span1", {"organization.id": "org_vip"})
    assert res_vip.decision is True

    res_normal = org_sampler.should_sample(None, "id1", "span1", {"organization.id": "org_normal"})
    assert res_normal.decision is False
