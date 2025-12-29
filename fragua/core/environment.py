"""Base environment class for Fragua, refactored with docstrings."""

from __future__ import annotations

from typing import Any, Dict, Literal, Type, overload

from fragua.core.agent import FraguaAgent
from fragua.core.sections import FraguaSections
from fragua.core.component import FraguaComponent
from fragua.core.registry import FraguaRegistry
from fragua.core.set import FraguaSet
from fragua.core.warehouse import FraguaWarehouse

from fragua.extract import Extractor
from fragua.transform import Transformer
from fragua.load import Loader


from fragua.utils.logger import get_logger
from fragua.utils.security.security_context import FraguaSecurityContext, FraguaToken
from fragua.utils.types.enums import ActionType, ComponentType

logger = get_logger(__name__)


class FraguaEnvironment(FraguaComponent):
    """
    Core environment abstraction for Fragua.

    This class represents the top-level orchestration layer of the framework.
    It encapsulates and coordinates all fundamental components, including
    the warehouse, warehouse, action registries, and agents.

    The Environment is responsible for initializing, exposing, and managing
    the lifecycle of all ETL-related components within a given execution context.
    """

    def __init__(self, env_name: str, fg_config: bool = False):
        """
        Initialize a Fragua execution environment.

        This constructor bootstraps all core components required for
        ETL operations, including the warehouse and
        the action registries (extract, transform, load).

        Args:
            env_name (str):
                Logical name of the environment instance.
            fg_config (bool):
                Enables the default Fragua configuration.
                When True, built-in components such as
                functions and agents are automatically registered.
        """

        super().__init__(instance_name=env_name)
        self.fg_config = fg_config
        self.security = FraguaSecurityContext(env_name)
        self.warehouse = self._initialize_warehouse()
        self.sections = self._initialize_actions()

        logger.debug("Environment '%s' initialized.", self.name)

    # -------------------- Internal helpers -------------------- #
    def _token(self, *, kind: str, name: str) -> FraguaToken:
        return self.security.issue_token(
            component_kind=kind,
            component_name=name,
        )

    # ---------------------- Error Handle ---------------------- #
    def agent_not_found(self) -> ValueError:
        """
        Generate a standardized error for missing agents.

        Returns:
            ValueError:
                Exception indicating that the requested agent
                does not exist within the current environment.
        """

        return ValueError("Agent not found.")

    # ---------------------- Initializers ---------------------- #
    def _initialize_warehouse(self) -> FraguaWarehouse:
        """
        Initialize the warehouse for the environment.

        The warehouse serves as the central data container where
        intermediate and final datasets are stored during
        extract, transform, and load operations.

        Returns:
            FraguaWarehouse:
                Initialized warehouse instance bound to this environment.
        """

        warehouse = FraguaWarehouse(f"{self.name}_warehouse", self)

        logger.info("Default warehouse initialized for environment '%s'.", self.name)
        return warehouse

    def _initialize_actions(self) -> FraguaSections:
        """
        Initialize action registries for the environment.

        This method sets up all action-specific registries
        (extract, transform, load), optionally preloading
        default Fragua components when fg_config is enabled.

        Returns:
            FraguaSections:
                Container holding all action registries.
        """

        sections = FraguaSections(self)
        logger.info("Default actions initialized for environment '%s'.", self.name)
        return sections

    # ------------------- Helper Properties -------------------- #
    @property
    def extract(self) -> FraguaRegistry:
        """
        Access the Extract action registry.

        Returns:
            ExtractRegistry:
                Registry containing all extract-related components
                (agents, functions, etc).
        """
        return self.sections.extract

    @property
    def transform(self) -> FraguaRegistry:
        """
        Access the Transform action registry.

        Returns:
            TransformRegistry:
                Registry containing all transform-related components
                (agents, functions, etc).
        """
        return self.sections.transform

    @property
    def load(self) -> FraguaRegistry:
        """
        Access the Load action registry.

        Returns:
            LoadRegistry:
                Registry containing all load-related components
                (agents, functions, etc).
        """
        return self.sections.load

    @property
    def functions(self) -> Dict[str, FraguaSet[Any]]:
        """
        Retrieve all function sets grouped by action.

        Returns:
            Dict[str, FraguaSet]:
                Mapping of action name to its corresponding functions set.
        """
        extract_functions = self.extract.get_set(ComponentType.FUNCTION.value)
        transform_functions = self.transform.get_set(ComponentType.FUNCTION.value)
        load_functions = self.load.get_set(ComponentType.FUNCTION.value)

        if extract_functions and transform_functions and load_functions:

            return {
                ActionType.EXTRACT.value: extract_functions,
                ActionType.TRANSFORM.value: transform_functions,
                ActionType.LOAD.value: load_functions,
            }
        raise KeyError("Functions set not found in registry.")

    @property
    def agents(self) -> Dict[str, FraguaSet[Any]]:
        """
        Retrieve all agent sets grouped by action.

        Returns:
            Dict([str, FraguaSet]):
                Mapping of action name to its corresponding agents set.
        """
        extract_agents = self.extract.get_set(ComponentType.FUNCTION.value)
        transform_agents = self.transform.get_set(ComponentType.FUNCTION.value)
        load_agents = self.load.get_set(ComponentType.FUNCTION.value)

        if extract_agents and transform_agents and load_agents:

            return {
                ActionType.EXTRACT.value: extract_agents,
                ActionType.TRANSFORM.value: transform_agents,
                ActionType.LOAD.value: load_agents,
            }
        raise KeyError("Agents set not found in registry.")

    # ---------------------- Global API ---------------------- #
    def _get_set(self, action: ActionType, kind: ComponentType) -> FraguaSet[Any]:
        """
        Resolve a FraguaSet by action and component kind.
        """
        registry = self.sections.get_section(action.value)

        fragua_set = registry.get_set(kind.value)

        if fragua_set is None:
            raise ValueError(f"Invalid action type: {action.value}")

        return fragua_set

    @overload
    def get(
        self,
        action: ActionType,
        kind: Literal[ComponentType.AGENT],
        name: str,
    ) -> FraguaAgent: ...

    @overload
    def get(
        self,
        action: ActionType,
        kind: Literal[ComponentType.FUNCTION],
        name: str,
    ) -> Dict[str, Any]: ...

    def get(
        self,
        action: ActionType,
        kind: ComponentType,
        name: str,
    ) -> Any:
        """Retrive a Component, by an given action type and component type."""
        fragua_set = self._get_set(action, kind)
        return fragua_set.get_one(name)

    def add(
        self,
        action: ActionType,
        kind: ComponentType,
        name: str,
        component: Any,
    ) -> bool:
        """Add component."""
        fragua_set = self._get_set(action, kind)
        created = fragua_set.add(name, component)

        if not created:
            return False

        token = self._token(kind=kind.value, name=name)

        if hasattr(component, "__dict__"):
            component.token = token

        logger.info(
            "%s registered: %s (%s)",
            kind.value.capitalize(),
            name,
            action.value,
        )

        return True

    def update(
        self,
        kind: ComponentType,
        action: ActionType,
        old_name: str,
        new_name: str,
    ) -> bool:
        """Update a component."""
        fragua_set = self._get_set(action, kind)
        updated = fragua_set.update(old_name, new_name)

        if not updated:
            raise ValueError(f"{kind.value.capitalize()} not found.")

        logger.info(
            "%s renamed: %s -> %s (%s)",
            kind.value.capitalize(),
            old_name,
            new_name,
            action.value,
        )

        return updated

    def delete(self, kind: ComponentType, name: str, action: ActionType) -> bool:
        """Delete a component."""
        fragua_set = self._get_set(action, kind)
        deleted = fragua_set.delete_one(name)

        if not deleted:
            raise ValueError(f"{kind.value.capitalize()} not found.")

        logger.info(
            "%s deleted: %s (%s)",
            kind.value.capitalize(),
            name,
            action.value,
        )

        return deleted

    def create(self, action: ActionType, kind: ComponentType, name: str) -> bool:
        """Create and add new component."""
        new_component: Any = object()

        def _build_agent(agent_name: str) -> FraguaAgent:
            """Instantiate the correct agent class based on action."""
            class_map: Dict[str, Type[FraguaAgent]] = {
                ActionType.EXTRACT.value: Extractor,
                ActionType.TRANSFORM.value: Transformer,
                ActionType.LOAD.value: Loader,
            }

            agent_class = class_map.get(action)
            if agent_class is None:
                raise ValueError(f"Invalid action type: {action.value}")

            return agent_class(agent_name, self)

        if kind is ComponentType.AGENT:
            new_component = _build_agent(name)

        added = self.add(action, kind, name, new_component)

        if added:
            logger.info(
                "component created: %s (%s)",
                name,
                new_component.__class__.__name__,
            )

        return added

    # ---------------------- Summary ------------------------- #
    def summary(self) -> Dict[str, Any]:
        """
        Return a structured summary of the Environment instance.

        This summary aggregates high-level metadata and detailed
        information from all core environment components, including:

        - Environment identity (name and type)
        - Warehouse state and configuration
        - Action registries (extract, transform, load), each including
        their respective agents, functions, etc.

        Returns:
            Dict([str, Any]):
                A hierarchical dictionary representing the complete
                environment configuration and registered components.
        """

        return {
            ComponentType.ENVIRONMENT.value: self.name,
            ComponentType.WAREHOUSE.value: self.warehouse.summary(),
            ComponentType.ACTIONS.value: self.sections.summary(),
        }

    def __repr__(self) -> str:
        return f"<Environment name={self.name!r}>"
