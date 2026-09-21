"""Unit tests for AuthenticationManager assurance levels and verification."""

import pytest

from app.identity.authentication import AuthenticationAssuranceLevel, AuthenticationManager, AuthenticationMethod
from app.identity.exceptions import AuthenticationAssuranceException


def test_authentication_assurance_verification():
    mgr = AuthenticationManager()

    # JWT login -> STANDARD assurance
    res_jwt = mgr.authenticate("user_1", method=AuthenticationMethod.JWT)
    assert res_jwt.assurance_level == AuthenticationAssuranceLevel.STANDARD

    # Verify STANDARD -> Pass
    assert mgr.verify_assurance(res_jwt.session_id, AuthenticationAssuranceLevel.STANDARD) is True

    # Verify HIGH requirement for STANDARD session -> Exception
    with pytest.raises(AuthenticationAssuranceException):
        mgr.verify_assurance(res_jwt.session_id, AuthenticationAssuranceLevel.HIGH)

    # MFA Login -> HIGH assurance
    res_mfa = mgr.authenticate("user_1", method=AuthenticationMethod.MFA, mfa_verified=True)
    assert res_mfa.assurance_level == AuthenticationAssuranceLevel.HIGH
    assert mgr.verify_assurance(res_mfa.session_id, AuthenticationAssuranceLevel.HIGH) is True
