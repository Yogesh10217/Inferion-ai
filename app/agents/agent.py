"""
Core Agent Driver & Execution Pipeline
"""

import logging
import time
from typing import Optional

from app.agents.agent_config import AgentConfig
from app.agents.agent_context import AgentContext
from app.agents.agent_state import AgentState, AgentStatus, ExecutionStep, StepType
from app.agents.approval import ApprovalController
from app.agents.artifacts.manager import ArtifactManager
from app.agents.budget import AgentBudgetTracker
from app.agents.checkpoint import CheckpointManager
from app.agents.exceptions import ApprovalRequiredException, MaxIterationsReachedError
from app.agents.memory.coordinator import MemoryCoordinator
from app.agents.planner.factory import PlannerFactory
from app.agents.reflection.self_critique import SelfCritiqueReflection
from app.agents.tools.executor import ToolExecutor
from app.agents.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


class Agent:
    def __init__(
        self,
        agent_id: str,
        config: AgentConfig,
        tool_registry: Optional[ToolRegistry] = None,
        tool_executor: Optional[ToolExecutor] = None,
        memory_coordinator: Optional[MemoryCoordinator] = None,
    ):
        self.agent_id = agent_id
        self.config = config
        self.tool_registry = tool_registry or ToolRegistry()
        self.tool_executor = tool_executor or ToolExecutor(registry=self.tool_registry)
        self.memory = memory_coordinator or MemoryCoordinator()
        self.planner = PlannerFactory.get_planner(config.planner_strategy)
        self.reflection = SelfCritiqueReflection()
        self.approval_controller = ApprovalController()
        self.checkpoint_manager = CheckpointManager()
        self.artifact_manager = ArtifactManager()

    async def run(self, user_request: str, context: AgentContext, state: AgentState) -> AgentState:
        logger.info(f"Agent '{self.config.name}' starting execution for goal: '{user_request}'")
        state.status = AgentStatus.PLANNING
        budget = AgentBudgetTracker(max_cost_dollars=self.config.max_cost_dollars, max_tokens=self.config.max_tokens)

        self.memory.working_memory.goal = user_request
        self.memory.conversation_memory.add_message("user", user_request)

        # Retrieve available tool definitions
        available_tools = {
            t_name: self.tool_registry.get_definition(t_name)
            for t_name in self.config.tools
            if t_name in self.tool_registry.list_tools()
        }

        retry_count = 0
        max_retries = 3

        while state.current_iteration < state.max_iterations:
            state.current_iteration += 1
            start_step_time = time.time()
            iter_num = state.current_iteration

            # 1. Planning Step
            state.status = AgentStatus.PLANNING
            history_repr = [step.model_dump() for step in state.execution_history]
            plan = await self.planner.create_plan(
                goal=user_request, available_tools=available_tools, execution_history=history_repr, context=context
            )
            state.plan_steps = plan

            # Save initial checkpoint
            self.checkpoint_manager.save_checkpoint(state.session_id, state, f"iter_{iter_num}")

            if not plan:
                break

            step = plan[0]
            tool_name = step.get("tool")
            tool_input = step.get("tool_input", {})
            obs_status = ""

            # 2. Human Approval Check
            if tool_name:
                try:
                    self.approval_controller.check_approval(
                        tool_name=tool_name,
                        tool_args=tool_input,
                        required_tools=self.config.require_approval_tools,
                        session_id=state.session_id,
                        state=state,
                    )
                except ApprovalRequiredException:
                    logger.info(f"Session '{state.session_id}' paused for human approval.")
                    return state

            # 3. Tool Execution & Observation
            if tool_name:
                state.status = AgentStatus.EXECUTING_TOOL
                try:
                    exec_res = await self.tool_executor.execute_tool(
                        tool_name=tool_name, kwargs=tool_input, context=context, budget_tracker=budget
                    )
                    obs_status = "SUCCESS"
                    obs_output = exec_res.get("result", {})
                    obs_error = None
                except Exception as e:
                    obs_status = "FAILED"
                    obs_output = {}
                    obs_error = str(e)

                step_record = ExecutionStep(
                    step_id=f"step_{iter_num}",
                    step_type=StepType.TOOL_CALL,
                    iteration=iter_num,
                    title=f"Tool Execution: {tool_name}",
                    input_data={"tool": tool_name, "input": tool_input},
                    output_data={"result": obs_output},
                    status=obs_status,
                    error=obs_error,
                    duration_ms=(time.time() - start_step_time) * 1000,
                )
                state.execution_history.append(step_record)
                self.memory.working_memory.add_step(tool_name, obs_output if obs_status == "SUCCESS" else obs_error)

            # 4. Reflection Step
            if self.config.enable_reflection:
                state.status = AgentStatus.REFLECTING
                refl_res = await self.reflection.reflect(
                    goal=user_request,
                    execution_history=[s.model_dump() for s in state.execution_history],
                    context=context,
                )
                if refl_res.get("retry_recommended") and retry_count < max_retries:
                    retry_count += 1
                    logger.warning(f"Reflection requested retry ({retry_count}/{max_retries})")
                    continue

            # 5. Check Termination / Final Response Creation
            if obs_status == "SUCCESS" or not tool_name:
                final_res = f"Completed goal '{user_request}' successfully based on tool observations."
                state.final_output = final_res
                state.status = AgentStatus.COMPLETED
                self.memory.conversation_memory.add_message("assistant", final_res)
                await self.memory.save_session_memory(state.session_id)
                return state

        if state.status != AgentStatus.COMPLETED:
            state.status = AgentStatus.FAILED
            state.error_message = f"Execution reached iteration limit of {state.max_iterations}"
            raise MaxIterationsReachedError(state.error_message)

        return state
