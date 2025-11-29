"""Base environment class for Fragua, refactored with docstrings."""

from __future__ import annotations
from typing import Any, Dict, Optional, Type, List, TypedDict, cast

from fragua.core import (
    Params,
    Style,
    FraguaFunction,
    Warehouse,
    Agent,
    WarehouseManager,
)

from fragua.extract import (
    Extractor,
    EXTRACT_PARAMS_CLASSES,
    EXTRACT_FUNCTION_CLASSES,
    EXTRACT_STYLE_CLASSES,
)

from fragua.transform import (
    Transformer,
    TRANSFORM_PARAMS_CLASSES,
    TRANSFORM_FUNCTION_CLASSES,
    TRANSFORM_STYLE_CLASSES,
)

from fragua.load import (
    Loader,
    LOAD_PARAMS_CLASSES,
    LOAD_FUNCTION_CLASSES,
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

    def _validate_registry_type(self, registry_type: str) -> bool:
        """Check if the registry type is valid."""
        return registry_type in self.REGISTRY_TYPES

    def _validate_record_name(
        self, registry: Dict[str, Any], registry_name: str
    ) -> bool:
        """Check if record name is in the registry."""
        return registry_name in registry

    def _validate_record(
        self,
        registry_type: str,
        registry_name: str,
        not_exist_name: bool = False,
    ) -> bool:
        """Check if a registry is valid."""

        registry = self.registries[registry_type]
        exist_name = self._validate_record_name(registry, registry_name)

        is_valid_type = self._validate_registry_type(registry_type)
        is_valid_name = exist_name if not_exist_name else not exist_name

        is_valid_registry = is_valid_type == is_valid_name

        return is_valid_registry

    # ---------------------- Registry Management ---------------------- #
    def create_registry_record(
        self, registry_type: str, name: str, data: Dict[str, Any]
    ) -> bool:
        """
        Create a new record in a registry.
        Return boolean if record is created succesfully or not.
        """
        created = (
            True
            if self._validate_registry_type(registry_type)
            and not self._validate_registry_name(self.registries[registry_type], name)
            else False
        )

        if created:
            self.registries[registry_type] = data
            logger.info("%s created: %s", registry_type.capitalize(), name)

        return created

    def get_registry_record(
        self,
        registry_type: str,
        action: str,
        name: str,
    ) -> Any | None:
        """Retrieve a record from a registry by name."""

        record = (
            self.registries[registry_type][action].get(name)
            if self._validate_registry_type(registry_type)
            and self._validate_registry_name(
                self.registries[registry_type][action], name
            )
            else None
        )

        return record

    def update_registry_record(
        self, registry_type: str, action: str, name: str, data: Dict[str, Any]
    ) -> bool:
        """
        Update an existing record in a registry.
        Return boolean if record is created succesfully or not.
        """

        updated = self._validate_record(registry_type, name)

        if updated:
            self.registries[registry_type][action].update(data)
            logger.info("%s updated: %s", registry_type.capitalize(), name)

        return updated

    def delete_registry_record(
        self, registry_type: str, action: str, name: str
    ) -> bool:
        """
        Delete a record from a registry by name.
        Return boolean if record is created succesfully or not.
        """

        deleted = self._validate_record(registry_type, name)

        if deleted:
            self.registries[registry_type][action].pop(name)
            logger.info("%s deleted: %s", registry_type.capitalize(), name)

        return deleted

    def list_registry_records(self, registry_type: str) -> Dict[str, Any]:
        """List all records in a registry."""

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
        return cast(Extractor, self.create_agent("extractor", name))

    def create_transformer(self, name: Optional[str] = None) -> Transformer:
        """Shortcut to create a Transformer agent."""
        return cast(Transformer, self.create_agent("transformer", name))

    def create_loader(self, name: Optional[str] = None) -> Loader:
        """Shortcut to create a Loader agent."""
        return cast(Loader, self.create_agent("loader", name))

    # ---------------------- Get Helpers ---------------------- #
    def get_warehouse(self) -> Warehouse | None:
        """Return the warehouse instance."""
        wh = self.components["warehouse"]
        return wh

    def get_manager(self) -> WarehouseManager | None:
        """Return the warehouse manager instance."""
        mgr = self.components["manager"]
        return mgr

    def get_agents(self, agent_type: Optional[str] = None) -> List[Any]:
        """Return all agents, or agents of a given type."""
        if agent_type is None:
            return [a for agents in self.components["agents"].values() for a in agents]
        if agent_type not in self.AGENT_CLASSES:
            raise ValueError(f"Invalid agent type '{agent_type}'.")
        return cast(List[Any], self.components["agents"][agent_type])

    def get_params(self) -> Dict[str, Any]:
        """Return list of params of the environment"""
        return self.list_registry_records("params")

    def get_functions(self) -> Dict[str, Any]:
        """Return list of functions of the environment"""
        return self.list_registry_records("functions")

    def get_styles(self) -> Dict[str, Any]:
        """Return list of styles of the environment"""
        return self.list_registry_records("styles")

    def get_one_params(self, action: str, name: str) -> type[Params]:
        """Return a params class by an given name from the params registry."""
        return cast(type[Params], self.get_registry_record("params", action, name))

    def get_one_function(self, action: str, name: str) -> type[FraguaFunction]:
        """Return a function class by an given name from the functions registry."""
        return cast(
            type[FraguaFunction], self.get_registry_record("functions", action, name)
        )

    def get_one_style(self, action: str, name: str) -> type[Style]:
        """Return a style class by an given name from the styles registry."""
        return cast(type[Style], self.get_registry_record("styles", action, name))

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

        not_init = "Not initialized."

        warehouse = self.get_warehouse()
        warehouse_summary = not_init if warehouse is None else warehouse.summary()

        manager = self.get_manager()
        manager_summary = not_init if manager is None else manager.summary()

        agents = serialize_agents(self.components["agents"])

        registries = (
            {
                rtype: serialize_registry(self.registries[rtype])
                for rtype in self.REGISTRY_TYPES
            },
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
                "agents": agents,
            },
            "registries": registries,
        }

    def __repr__(self) -> str:
        agent_count = sum(len(lst) for lst in self.components["agents"].values())
        return f"<Environment name={self.name!r} type={self.env_type!r} agents={agent_count}>"
