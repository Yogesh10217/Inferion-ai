"""Contract Semantic Versioning & Compatibility Subsystem (Phase 5.30)."""

from enum import Enum
from typing import Optional

from pydantic import BaseModel

from app.platform_contracts.exceptions import ContractVersionException


class ContractCompatibility(str, Enum):
    COMPATIBLE = "COMPATIBLE"
    BACKWARD_COMPATIBLE = "BACKWARD_COMPATIBLE"
    INCOMPATIBLE = "INCOMPATIBLE"


class ContractVersion(BaseModel):
    major: int = 1
    minor: int = 0
    patch: int = 0

    def to_string(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    @classmethod
    def parse(cls, version_str: str) -> "ContractVersion":
        try:
            parts = [int(p) for p in version_str.strip().split(".")]
            if len(parts) == 3:
                return cls(major=parts[0], minor=parts[1], patch=parts[2])
            elif len(parts) == 2:
                return cls(major=parts[0], minor=parts[1], patch=0)
            elif len(parts) == 1:
                return cls(major=parts[0], minor=0, patch=0)
        except Exception:
            pass
        return cls(major=1, minor=0, patch=0)


class ContractVersionRange(BaseModel):
    min_version: str = "1.0.0"
    max_version: Optional[str] = None


class ContractCompatibilityValidator:
    """Validates semantic compatibility across contract versions."""

    @staticmethod
    def check_compatibility(current_version: str, expected_version: str) -> ContractCompatibility:
        curr = ContractVersion.parse(current_version)
        exp = ContractVersion.parse(expected_version)

        if curr.major != exp.major:
            return ContractCompatibility.INCOMPATIBLE
        if curr.minor >= exp.minor:
            return ContractCompatibility.COMPATIBLE
        return ContractCompatibility.BACKWARD_COMPATIBLE

    @staticmethod
    def validate(current_version: str, expected_version: str) -> bool:
        compat = ContractCompatibilityValidator.check_compatibility(current_version, expected_version)
        if compat == ContractCompatibility.INCOMPATIBLE:
            raise ContractVersionException(current_version, f"Major version must match '{expected_version}'")
        return True
