"""Base environment class for Fragua, refactored with docstrings."""

from __future__ import annotations

from typing import Any, Dict, List, Type, cast

from fragua.core.agent import Agent
from fragua.core.component import FraguaComponent
from fragua.core.section_registry import SectionRegistry
from fragua.core.warehouse import Warehouse
from fragua.core.manager import WarehouseManager


from fragua.extract import Extractor, ExtractRegistry
from fragua.extract.params.base import ExtractParams


from fragua.load import Loader, LoadRegistry
from fragua.load.params.base import LoadParams

from fragua.transform import Transformer, TransformRegistry
from fragua.transform.params.base import TransformParams

from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class Environment(FraguaComponent):
    """Environment class for Fragua.

    Encapsulates all logic for warehouse, warehouse manager, agents, and registries.
    Provides methods for creation, retrieval, updating, and deletion of all components.
    """

    REGISTRY_TYPES: List[str] = ["params", "functions", "styles", "agents"]
    AGENT_TYPES: Dict[str, Type[Agent[Any]]] = {
        "extract": Extractor,
        "transform": Transformer,
        "load": Loader,
    }

    def __init__(self, env_name: str, env_type: str = "base", fg_reg: bool = False):
        """
        Initialize the environment.

        Args:
            name: Name of the environment.
            env_type: Type of the environment.
            fg_reg: If True, populate default Fragua registries (params, functions, styles).
        """
        super().__init__(component_name=env_name)
        self.env_type = env_type
        self.fg_reg = fg_reg
        self.warehouse = self._initialize_warehouse()
        self.manager = self._initialize_manager()
        self.extract = self._initialize_extract_registry()
        self.transform = self._initialize_transform_registry()
        self.load = self._initialize_load_registry()

        logger.debug(
            "Environment '%s' initialized (type=%s).", self.name, self.env_type
        )

    def build_config(
        self, action: str | None = None, registry: str | None = None
    ) -> Any:
        """Retrive config for components management."""

        config: Dict[str, Dict[str, SectionRegistry]] = {
            "extract": {
                "agents": self.extract.agents,
                "params": self.extract.params,
                "styles": self.extract.styles,
                "functions": self.extract.functions,
            },
            "transform": {
                "agents": self.transform.agents,
                "params": self.transform.params,
                "styles": self.transform.styles,
                "functions": self.transform.functions,
            },
            "load": {
                "agents": self.load.agents,
                "params": self.load.params,
                "styles": self.load.styles,
                "functions": self.load.functions,
            },
        }

        if action and registry:
            return config[action][registry]

        if action and not registry:
            return config[action]

        if not action and registry:
            return {act: registry for act, registry in config.items()}

        return config

    # ---------------------- Error Handle ---------------------- #
    def agent_not_found(self, agent_name: str) -> ValueError:
        """Retrive a value error if for"""
        return ValueError(f"Not agent named {agent_name} found in registry.")

    # ---------------------- Initializers ---------------------- #
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

    def _initialize_extract_registry(self) -> ExtractRegistry:
        """"""
        reg_name = "extract"
        extract_registry = ExtractRegistry(reg_name)

        return extract_registry

    def _initialize_transform_registry(self) -> TransformRegistry:
        """"""
        reg_name = "transform"
        transform_registry = TransformRegistry(reg_name)

        return transform_registry

    def _initialize_load_registry(self) -> LoadRegistry:
        """"""
        reg_name = "load"
        load_registry = LoadRegistry(reg_name)

        return load_registry

    # ---------------------- Create Helpers ---------------------- #
    def _create_agent(self, action: str, agent_name: str) -> bool:
        """Retrive an agent by an given name."""
        registry = "agents"
        config = self.build_config(registry=registry)

        new_agent = self.AGENT_TYPES[action](agent_name, self)
        created = config[action][registry].create_one(agent_name, new_agent)

        if created:
            logger.info(
                "Agent created: %s (%s)", agent_name, new_agent.__class__.__name__
            )
        return created

    def create_extractor(self, agent_name: str) -> bool:
        """Shortcut to create an Extractor agent."""
        return self._create_agent("extract", agent_name)

    def create_transformer(self, agent_name: str) -> bool:
        """Shortcut to create a Transformer agent."""
        return self._create_agent("transform", agent_name)

    def create_loader(self, agent_name: str) -> bool:
        """Shortcut to create a Loader agent."""
        return self._create_agent("load", agent_name)

    # ---------------------- Get Helpers ---------------------- #
    def _get_agent(self, action: str, agent_name: str | None = None) -> Agent[Any]:
        """Retrive a agent by a given action and name."""
        config = self.build_config(registry="agents")

        if agent_name is None:
            first_agent = next(iter(config[action]["agents"].get_all().values()))
            agent = first_agent
        else:
            agent = config[action]["agents"].get_one(agent_name)

            if agent is None:
                raise self.agent_not_found(agent_name)

        return cast(Agent, agent)

    def get_extractor(self, agent_name: str | None = None) -> Extractor[ExtractParams]:
        """
        Retrive an extractor agent by a given name.
        If no name is given retrive the first extractor in the registry.

        """
        agent = self._get_agent("extract", agent_name)

        return cast(Extractor, agent)

    def get_transformer(
        self, agent_name: str | None = None
    ) -> Transformer[TransformParams]:
        """
        Retrive an extractor agent by a given name.
        If no name is given retrive the first extractor in the registry.

        """
        agent = self._get_agent("transform", agent_name)

        return cast(Transformer, agent)

    def get_loader(self, agent_name: str | None = None) -> Loader[LoadParams]:
        """
        Retrive an extractor agent by a given name.
        If no name is given retrive the first extractor in the registry.

        """
        agent = self._get_agent("load", agent_name)

        return cast(Loader, agent)

    # ---------------------- Summary ---------------------- #

    def summary(self) -> Dict[str, Any]:
        """
        Summary of the Environment instance,
        including summaries from all entities(Manager, Agents, Params, Styles, Functions).
        """

        return {
            "env_name": self.name,
            "env_type": self.env_type,
            "warehouse": self.warehouse.summary(),
            "manager": self.manager.summary(),
            "extract": self.extract.summary(),
            "transform": self.transform.summary(),
            "load": self.load.summary(),
        }

    def __repr__(self) -> str:
        return f"<Environment name={self.name!r} type={self.env_type!r}>"
