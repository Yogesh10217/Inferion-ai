"""Unit tests for APIContractValidator and breaking change detection."""

import pytest

from app.developer_platform.api_contracts import APIContract, APIContractValidator
from app.developer_platform.exceptions import APIContractBreakingChangeException


def test_breaking_change_detection_and_approval_trigger():
    validator = APIContractValidator()

    old_contract = APIContract(contract_id="c1", service_id="svc_1", endpoints={"/v1/predict": {"method": "POST"}})
    new_contract = APIContract(contract_id="c2", service_id="svc_1", endpoints={"/v2/predict": {"method": "POST"}})

    # Endpoint '/v1/predict' removed in new_contract -> breaking change exception
    with pytest.raises(APIContractBreakingChangeException):
        validator.compare_contracts(old_contract, new_contract, tenant_id="t_bc")
