"""Base environment class."""

from __future__ import annotations

from typing import Any, Dict, Optional, Type, List, cast


from fragua.storages.warehouse import Warehouse

from fragua.agents.agent import Agent
from fragua.agents.warehouse_manager import WarehouseManager
from fragua.agents.miner import Miner
from fragua.agents.blacksmith import Blacksmith
from fragua.agents.haulier import Haulier

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


class Environment:  # pylint: disable=too-many-public-methods
    """
    Base Environment for Fragua.

    Manages the lifecycle and registration of a single warehouse,
    a single warehouse manager, and multiple agents of different types.
    """

    AGENT_CLASSES: Dict[str, Type[Agent]] = {
        "miner": Miner,
        "blacksmith": Blacksmith,
        "haulier": Haulier,
    }

    REGISTRY_TYPES: List[str] = ["params", "functions", "styles"]

    def __init__(self, name: str, env_type: str = "base", fg_reg: bool = False):
        self.name = name
        self.env_type = env_type
        self.fg_reg = fg_reg
        self.components: Dict[str, Any] = {
            "warehouse": None,
            "manager": None,
            "agents": {atype: [] for atype in self.AGENT_CLASSES},
        }

        self.registries = self._initialize_registries()

        logger.debug(
            "Environment '%s' initialized (type=%s).", self.name, self.env_type
        )

    # ---------------------------------------------------------------------
    # INTERNAL VALIDATION
    # ---------------------------------------------------------------------

    def _check_duplicate_name(self, name: str) -> None:
        """Ensure no component with the given name already exists."""

        # Warehouse
        wh = self.components["warehouse"]
        if wh is not None and getattr(wh, "name", None) == name:
            raise ValueError(f"Duplicate name '{name}' already used for Warehouse.")

        # Manager
        mgr = self.components["manager"]
        if mgr is not None and getattr(mgr, "name", None) == name:
            raise ValueError(
                f"Duplicate name '{name}' already used for WarehouseManager."
            )

        # Agents
        for atype, agents in self.components["agents"].items():
            for agent in agents:
                if getattr(agent, "name", None) == name:
                    raise ValueError(
                        f"Duplicate agent name detected: '{name}' ({atype})."
                    )

    # ---------------------------------------------------------------------
    # REGISTRY INITIALIZATION
    # ---------------------------------------------------------------------

    def _initialize_registries(self) -> Dict[str, Dict[str, Dict[str, Any]]]:
        """Populate default registry entries for Params, Functions, and Styles."""

        registries: Dict[str, Dict[str, Dict[str, Any]]] = {
            "params": {
                "extract": {},
                "transform": {},
                "load": {},
            },
            "functions": {
                "extract": {},
                "transform": {},
                "load": {},
            },
            "styles": {
                "extract": {},
                "transform": {},
                "load": {},
            },
        }

        if self.fg_reg:

            registries["params"] = {
                "extract": {**EXTRACT_PARAMS_CLASSES},
                "transform": {**TRANSFORM_PARAMS_CLASSES},
                "load": {**LOAD_PARAMS_CLASSES},
            }

            registries["functions"] = {
                "extract": {**EXTRACT_FUNCTION_CLASSES},
                "transform": {**TRANSFORM_FUNCTION_CLASSES},
                "load": {**LOAD_FUNCTION_CLASSES},
            }
            registries["styles"] = {
                "extract": {**EXTRACT_STYLE_CLASSES},
                "transform": {**TRANSFORM_STYLE_CLASSES},
                "load": {**LOAD_STYLE_CLASSES},
            }

        logger.info("Default registries initialized for environment '%s'.", self.name)

        return registries

    # ---------------------------------------------------------------------
    # REGISTRY MANAGEMENT (CREATE, GET, UPDATE, DELETE)
    # ---------------------------------------------------------------------

    def _validate_registry_type(self, registry_type: str) -> None:
        """Validate that a given registry type is valid."""
        if registry_type not in self.REGISTRY_TYPES:
            raise ValueError(
                f"Invalid registry type '{registry_type}'. Must be one of {self.REGISTRY_TYPES}"
            )

    def create_registry_record(
        self, registry_type: str, name: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create and register a new record in the specified registry."""
        self._validate_registry_type(registry_type)
        registry = self.registries[registry_type]

        if name in registry:
            raise ValueError(
                f"Record '{name}' already exists in {registry_type} registry."
            )

        registry[name] = data
        logger.info("%s created: %s", registry_type.capitalize(), name)
        return {name: data}

    def get_registry_record(
        self, registry_type: str, name: str
    ) -> Optional[Dict[str, Any]]:
        """Retrieve a specific registry record by name."""
        self._validate_registry_type(registry_type)
        return self.registries[registry_type].get(name)

    def update_registry_record(
        self, registry_type: str, name: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing registry record."""
        self._validate_registry_type(registry_type)
        registry = self.registries[registry_type]

        if name not in registry:
            raise ValueError(f"Record '{name}' not found in {registry_type} registry.")

        registry[name].update(data)
        logger.info("%s updated: %s", registry_type.capitalize(), name)
        return {name: registry[name]}

    def delete_registry_record(self, registry_type: str, name: str) -> bool:
        """Delete a registry record by name."""
        self._validate_registry_type(registry_type)
        registry = self.registries[registry_type]

        if name not in registry:
            raise ValueError(f"Record '{name}' not found in {registry_type} registry.")

        del registry[name]
        logger.info("%s deleted: %s", registry_type.capitalize(), name)
        return True

    def list_registry_records(self, registry_type: str) -> Dict[str, Any]:
        """List all records in a given registry."""
        self._validate_registry_type(registry_type)
        return self.registries[registry_type]

    # ---------------------------------------------------------------------
    # AGENT MANAGEMENT (CREATE, GET, UPDATE, DELETE)
    # ---------------------------------------------------------------------

    def create_agent(
        self,
        agent_type: str,
        name: Optional[str] = None,
        environment: Optional[Environment] = None,
    ) -> Agent:
        """
        Create and register an agent within the given environment.

        Args:
            agent_type: One of 'miner', 'blacksmith', or 'haulier'.
            name: Optional name for the agent.
            environment: The environment instance this agent belongs to.
        """
        agent_type = agent_type.lower()

        if agent_type not in self.AGENT_CLASSES:
            raise ValueError(
                f"Unknown agent type '{agent_type}'. "
                f"Available: {list(self.AGENT_CLASSES.keys())}"
            )

        if environment is None:
            raise TypeError("An Environment instance is required to create an agent.")

        agent_cls = self.AGENT_CLASSES[agent_type]
        agent_name = (
            name
            or f"{self.name}_{agent_type}_{len(self.components['agents'][agent_type]) + 1}"
        )

        self._check_duplicate_name(agent_name)

        agent = agent_cls(name=agent_name, environment=environment)

        self.components["agents"][agent_type].append(agent)
        logger.info("Agent created: %s (%s)", agent_name, agent_cls.__name__)

        return agent

    def get_agent(self, agent_name: str) -> Optional[Agent]:
        """Return an agent by its name."""
        agents_dict = cast(Dict[str, List[Agent]], self.components["agents"])
        for agents in agents_dict.values():
            for agent in agents:
                if getattr(agent, "name", None) == agent_name:
                    return agent
        return None

    def update_agent(self, agent_name: str, **updates: Any) -> Agent:
        """
        Update attributes of an existing agent.
        Example: update_agent("miner_1", active=True)
        """
        agent = self.get_agent(agent_name)
        if not agent:
            raise ValueError(
                f"Agent '{agent_name}' not found in environment '{self.name}'."
            )

        for key, value in updates.items():
            if not hasattr(agent, key):
                raise AttributeError(f"Agent has no attribute '{key}'.")
            setattr(agent, key, value)

        logger.info("Agent updated: %s (%s)", agent_name, updates)
        return agent

    def delete_agent(self, agent_name: str) -> bool:
        """Remove an agent from this environment."""
        for atype, agents in self.components["agents"].items():
            for i, agent in enumerate(agents):
                if getattr(agent, "name", None) == agent_name:
                    agents.pop(i)
                    logger.info("Agent deleted: %s (%s)", agent_name, atype)
                    return True
        raise ValueError(
            f"Agent '{agent_name}' not found in environment '{self.name}'."
        )

    # ---------------------------------------------------------------------
    # CREATION HELPERS
    # ---------------------------------------------------------------------

    def create_warehouse(self, name: Optional[str] = None) -> Warehouse:
        """Create the warehouse (only one allowed per environment)."""
        if self.components["warehouse"] is not None:
            raise RuntimeError("A warehouse already exists in this environment.")

        wh_name = name or f"{self.name}_warehouse"
        self._check_duplicate_name(wh_name)

        warehouse = Warehouse(wh_name)
        self.components["warehouse"] = warehouse
        logger.info("Warehouse created: %s", wh_name)
        return warehouse

    def create_manager(
        self, name: Optional[str] = None, warehouse: Optional[Warehouse] = None
    ) -> WarehouseManager:
        """Create the warehouse manager (only one allowed per environment)."""

        if self.components["manager"] is not None:
            raise RuntimeError("A WarehouseManager already exists in this environment.")

        # Ensure warehouse exists
        if warehouse is None:
            warehouse = self.components["warehouse"] or self.create_warehouse()

        if warehouse is None:
            raise TypeError("A warehouse is required.")

        mgr_name = name or f"{self.name}_manager"
        self._check_duplicate_name(mgr_name)

        manager = WarehouseManager(mgr_name, warehouse)
        self.components["manager"] = manager
        logger.info("WarehouseManager created: %s", mgr_name)
        return manager

    def create_miner(self, name: Optional[str] = None) -> Miner:
        """Shortcut to create a Miner agent."""
        return cast(Miner, self.create_agent("miner", name, environment=self))

    def create_blacksmith(self, name: Optional[str] = None) -> Blacksmith:
        """Shortcut to create a Blacksmith agent."""
        return cast(Blacksmith, self.create_agent("blacksmith", name, environment=self))

    def create_haulier(self, name: Optional[str] = None) -> Haulier:
        """Shortcut to create a Haulier agent."""
        return cast(Haulier, self.create_agent("haulier", name, environment=self))

    # ---------------------------------------------------------------------
    # GET HELPERS
    # ---------------------------------------------------------------------

    def get_warehouse(self) -> Warehouse:
        """Return warehouse."""
        return self.components["warehouse"]

    def get_manager(self) -> WarehouseManager:
        """Return warehouse manager."""
        return self.components["manager"]

    def get_agents(self, agent_type: Optional[str] = None) -> List[Any]:
        """Return all agents or those of a given type."""
        if agent_type is None:
            return [a for agents in self.components["agents"].values() for a in agents]
        if agent_type not in self.AGENT_CLASSES:
            raise ValueError(f"Invalid agent type '{agent_type}'.")
        return cast(List[Any], self.components["agents"][agent_type])

    def get_miner(self, agent_name: str) -> Miner:
        """Return a miner agent by a given name."""
        return cast(
            Miner,
            self.get_agent(
                agent_name,
            ),
        )

    def get_blacksmith(self, agent_name: str) -> Blacksmith:
        """Return a blacksmith agent by a given name."""
        return cast(
            Blacksmith,
            self.get_agent(
                agent_name,
            ),
        )

    def get_haulier(self, agent_name: str) -> Haulier:
        """Return a haulier agent by a given name."""
        return cast(
            Haulier,
            self.get_agent(
                agent_name,
            ),
        )

    # ---------------------------------------------------------------------
    # SUMMARY
    # ---------------------------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        """Return a full summary of the environment including actual objects and metadata."""
        return {
            "name": self.name,
            "type": self.env_type,
            "fg_reg": self.fg_reg,
            "registries": self.registries,
            "components": {
                "warehouse": self.components.get("warehouse"),
                "manager": self.components.get("manager"),
                "agents": {
                    atype: list(agents)
                    for atype, agents in self.components["agents"].items()
                },
            },
        }

    def __repr__(self) -> str:
        agent_count = sum(len(lst) for lst in self.components["agents"].values())
        return f"<Environment name={self.name!r} type={self.env_type!r} agents={agent_count}>"
