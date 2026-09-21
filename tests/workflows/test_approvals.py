"""
Tests for Human Approval Queue & Audit Log System
"""

from app.workflows.approvals import ApprovalDecision, ApprovalManager


def test_approval_manager_lifecycle():
    mgr = ApprovalManager()
    req = mgr.create_request(run_id="run_100", node_id="appr_node", workflow_id="wf_test", prompt="Deploy to Prod?")

    assert req.status == ApprovalDecision.PENDING
    assert mgr.get_pending_request_for_run("run_100").request_id == req.request_id

    # Approve
    decided = mgr.approve(req.request_id, decided_by="admin_user", feedback="Approved for deployment")
    assert decided.status == ApprovalDecision.APPROVED
    assert decided.feedback == "Approved for deployment"
    assert len(decided.audit_log) == 2
    assert mgr.get_pending_request_for_run("run_100") is None


def test_approval_rejection():
    mgr = ApprovalManager()
    req = mgr.create_request(run_id="run_200", node_id="appr_node", workflow_id="wf_test")

    rejected = mgr.reject(req.request_id, decided_by="reviewer", feedback="Security risk")
    assert rejected.status == ApprovalDecision.REJECTED
    assert rejected.feedback == "Security risk"
