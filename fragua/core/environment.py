"""Base environment class for Fragua, refactored with docstrings."""

from __future__ import annotations

from typing import Any, Dict, Literal, overload

from fragua.core.agent import FraguaAgent
from fragua.core.sections import FraguaSections
from fragua.core.component import FraguaComponent
from fragua.core.registry import FraguaRegistry
from fragua.core.set import FraguaSet
from fragua.core.warehouse import FraguaWarehouse

from fragua.utils.logger import get_logger
from fragua.utils.security.security_context import FraguaSecurityContext, FraguaToken
from fragua.utils.types.enums import ActionType, ComponentType, FieldType

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

        sections = FraguaSections(self.fg_config)
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
        """Retrieve all function sets grouped by action."""
        try:
            return self._group_components(ComponentType.FUNCTION)
        except ValueError as exc:
            raise KeyError("Functions set not found in registry.") from exc

    @property
    def agents(self) -> Dict[str, FraguaSet[Any]]:
        """Retrieve all agent sets grouped by action."""
        try:
            return self._group_components(ComponentType.AGENT)
        except ValueError as exc:
            raise KeyError("Agents set not found in registry.") from exc

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

    def _group_components(self, kind: ComponentType) -> Dict[str, FraguaSet[Any]]:
        """Return a mapping of action name to the corresponding FraguaSet for a kind.

        This consolidates the repeated logic used to build dictionaries of agents
        or functions grouped by action and ensures a single failure mode if a
        set is missing.
        """
        result: Dict[str, FraguaSet[Any]] = {}

        for action in (ActionType.EXTRACT, ActionType.TRANSFORM, ActionType.LOAD):
            result[action.value] = self._get_set(action, kind)

        return result

    def _infer_name_from_component(self, component: Any) -> str:
        """Attempt to infer a registration name from a component.

        - If the component exposes a ``name`` attribute (e.g. FraguaAgent), use it.
        - If the component is a dictionary defining a function record (contains
          the ``FieldType.FUNCTION`` key), use the underlying function's ``__name__``.
        - If the component is callable, use ``component.__name__``.
        - Otherwise raise ValueError requiring an explicit name.
        """
        # FraguaComponent instances expose a .name attribute
        if hasattr(component, "name"):
            name = getattr(component, "name")
            if isinstance(name, str) and name:
                return name

        # Dict-based function records: try to extract the callable
        if isinstance(component, dict):
            func = component.get(FieldType.FUNCTION.value)
            if callable(func):
                inferred = getattr(func, "__name__", None)
                if isinstance(inferred, str) and inferred:
                    return inferred

            # As a fallback, allow a direct 'name' key in the dict
            dict_name = component.get("name") or component.get(FieldType.FUNC_KEY.value)
            if isinstance(dict_name, str) and dict_name:
                return dict_name

        # Callables (functions) typically have __name__
        if callable(component):
            inferred = getattr(component, "__name__", None)
            if isinstance(inferred, str) and inferred:
                return inferred

        raise ValueError(
            "Could not infer a name from component; please provide an explicit 'name' argument."
        )

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

    @overload
    def get(
        self,
        action: ActionType,
        kind: ComponentType,
        name: str,
    ) -> Any: ...

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
        component: Any,
        name: str | None = None,
    ) -> bool:
        """Add component.

        If ``name`` is omitted (None), attempt to infer it from the provided
        component (e.g. agent's ``.name`` or function's ``__name__``).
        """
        fragua_set = self._get_set(action, kind)

        # Infer name when not explicitly provided
        resolved_name = (
            name if name is not None else self._infer_name_from_component(component)
        )

        created = fragua_set.add(resolved_name, component)

        if not created:
            return False

        token = self._token(kind=kind.value, name=resolved_name)

        # Attach token when possible (best-effort). Avoid broad exception catching
        # by checking for a writable __dict__ first.
        if hasattr(component, "__dict__"):
            component.token = token

        logger.info(
            "%s registered: %s (%s)",
            kind.value.capitalize(),
            resolved_name,
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
        """Create and register a new component in the environment."""

        new_component: Any = None

        # ---------- Component construction ----------
        if kind is ComponentType.AGENT:
            new_component = FraguaAgent(name, self)
            new_component.set_execution_context(action)

        elif kind is ComponentType.REGISTRY:
            new_component = FraguaRegistry(name)

        elif kind is ComponentType.SET:
            new_component = FraguaSet(name)

        else:
            raise ValueError(f"Unsupported component type: {kind}")

        # ---------- Registration ----------
        self.add(action=action, kind=kind, name=name, component=new_component)
        return True

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
