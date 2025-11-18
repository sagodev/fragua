"""Base environment class for Fragua, refactored with docstrings."""

from __future__ import annotations
from typing import Any, Dict, Optional, Type, List, TypedDict, cast
from fragua.storages.warehouse import Warehouse
from fragua.agents.agent import Agent
from fragua.agents.warehouse_manager import WarehouseManager
from fragua.agents.extractor import Extractor
from fragua.agents.transformer import Transformer
from fragua.agents.loader import Loader
from fragua.params import (
    EXTRACT_PARAMS_CLASSES,
    TRANSFORM_PARAMS_CLASSES,
    LOAD_PARAMS_CLASSES,
)
from fragua.functions import (
    EXTRACT_FUNCTION_CLASSES,
    TRANSFORM_FUNCTION_CLASSES,
    LOAD_FUNCTION_CLASSES,
)
from fragua.styles import (
    EXTRACT_STYLE_CLASSES,
    TRANSFORM_STYLE_CLASSES,
    LOAD_STYLE_CLASSES,
)
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class EnvironmentComponents(TypedDict):
    """Components stored inside an environment."""

    warehouse: Optional[Warehouse]
    manager: Optional[WarehouseManager]
    agents: Dict[str, List[Agent[Any]]]


class Environment:
    """Refactored base environment for Fragua.

    Manages warehouse, warehouse manager, agents, and registries.
    Provides methods for creation, retrieval, updating, and deletion of all components.
    """

    AGENT_CLASSES: Dict[str, Type[Agent[Any]]] = {
        "extractor": Extractor,
        "transformer": Transformer,
        "loader": Loader,
    }
    REGISTRY_TYPES: List[str] = ["params", "functions", "styles"]

    def __init__(self, name: str, env_type: str = "base", fg_reg: bool = False):
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
            "warehouse": None,
            "manager": None,
            "agents": {atype: [] for atype in self.AGENT_CLASSES},
        }
        self.registries = self._initialize_registries()
        logger.debug(
            "Environment '%s' initialized (type=%s).", self.name, self.env_type
        )

    # ---------------------- Internal Helpers ---------------------- #
    def _check_duplicate_name(self, name: str) -> None:
        """Ensure no warehouse, manager, or agent already has the given name."""
        wh = self.components["warehouse"]
        mgr = self.components["manager"]
        if (wh and getattr(wh, "name", None) == name) or (
            mgr and getattr(mgr, "name", None) == name
        ):
            raise ValueError(f"Duplicate name '{name}' already exists in environment.")
        for agents in self.components["agents"].values():
            if any(getattr(a, "name", None) == name for a in agents):
                raise ValueError(f"Duplicate agent name detected: '{name}'.")

    def _initialize_registries(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Initialize the environment registries for params, functions, and styles."""
        registries: Dict[str, Dict[str, Dict[str, Any]]] = {
            rtype: {atype: {} for atype in ["extract", "transform", "load"]}
            for rtype in self.REGISTRY_TYPES
        }
        if self.fg_reg:
            registries["params"].update(
                {
                    "extract": EXTRACT_PARAMS_CLASSES,
                    "transform": TRANSFORM_PARAMS_CLASSES,
                    "load": LOAD_PARAMS_CLASSES,
                }
            )
            registries["functions"].update(
                {
                    "extract": EXTRACT_FUNCTION_CLASSES,
                    "transform": TRANSFORM_FUNCTION_CLASSES,
                    "load": LOAD_FUNCTION_CLASSES,
                }
            )
            registries["styles"].update(
                {
                    "extract": EXTRACT_STYLE_CLASSES,
                    "transform": TRANSFORM_STYLE_CLASSES,
                    "load": LOAD_STYLE_CLASSES,
                }
            )
        logger.info("Default registries initialized for environment '%s'.", self.name)
        return registries

    def _validate_registry_type(self, registry_type: str) -> None:
        """Check if the registry type is valid."""
        if registry_type not in self.REGISTRY_TYPES:
            raise ValueError(f"Invalid registry type '{registry_type}'.")

    # ---------------------- Registry Management ---------------------- #
    def create_registry_record(
        self, registry_type: str, name: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a new record in a registry."""
        self._validate_registry_type(registry_type)
        registry = self.registries[registry_type]
        if name in registry:
            raise ValueError(f"Record '{name}' already exists in {registry_type}.")
        registry[name] = data
        logger.info("%s created: %s", registry_type.capitalize(), name)
        return {name: data}

    def get_registry_record(
        self, registry_type: str, name: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve a record from a registry by name."""
        self._validate_registry_type(registry_type)
        return self.registries[registry_type].get(name)

    def update_registry_record(
        self, registry_type: str, name: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing record in a registry."""
        self._validate_registry_type(registry_type)
        registry = self.registries[registry_type]
        if name not in registry:
            raise ValueError(f"Record '{name}' not found in {registry_type}.")
        registry[name].update(data)
        logger.info("%s updated: %s", registry_type.capitalize(), name)
        return {name: registry[name]}

    def delete_registry_record(self, registry_type: str, name: str) -> bool:
        """Delete a record from a registry by name."""
        self._validate_registry_type(registry_type)
        registry = self.registries[registry_type]
        if name not in registry:
            raise ValueError(f"Record '{name}' not found in {registry_type}.")
        del registry[name]
        logger.info("%s deleted: %s", registry_type.capitalize(), name)
        return True

    def list_registry_records(self, registry_type: str) -> Dict[str, Any]:
        """List all records in a registry."""
        self._validate_registry_type(registry_type)
        return self.registries[registry_type]

    # ---------------------- Agent Management ---------------------- #
    def create_agent(
        self,
        agent_type: str,
        name: Optional[str] = None,
        environment: Optional[Environment] = None,
    ) -> Agent[Any]:
        """Create and register an agent in the environment."""
        agent_type = agent_type.lower()
        if agent_type not in self.AGENT_CLASSES:
            raise ValueError(f"Unknown agent type '{agent_type}'.")
        if environment is None:
            raise TypeError("Environment instance required.")
        agent_cls = self.AGENT_CLASSES[agent_type]
        agent_name = (
            name
            or f"{self.name}_{agent_type}_{len(self.components['agents'][agent_type])+1}"
        )
        self._check_duplicate_name(agent_name)
        agent = agent_cls(name=agent_name, environment=environment)
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

    # ---------------------- Warehouse & Manager ---------------------- #
    def create_warehouse(self, name: Optional[str] = None) -> Warehouse:
        """Create the warehouse for the environment (only one allowed)."""
        if self.components["warehouse"] is not None:
            raise RuntimeError("Warehouse already exists.")
        wh_name = name or f"{self.name}_warehouse"
        self._check_duplicate_name(wh_name)
        warehouse = Warehouse(wh_name)
        self.components["warehouse"] = warehouse
        logger.info("Warehouse created: %s", wh_name)
        return warehouse

    def create_manager(
        self, name: Optional[str] = None, warehouse: Optional[Warehouse] = None
    ) -> WarehouseManager:
        """Create the warehouse manager (only one allowed)."""
        if self.components["manager"] is not None:
            raise RuntimeError("WarehouseManager already exists.")
        warehouse = warehouse or self.components["warehouse"] or self.create_warehouse()
        mgr_name = name or f"{self.name}_manager"
        self._check_duplicate_name(mgr_name)
        manager = WarehouseManager(mgr_name, warehouse)
        self.components["manager"] = manager
        logger.info("WarehouseManager created: %s", mgr_name)
        return manager

    # ---------------------- Shortcuts ---------------------- #
    def create_extractor(self, name: Optional[str] = None) -> Extractor:
        """Shortcut to create an Extractor agent."""
        return cast(Extractor, self.create_agent("extractor", name, environment=self))

    def create_transformer(self, name: Optional[str] = None) -> Transformer:
        """Shortcut to create a Transformer agent."""
        return cast(
            Transformer, self.create_agent("transformer", name, environment=self)
        )

    def create_loader(self, name: Optional[str] = None) -> Loader:
        """Shortcut to create a Loader agent."""
        return cast(Loader, self.create_agent("loader", name, environment=self))

    # ---------------------- Get Helpers ---------------------- #
    def warehouse(self) -> Warehouse:
        """Return the warehouse instance."""
        wh = self.components["warehouse"]
        if not wh:
            raise RuntimeError("Warehouse not initialized.")
        return wh

    def manager(self) -> WarehouseManager:
        """Return the warehouse manager instance."""
        mgr = self.components["manager"]
        if not mgr:
            raise RuntimeError("WarehouseManager not initialized.")
        return mgr

    def agents(self, agent_type: Optional[str] = None) -> List[Any]:
        """Return all agents, or agents of a given type."""
        if agent_type is None:
            return [a for agents in self.components["agents"].values() for a in agents]
        if agent_type not in self.AGENT_CLASSES:
            raise ValueError(f"Invalid agent type '{agent_type}'.")
        return cast(List[Any], self.components["agents"][agent_type])

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

        def serialize_agents(agent_dict: Dict[str, List[Agent[Any]]]) -> Dict[str, Any]:
            """Serialize all agents by calling agent.summary() if available."""
            output: Dict[str, Any] = {}
            for atype, agents in agent_dict.items():
                output[atype] = [
                    a.summary() if hasattr(a, "summary") else {"name": a.name}
                    for a in agents
                ]
            return output

        # Warehouse
        warehouse = self.components["warehouse"]
        warehouse_summary = (
            warehouse.summary() if warehouse and hasattr(warehouse, "summary") else None
        )

        # Manager
        manager = self.components["manager"]
        manager_summary = (
            manager.summary() if manager and hasattr(manager, "summary") else None
        )

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
                "agents": serialize_agents(self.components["agents"]),
            },
            "registries": {
                rtype: serialize_registry(self.registries[rtype])
                for rtype in self.REGISTRY_TYPES
            },
        }

    def __repr__(self) -> str:
        agent_count = sum(len(lst) for lst in self.components["agents"].values())
        return f"<Environment name={self.name!r} type={self.env_type!r} agents={agent_count}>"
