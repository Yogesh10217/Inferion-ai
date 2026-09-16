"""
Learning Engine for Autonomous Continuous Self-Improvement
"""

import logging
from typing import Any, Dict, Optional

from app.learning.optimization_engine import OptimizationEngine
from app.learning.pattern_detector import PatternDetector
from app.memory.memory_service import MemoryService

logger = logging.getLogger(__name__)


class LearningEngine:
    """Consolidates experience across execution episodes to drive platform self-improvement."""

    def __init__(self, memory_service: Optional[MemoryService] = None):
        self.memory_service = memory_service or MemoryService()
        self.pattern_detector = PatternDetector()
        self.optimization_engine = OptimizationEngine()

    def learn_from_episode(self, episode_id: str, episode_data: Dict[str, Any], tenant_id: str = "default_tenant") -> Dict[str, Any]:
        """Process completed or failed episode to extract lessons and update memory."""
        status = episode_data.get("status", "completed")
        history = episode_data.get("history", [episode_data])

        patterns = self.pattern_detector.detect_patterns(history)
        opt_rec = self.optimization_engine.optimize_plan_workflow(episode_id, episode_data.get("nodes", []))

        # Store lesson in Episodic Memory via Phase 5.3 Memory Service
        mem_content = f"[Episode: {episode_id}] Status: {status}. Patterns: {[p.description for p in patterns]}"
        self.memory_service.create_memory_entry(
            content=mem_content,
            organization_id=tenant_id,
            workspace_id="default_workspace",
            user_id="learning_engine",
            context_hint=f"episode_{episode_id}",
        )

        logger.info(f"[LEARNING ENGINE] Processed episode '{episode_id}' (status: {status}), saved lesson to memory")
        return {
            "episode_id": episode_id,
            "status": status,
            "patterns_detected": [p.model_dump() for p in patterns],
            "optimization_recommendation": opt_rec.model_dump(),
        }
