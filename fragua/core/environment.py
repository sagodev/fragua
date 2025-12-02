"""Base environment class for Fragua, refactored with docstrings."""

from __future__ import annotations

from typing import Any, Dict, Optional, Type, List, cast

from fragua.core.warehouse import Warehouse
from fragua.core.agent import Agent
from fragua.core.manager import WarehouseManager
from fragua.core.style import Style
from fragua.core.function import FraguaFunction
from fragua.core.params import Params
from fragua.core.registry import Registry

from fragua.extract import Extractor

from fragua.transform import Transformer

from fragua.load import Loader

from fragua import AGENT_CLASSES, PARAMS_CLASSES, FUNCTION_CLASSES, STYLE_CLASSES

from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class EnvironmentComponents(TypedDict):
    """Components stored inside an environment."""

    agents: Dict[str, List[Agent[Any]]]


class Environment:
    """Environment class for Fragua.

    Encapsulates all logic for warehouse, warehouse manager, agents, and registries.
    Provides methods for creation, retrieval, updating, and deletion of all components.
    """

    AGENT_CLASSES: Dict[str, Type[Agent[Any]]] = {
        "extractor": Extractor,
        "transformer": Transformer,
        "loader": Loader,
    }
    REGISTRY_TYPES: List[str] = ["params", "functions", "styles"]

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
        self.components: EnvironmentComponents = {
            "agents": {atype: [] for atype in self.AGENT_CLASSES},
        }
        self.warehouse = self._initialize_warehouse()
        self.manager = self._initialize_manager()
        self.params = self._initialize_params()
        self.functions = self._initialize_functions()
        self.styles = self._initialize_styles()
        logger.debug(
            "Environment '%s' initialized (type=%s).", self.name, self.env_type
        )

    # ---------------------- Initializers ---------------------- #
    def _initialize_params(self) -> Registry:
        """Initialize the environment params class."""
        params = Registry("params", {atype: {} for atype in self.ACTION_TYPES})

        logger.info("Default params initialized for environment '%s'.", self.name)
        return params

    def _initialize_functions(self) -> Registry:
        """Initialize the environment functions class."""

        functions = Registry("functions", {atype: {} for atype in self.ACTION_TYPES})

        logger.info("Default functions initialized for environment '%s'.", self.name)
        return functions

    def _initialize_styles(self) -> Registry:
        """Initialize the environment styles class."""
        styles = Registry("styles", {atype: {} for atype in self.ACTION_TYPES})

        logger.info("Default styles initialized for environment '%s'.", self.name)
        return styles
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

    # ---------------------- Checkers ---------------------- #
    def _check_action_type(self, action: str) -> bool:
        """Check if the action type is valid."""
        return any(action in actions for actions in self.REGISTRY_TYPES)

    # ---------------------- Registry Management ---------------------- #
        self,


        exist_list = self._validate_registry_type(registry_type)

        if not exist_list:
            raise RuntimeError("Registry not found.")

        return self.registries[registry_type]

    # ---------------------- Agent Management ---------------------- #
    def create_agent(
        self,
        agent_type: str,
        name: Optional[str] = None,
    ) -> Agent[Any]:
        """Create and register an agent in the environment."""
        agent_type = agent_type.lower()
        if agent_type not in self.AGENT_CLASSES:
            raise ValueError(f"Unknown agent type '{agent_type}'.")

        agent_cls = self.AGENT_CLASSES[agent_type]
        agent_name = (
            name
            or f"{self.name}_{agent_type}_{len(self.components['agents'][agent_type])+1}"
        )
        self._check_duplicate_name(agent_name)
        agent = agent_cls(name=agent_name, environment=self)
        self.components["agents"][agent_type].append(agent)
        logger.info("Agent created: %s (%s)", agent_name, agent_cls.__name__)
        return agent

    def get_agent(self, agent_name: str) -> Optional[Agent[Any]]:
        """Retrieve an agent by name."""
        for agents in self.components["agents"].values():
            for agent in agents:
                if getattr(agent, "name", None) == agent_name:
                    return agent
        return None

    def delete_agent(self, agent_name: str) -> bool:
        """Remove an agent from the environment."""
        for atype, agents in self.components["agents"].items():
            for i, agent in enumerate(agents):
                if getattr(agent, "name", None) == agent_name:
                    agents.pop(i)
                    logger.info("Agent deleted: %s (%s)", agent_name, atype)
                    return True
        raise ValueError(f"Agent '{agent_name}' not found.")

    def update_agent(
        self,
        agent_name: str,
        new_name: Optional[str] = None,
    ) -> Agent[Any]:
        """
        Update an existing agent inside the environment.

        Args:
            agent_name: Current name of the agent to update.
            new_name: Optional new name for the agent.

        Returns:
            The updated Agent instance.

        Raises:
            ValueError: If agent is not found or new name conflicts with another component.
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

    # ---------------------- Properties ---------------------- #
    @property
    def agents(self) -> Dict[str, List[Type[Agent]]] | None:
        """Return all agents, or agents of a given type."""
        if agent_type is None:
            return [a for agents in self.components["agents"].values() for a in agents]
        if agent_type not in self.AGENT_CLASSES:
            raise ValueError(f"Invalid agent type '{agent_type}'.")
        return cast(List[Any], self.components["agents"][agent_type])
    # ---------------------- Create Helpers ---------------------- #
    def create_extractor(self, name: Optional[str] = None) -> Extractor:
        """Shortcut to create an Extractor agent."""
        return cast(Extractor, self.create_agent("extractor", name))

    def create_transformer(self, name: Optional[str] = None) -> Transformer:
        """Shortcut to create a Transformer agent."""
        return cast(Transformer, self.create_agent("transformer", name))

    def create_loader(self, name: Optional[str] = None) -> Loader:
        """Shortcut to create a Loader agent."""
        return cast(Loader, self.create_agent("loader", name))

    # ---------------------- Get Helpers ---------------------- #
    def get_one_params(self, action: str, name: str) -> Type[Params]:
        """Return a params class by an given name from the params registry."""
        return cast(Type[Params], self.get_registry_record("params", action, name))

    def get_one_function(self, action: str, name: str) -> Type[FraguaFunction]:
        """Return a function class by an given name from the functions registry."""
        return cast(
            Type[FraguaFunction], self.get_registry_record("functions", action, name)
        )

    def get_one_style(self, action: str, name: str) -> Type[Style]:
        """Return a style class by an given name from the styles registry."""
        return cast(Type[Style], self.get_registry_record("styles", action, name))

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

        agents = serialize_agents(self.components["agents"])

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
            "components": {
                "warehouse": warehouse_summary,
                "manager": manager_summary,
                "agents": agents,
            },
            "registries": registries,
            "params": params_summaries,
            "functions": functions_summaries,
            "styles": styles_summaries,
        }

    def __repr__(self) -> str:
        agent_count = sum(len(lst) for lst in self.components["agents"].values())
        return f"<Environment name={self.name!r} type={self.env_type!r} agents={agent_count}>"
