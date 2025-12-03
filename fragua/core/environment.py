"""Base environment class for Fragua, refactored with docstrings."""

from __future__ import annotations

from typing import Any, Dict, Optional, List, Type

from fragua.core.warehouse import Warehouse
from fragua.core.agent import Agent
from fragua.core.manager import WarehouseManager
from fragua.core.registry import Registry, ACTION_TYPES


from fragua.extract import (
    Extractor,
    EXTRACT_FUNCTION_CLASSES,
    EXTRACT_PARAMS_CLASSES,
    EXTRACT_STYLE_CLASSES,
)


from fragua.load import (
    Loader,
    LOAD_FUNCTION_CLASSES,
    LOAD_PARAMS_CLASSES,
    LOAD_STYLE_CLASSES,
)

from fragua.transform import (
    Transformer,
    TRANSFORM_FUNCTION_CLASSES,
    TRANSFORM_PARAMS_CLASSES,
    TRANSFORM_STYLE_CLASSES,
)

from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class Environment:
    """Environment class for Fragua.

    Encapsulates all logic for warehouse, warehouse manager, agents, and registries.
    Provides methods for creation, retrieval, updating, and deletion of all components.
    """

    REGISTRY_TYPES: List[str] = ["params", "functions", "styles", "agents"]

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

    # ---------------------- Fragua Custom Registries ---------------------- #
    def add_fg_params(self) -> None:
        """Set the environment params registry with instances of Fragua params classes."""
        new_entries: Dict[str, Dict[str, Any]] = {}

        class_groups = {
            "extract": EXTRACT_PARAMS_CLASSES,
            "transform": TRANSFORM_PARAMS_CLASSES,
            "load": LOAD_PARAMS_CLASSES,
        }

        for action, classes in class_groups.items():
            new_entries[action] = {
                name: cls(action, name) for name, cls in classes.items()
            }

        self.params.set_entries(new_entries)
        logger.info("Environment params set with Fragua params. '%s'.", self.name)

    def add_fg_styles(self) -> None:
        """Set the environment styles registry with instances of Fragua style classes."""
        new_entries: Dict[str, Dict[str, Any]] = {}

        class_groups = {
            "extract": EXTRACT_STYLE_CLASSES,
            "transform": TRANSFORM_STYLE_CLASSES,
            "load": LOAD_STYLE_CLASSES,
        }

        for action, classes in class_groups.items():
            new_entries[action] = {name: cls(name) for name, cls in classes.items()}

        self.styles.set_entries(new_entries)
        logger.info("Environment styles set with Fragua styles. '%s'.", self.name)

    def add_fg_functions(self) -> None:
        """Set the environment functions registry with instances of Fragua function classes."""
        new_entries: Dict[str, Dict[str, Any]] = {}

        class_groups = {
            "extract": EXTRACT_FUNCTION_CLASSES,
            "transform": TRANSFORM_FUNCTION_CLASSES,
            "load": LOAD_FUNCTION_CLASSES,
        }

        for action, classes in class_groups.items():
            new_entries[action] = {}

            for name, cls in classes.items():

                params_instance = self.params.get_entrie(name, action)

                if params_instance is None:
                    raise ValueError(
                        f"Missing param '{name}' for function '{name}' in action '{action}'."
                    )

                instance = cls(name, params_instance)

                new_entries[action][name] = instance

        self.functions.set_entries(new_entries)
        logger.info("Environment functions set with Fragua functions. '%s'.", self.name)

    def add_fg_registries(
        self,
    ) -> None:
        """fill the environment registries."""
        if self.fg_reg:
            self.add_fg_params()
            self.add_fg_functions()
            self.add_fg_styles()
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

    def get_agent(
        self,
        agent_name: str,
        action: Optional[str] = None,
    ) -> Optional[Type[Agent[Any]]]:
        """Retrieve an agent by name. If action is None, search in ALL actions."""

        agent = self.agents.get_entrie(agent_name, action)
        return agent

    def delete_agent(self, agent_name: str, action: str) -> bool:
        """
        Remove an agent from agent registry.
        Returns a boolean value indicating whether the agent was deleted successfully or not.
        """

        action = action.lower()

        deleted = self.agents.delete_entrie(action, agent_name)

        if deleted:
            logger.info("Agent deleted: %s (%s)", agent_name, action)

        return deleted

    def update_agent(
        self,
        action: str,
        agent_name: str,
        new_name: str,
    ) -> bool:
        """
        Update an existing agent inside of agents registry.
        Returns a boolean value indicating whether the agent was updated successfully or not.
        """
        action = action.lower()

        updated = self.agents.update_entrie(action, agent_name, new_name)

        if updated:
            logger.info("Agent renamed: %s → %s", agent_name, new_name)

        return updated

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
    @property
    def summary(self) -> Dict[str, Any]:
        """
        Return a JSON-serializable summary of the Environment instance,
        including metadata, components, agents and registries.
        """

        def serialize_registry(registry: Registry):
            clean = {}

            for action, entries in registry.get_entries().items():
                clean[action] = {}

                for name, obj in entries.items():

                    # ----- PARAMS -----
                    if registry.name == "params":
                        instance = obj(action, name)

                    # ----- STYLES -----
                    elif registry.name == "styles":
                        instance = obj(name)

                    # ----- FUNCTIONS -----
                    elif registry.name == "functions":
                        params_cls = self.params.get_entrie(action, name)

                        if params_cls is None:
                            raise ValueError("")

                        params_instance = params_cls(action, name)
                        instance = obj(name, params_instance)

                    # ----- AGENTS -----
                    elif registry.name == "agents":
                        instance = obj

                    # ----- DEFAULT -----
                    else:
                        instance = obj()

                    clean[action][name] = instance.summary()

            return clean

        return {
            "env_name": self.name,
            "env_type": self.env_type,
            "warehouse": self.warehouse.summary(),
            "manager": self.manager.summary(),
            "params": serialize_registry(self.params),
            "functions": serialize_registry(self.functions),
            "styles": serialize_registry(self.styles),
            "agents": serialize_registry(self.agents),
        }

    def __repr__(self) -> str:
        return f"<Environment name={self.name!r} type={self.env_type!r}>"
