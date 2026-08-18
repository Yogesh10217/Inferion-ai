"""
Supervisor Agent for Team Execution Monitoring, Failure Handling, and Approval Escalations
"""

import logging
from typing import Dict, Any, List, Optional
from app.multi_agent.agent_team import AgentTeam
from app.multi_agent.agent_messaging import AgentMessage, MessageType
from app.multi_agent.exceptions import SupervisorEscalationError

logger = logging.getLogger(__name__)


class SupervisorAgent:
    """Monitors team execution, resolves deadlocks, handles failures, and escalates approvals."""

    def __init__(self, supervisor_id: str = "supervisor_root", team: Optional[AgentTeam] = None):
        self.supervisor_id = supervisor_id
        self.team = team
        self.monitored_failures: List[Dict[str, Any]] = []

    def monitor_execution_step(self, step_data: Dict[str, Any]) -> bool:
        """Inspect execution step for errors or high-risk actions requiring supervisor intervention."""
        status = step_data.get("status")
        if status in ("failed", "error"):
            self.monitored_failures.append(step_data)
            logger.warning(f"[SUPERVISOR] Detected execution failure in team: {step_data.get('error')}")
            return False
        return True

    def detect_deadlock(self, pending_messages: List[AgentMessage]) -> bool:
        """Detect circular dependencies or unanswered questions in message queue."""
        unanswered_questions = [m for m in pending_messages if m.message_type == MessageType.QUESTION]
        if len(unanswered_questions) > 5:
            logger.warning(f"[SUPERVISOR] Deadlock detected: {len(unanswered_questions)} unanswered questions")
            return True
        return False

    def handle_escalation(self, agent_id: str, reason: str, team_id: str) -> Dict[str, Any]:
        """Process an escalation from a team member."""
        logger.info(f"[SUPERVISOR] Handling escalation from agent '{agent_id}' for team '{team_id}': {reason}")
        return {
            "status": "escalated",
            "supervisor_id": self.supervisor_id,
            "agent_id": agent_id,
            "team_id": team_id,
            "reason": reason,
            "action": "human_approval_required",
        }
