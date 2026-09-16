import hashlib
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from .trace_context import SpanContext


class SamplingResult:
    def __init__(self, decision: bool, attributes: Optional[Dict[str, Any]] = None):
        self.decision = decision
        self.attributes = attributes or {}


class Sampler(ABC):
    @abstractmethod
    def should_sample(
        self,
        parent_context: Optional[SpanContext],
        trace_id: str,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> SamplingResult:
        pass


class AlwaysOnSampler(Sampler):
    def should_sample(self, parent_context, trace_id, name, attributes=None):
        return SamplingResult(True)


class AlwaysOffSampler(Sampler):
    def should_sample(self, parent_context, trace_id, name, attributes=None):
        return SamplingResult(False)


class ParentBasedSampler(Sampler):
    def __init__(self, root_sampler: Sampler):
        self.root_sampler = root_sampler

    def should_sample(self, parent_context, trace_id, name, attributes=None):
        if parent_context:
            return SamplingResult(parent_context.trace_flags == "01")
        return self.root_sampler.should_sample(parent_context, trace_id, name, attributes)


class TraceIdRatioBasedSampler(Sampler):
    def __init__(self, ratio: float = 0.1):
        self.ratio = max(0.0, min(1.0, ratio))

    def should_sample(self, parent_context, trace_id, name, attributes=None):
        if self.ratio >= 1.0:
            return SamplingResult(True)
        if self.ratio <= 0.0:
            return SamplingResult(False)
        # Deterministic hashing of trace_id
        val = int(hashlib.md5(trace_id.encode()).hexdigest(), 16) % 10000
        sampled = (val / 10000.0) < self.ratio
        return SamplingResult(sampled)


class OrganizationOverrideSampler(Sampler):
    def __init__(self, base_sampler: Sampler, org_overrides: Optional[Dict[str, float]] = None):
        self.base_sampler = base_sampler
        self.org_overrides = org_overrides or {}

    def set_org_override(self, org_id: str, ratio: float):
        self.org_overrides[org_id] = ratio

    def should_sample(self, parent_context, trace_id, name, attributes=None):
        attrs = attributes or {}
        org_id = attrs.get("organization.id")
        if org_id and org_id in self.org_overrides:
            ratio = self.org_overrides[org_id]
            ratio_sampler = TraceIdRatioBasedSampler(ratio)
            return ratio_sampler.should_sample(parent_context, trace_id, name, attributes)
        return self.base_sampler.should_sample(parent_context, trace_id, name, attributes)


class SamplerChain(Sampler):
    def __init__(self, samplers: list[Sampler]):
        self.samplers = samplers

    def should_sample(self, parent_context, trace_id, name, attributes=None):
        for sampler in self.samplers:
            res = sampler.should_sample(parent_context, trace_id, name, attributes)
            if res.decision:
                return res
        return SamplingResult(False)
