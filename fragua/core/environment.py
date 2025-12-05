"""Base environment class for Fragua, refactored with docstrings."""

from __future__ import annotations

from typing import Any, Dict, Optional, List, Type, cast

from fragua.core.params import Params
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


from fragua.extract.params.base import ExtractParams
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

from fragua.transform.params.base import TransformParams
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

    # ---------------------- Error Handle ---------------------- #
    def agent_not_found(self, agent_name: str) -> ValueError:
        """Retrive a value error if for"""
        return ValueError(f"Not agent named {agent_name} found in registry.")

    # ---------------------- Initializers ---------------------- #
    def _initialize_params(self) -> Registry:
        """Initialize the environment params class."""

        params = Registry("params")

        if self.fg_reg:
            fg_params = {}

            class_groups = {
                "extract": EXTRACT_PARAMS_CLASSES,
                "transform": TRANSFORM_PARAMS_CLASSES,
                "load": LOAD_PARAMS_CLASSES,
            }

            for action, classes in class_groups.items():
                fg_params[action] = {
                    name: cls(action, name) for name, cls in classes.items()
                }

            params = Registry("params", fg_params)

        msg = (
            "Environment params set with Fragua params. '%s'."
            if self.fg_reg
            else "Default params initialized for environment '%s'."
        )
        logger.info(msg, self.name)
        return params

    def _initialize_functions(self) -> Registry:
        """Initialize the environment functions class."""

        functions = Registry("functions")
        if self.fg_reg:
            fg_functions = {}

            class_groups = {
                "extract": EXTRACT_FUNCTION_CLASSES,
                "transform": TRANSFORM_FUNCTION_CLASSES,
                "load": LOAD_FUNCTION_CLASSES,
            }

            for action, classes in class_groups.items():
                fg_functions[action] = {}

                for name, cls in classes.items():
                    params_inst = self.params.get_entrie(name, action)
                    instance = cls(name, params_inst)
                    fg_functions[action][name] = instance

            functions = Registry("functions", fg_functions)

        msg = (
            "Environment functions set with Fragua functions. '%s'."
            if self.fg_reg
            else "Default functions initialized for environment '%s'."
        )
        logger.info(msg, self.name)
        return functions

    def _initialize_styles(self) -> Registry:
        """Initialize the environment styles class."""

        styles = Registry("styles")

        if self.fg_reg:
            fg_styles = {}

            class_groups = {
                "extract": EXTRACT_STYLE_CLASSES,
                "transform": TRANSFORM_STYLE_CLASSES,
                "load": LOAD_STYLE_CLASSES,
            }

            for action, classes in class_groups.items():
                fg_styles[action] = {name: cls(name) for name, cls in classes.items()}

            styles = Registry("styles", fg_styles)

        msg = (
            "Environment styles set with Fragua styles. '%s'."
            if self.fg_reg
            else "Default styles initialized for environment '%s'."
        )
        logger.info(msg, self.name)
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

    # ---------------------- Agent Management ---------------------- #
    def create_agent(
        self,
        agent_name: str,
        action: str,
    ) -> bool:
        """
        Create and register an agent in the agent registry.
        Action IS required because we need to know which subclass to instantiate.
        """

        agent_classes: Dict[str, Type[Agent]] = {
            "extract": Extractor,
            "transform": Transformer,
            "load": Loader,
        }

        action = action.lower()

        if action not in ACTION_TYPES:
            logger.error("Invalid agent action type: %s", action)
            return False

        new_agent = agent_classes[action](agent_name, environment=self)
        created = self.agents.create_entrie(action, agent_name, new_agent)

        if created:
            logger.info(
                "Agent created: %s (%s)", agent_name, new_agent.__class__.__name__
            )

        return created

    def _get_agent(
        self,
        agent_name: str,
        action: Optional[str] = None,
    ) -> Type[Agent[Params]] | None:
        """Retrieve an agent by name. If action is None, search in ALL actions."""

        agent = self.agents.get_entrie(agent_name, action)

        return agent

    def delete_agent(
        self,
        agent_name: str,
        action: Optional[str] = None,
    ) -> bool:
        """
        Remove an agent from registry.
        If action is None, attempts to locate agent automatically.
        """

        if action is None:
            entry = self.agents.get_entrie(agent_name, None)
            if entry is None:
                return False

            for act, entries in self.agents.get_entries("all").items():
                if agent_name in entries:
                    action = act
                    break

        deleted = self.agents.delete_entrie(action, agent_name)

        if deleted:
            logger.info("Agent deleted: %s (%s)", agent_name, action)

        return deleted

    def update_agent(
        self,
        agent_name: str,
        new_name: str,
        action: Optional[str] = None,
    ) -> bool:
        """
        Update an existing agent.
        If action is None, auto-detect which action the agent belongs to.
        """

        if action is None:
            entry = self.agents.get_entrie(agent_name, None)
            if entry is None:
                return False

            for act, entries in self.agents.get_entries("all").items():
                if agent_name in entries:
                    action = act
                    break

        updated = self.agents.update_entrie(action, agent_name, new_name)

        if updated:
            logger.info("Agent renamed: %s → %s", agent_name, new_name)

        return updated

    # ---------------------- Create Helpers ---------------------- #
    def create_extractor(self, agent_name: str) -> bool:
        """Shortcut to create an Extractor agent."""
        return self.create_agent(agent_name, "extract")

    def create_transformer(self, agent_name: str) -> bool:
        """Shortcut to create a Transformer agent."""
        return self.create_agent(agent_name, "transform")

    def create_loader(self, agent_name: str) -> bool:
        """Shortcut to create a Loader agent."""
        return self.create_agent(agent_name, "load")

    # ---------------------- Get Helpers ---------------------- #
    def get_extractor(self, agent_name: str | None = None) -> Extractor[ExtractParams]:
        """
        Retrive an extractor agent by a given name.
        If no name is given retrive the first extractor in the registry.

        """
        action: str = "extract"

        if agent_name is None:
            first_agent = next(iter(self.agents.get_entries(action).values()))
            agent = first_agent
        else:
            agent = self.agents.get_entrie(agent_name, action)

            if agent is None:
                raise self.agent_not_found(agent_name)

        return cast(Extractor, agent)

    def get_transformer(
        self, agent_name: str | None = None
    ) -> Transformer[TransformParams]:
        """
        Retrive an extractor agent by a given name.
        If no name is given retrive the first extractor in the registry.

        """
        action: str = "extract"
        if agent_name is None:
            first_agent = next(iter(self.agents.get_entries(action).values()))
            agent = first_agent
        else:
            agent = self.agents.get_entrie(agent_name, action)

            if agent is None:
                raise self.agent_not_found(agent_name)

        return cast(Transformer, agent)
    # ---------------------- Summary ---------------------- #
    @property
    def summary(self) -> Dict[str, Any]:
        """
        Return a JSON-serializable summary of the Environment instance,
        including summaries from all entities(Manager, Agents, Params, Styles, Functions).
        """

        def serialize_registry(registry: Registry):
            clean = {}

            for action in ACTION_TYPES:
                entries = registry.get_entries(action)
                if not entries:
                    continue

                clean[action] = {
                    name: instance.summary() for name, instance in entries.items()
                }

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
