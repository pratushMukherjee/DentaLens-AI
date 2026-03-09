"""Registry of available agents mapped by type."""

from dentalens.domain.enums import AgentType, IntentType
from dentalens.services.agents.base_agent import BaseAgent


class AgentRegistry:
    """Maintains a registry of agent instances by type."""

    def __init__(self):
        self._agents: dict[AgentType, BaseAgent] = {}

    def register(self, agent_type: AgentType, agent: BaseAgent) -> None:
        """Register an agent instance for a given type."""
        self._agents[agent_type] = agent

    def get(self, agent_type: AgentType) -> BaseAgent:
        """Get an agent by type."""
        if agent_type not in self._agents:
            raise KeyError(f"No agent registered for type: {agent_type}")
        return self._agents[agent_type]

    def get_for_intent(self, intent: IntentType) -> BaseAgent | None:
        """Get the specialist agent that handles a given intent."""
        for agent in self._agents.values():
            if agent.can_handle(intent):
                return agent
        return None

    @property
    def registered_types(self) -> list[AgentType]:
        return list(self._agents.keys())
