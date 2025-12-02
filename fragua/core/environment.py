"""Base environment class for Fragua, refactored with docstrings."""

from __future__ import annotations

from typing import Any, Dict, Optional, List, Type

from fragua.core.warehouse import Warehouse
from fragua.core.agent import Agent
from fragua.core.manager import WarehouseManager
from fragua.core.registry import Registry

from fragua import AGENT_CLASSES, PARAMS_CLASSES, FUNCTION_CLASSES, STYLE_CLASSES

from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class Environment:
    """Environment class for Fragua.

    Encapsulates all logic for warehouse, warehouse manager, agents, and registries.
    Provides methods for creation, retrieval, updating, and deletion of all components.
    """

    REGISTRY_TYPES: List[str] = ["params", "functions", "styles", "agents"]

    def __init__(self, name: str, env_type: str = "env", fg_reg: bool = False):
        """
        Initialize the environment.

        Args:
            name: Name of the environment.
            env_type: Type of the environment.
            fg_reg: If True, populate default Fragua registries (params, functions, styles).
        """
        self.name = name
        self.env_type = env_type
        self.fg_reg = fg_reg
        self.warehouse = self._initialize_warehouse()
        self.manager = self._initialize_manager()
        self.agents = self._initialize_agents()
        self.params = self._initialize_params()
        self.functions = self._initialize_functions()
        self.styles = self._initialize_styles()
        logger.debug(
            "Environment '%s' initialized (type=%s).", self.name, self.env_type
        )

    # ---------------------- Initializers ---------------------- #
    def _initialize_params(self) -> Registry:
        """Initialize the environment params class."""
        params = Registry("params")

        logger.info("Default params initialized for environment '%s'.", self.name)
        return params

    def _initialize_functions(self) -> Registry:
        """Initialize the environment functions class."""

        functions = Registry("functions")

        logger.info("Default functions initialized for environment '%s'.", self.name)
        return functions

    def _initialize_styles(self) -> Registry:
        """Initialize the environment styles class."""
        styles = Registry("styles")

        logger.info("Default styles initialized for environment '%s'.", self.name)
        return styles

    def _initialize_agents(self) -> Registry:
        """Initialize the environment agents."""
        agents = Registry("agents")

        logger.info("Default agents initialized for environment '%s'.", self.name)
        return agents

    def _initialize_manager(self) -> WarehouseManager:
        """Initialize warehouse manager for environment."""
        manager = WarehouseManager(f"{self.name}_manager", self.warehouse)

        logger.info(
            "Default warehouse manager initialized for environment '%s'.", self.name
        )
        return manager

    def _initialize_warehouse(self) -> Warehouse:
        """Initialize warehouse for environment."""
        warehouse = Warehouse(f"{self.name}_warehouse")

        logger.info("Default warehouse initialized for environment '%s'.", self.name)
        return warehouse

    # ---------------------- Registry Management ---------------------- #
    def add_params(
        self,
    ) -> None:
        """fill the environment params."""
        self.params.set_entries(PARAMS_CLASSES)
        logger.info("Default params initialized for environment '%s'.", self.name)

    def add_styles(
        self,
    ) -> None:
        """fill the environment styles."""

        self.styles.set_entries(STYLE_CLASSES)
        logger.info("Default styles initialized for environment '%s'.", self.name)

    def add_functions(
        self,
    ) -> None:
        """fill the environment function."""
        self.functions.set_entries(FUNCTION_CLASSES)
        logger.info("Default function initialized for environment '%s'.", self.name)

    def add_registries(
        self,
    ) -> None:
        """fill the environment registries."""
        if self.fg_reg:
            self.add_functions()
            self.add_params()
            self.add_styles()
            logger.info(
                "Default registries initialized for environment '%s'.", self.name
            )

    # ---------------------- Agent Management ---------------------- #
    def create_agent(
        self,
        agent_name: str,
        action: str,
    ) -> bool:
        """
        Create and register an agent in agent registry.
        Returns a boolean value indicating whether the agent was created successfully or not.
        """

        action = action.lower()

        new_agent = AGENT_CLASSES[action](agent_name, environment=self)
        created = self.agents.create_entrie(action, agent_name, new_agent)

        if created:
            logger.info(
                "Agent created: %s (%s)", agent_name, new_agent.__class__.__name__
            )

        return created

    def get_agent(self, agent_name: str, action: str) -> Optional[Type[Agent[Any]]]:
        """Retrieve an agent from agent registry by name and action."""
        agent = self.agents.get_entrie(action, agent_name)
        return agent

    def delete_agent(self, agent_name: str, action: str) -> bool:
        """
        Remove an agent from agent registry.
        Returns a boolean value indicating whether the agent was deleted successfully or not.
        """

        action = action.lower()
        deleted = self._check_action_type(action)
        if deleted:
            self.agents.delete_entrie(action, agent_name)
            logger.info("Agent deleted: %s (%s)", agent_name, action)
        return deleted

    def update_agent(
        self,
        agent_name: str,
        new_name: Optional[str] = None,
    ) -> Agent[Any]:
        """
        Update an existing agent inside of agents registry.
        Returns a boolean value indicating whether the agent was updated successfully or not.
        """


        agent = self.get_agent(agent_name)
        if agent is None:
            raise ValueError(f"Agent '{agent_name}' not found.")

        # ---------------------- Update Name ---------------------- #
        if new_name and new_name != agent_name:
            self._check_duplicate_name(new_name)
            setattr(agent, "name", new_name)
            logger.info("Agent renamed: %s → %s", agent_name, new_name)

        return agent

    # ---------------------- Create Helpers ---------------------- #
    def create_extractor(self, name: str) -> bool:
        """Shortcut to create an Extractor agent."""
        return self.create_agent(name, "extract")

    def create_transformer(self, name: str) -> bool:
        """Shortcut to create a Transformer agent."""
        return self.create_agent(name, "transform")

    def create_loader(self, name: str) -> bool:
        """Shortcut to create a Loader agent."""
        return self.create_agent(name, "load")

    # ---------------------- Summary ---------------------- #

    def summary(self) -> Dict[str, Any]:
        """
        Return a JSON-serializable summary of the Environment instance,
        including metadata, components, agents and registries.
        """

        def serialize_registry(reg: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
            """Convert registry class references into JSON-safe values."""
            clean: Dict[str, Any] = {}
            for category, items in reg.items():
                clean[category] = {
                    name: getattr(cls, "__name__", str(cls))
                    for name, cls in items.items()
                }
            return clean

        not_init = "Not initialized."

        warehouse = self.warehouse
        warehouse_summary = not_init if warehouse is None else warehouse.summary()

        manager = self.manager
        manager_summary = not_init if manager is None else manager.summary()

        agents = self.agents
        agents_summaries = not_init if agents is {} else serialize_registry(agents)

        params = self.params
        params_summaries = not_init if params is None else serialize_registry(params)

        functions = self.functions
        functions_summaries = (
            not_init if functions is None else serialize_registry(functions)
        )
        styles = self.styles
        styles_summaries = not_init if styles is None else serialize_registry(styles)

        return {
            "meta": {
                "class": type(self).__name__,
                "module": type(self).__module__,
            },
            "name": self.name,
            "type": self.env_type,
            "fg_reg": self.fg_reg,
            "warehouse": warehouse_summary,
            "manager": manager_summary,
            "agents": agents_summaries,
            "params": params_summaries,
            "functions": functions_summaries,
            "styles": styles_summaries,
        }

    def __repr__(self) -> str:
        agent_count = sum(len(lst) for lst in self.components["agents"].values())
        return f"<Environment name={self.name!r} type={self.env_type!r} agents={agent_count}>"
