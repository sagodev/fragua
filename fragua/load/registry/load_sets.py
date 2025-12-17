"""Load Sets Module."""

from typing import Any, Dict, cast
from fragua.core.function import FraguaFunction
from fragua.core.params import FraguaParams
from fragua.core.set import FraguaSet
from fragua.core.style import FraguaStyle
from fragua.load import (
    LOAD_FUNCTION_CLASSES,
    LOAD_PARAMS_SCHEMAS,
    LOAD_STYLE_CLASSES,
    Loader,
)


class LoadParamsSet(FraguaSet):
    """
    Set that registers and manages load parameter classes.

    This set contains all parameter definitions required by load styles
    to configure how data is written to external destinations.
    """

    def __init__(self, fg_config: bool, set_name: str = "params") -> None:
        """
        Initialize the LoadParamsSet.

        Args:
            fg_config (bool):
                Flag indicating whether parameter classes should be loaded
                from the Fragua configuration.
            set_name (str):
                Logical name of the set within the registry.
        """
        super().__init__(set_name)
        self.fg_config = fg_config
        self._initialize_params()

    def _initialize_params(self) -> None:
        """
        Register all predefined load parameter classes.

        Parameter classes are loaded only when Fragua configuration
        is enabled.
        """
        if self.fg_config:
            for name, cls in LOAD_PARAMS_SCHEMAS.items():
                instance = cls()
                self.add(name, instance)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Generate a summary of all registered load parameter classes.

        Returns:
            Dict[str, Dict[str, Any]]:
                A dictionary keyed by parameter name containing
                metadata and field descriptions for each parameter class.
        """
        result: Dict[str, Dict[str, Any]] = {}

        for name, instance in self.get_all().items():
            obj = cast(FraguaParams, instance)
            result[name] = obj.summary()

        return result


class LoadFunctionSet(FraguaSet):
    """
    Set that registers and manages load function classes.

    Load functions implement the concrete logic responsible for
    writing data to external systems or storage layers.
    """

    def __init__(self, fg_config: bool, set_name: str = "functions") -> None:
        """
        Initialize the LoadFunctionSet.

        Args:
            fg_config (bool):
                Flag indicating whether function classes should be loaded
                from the Fragua configuration.
            set_name (str):
                Logical name of the set within the registry.
        """
        super().__init__(set_name)
        self.fg_config = fg_config
        self._initialize_functions()

    def _initialize_functions(self) -> None:
        """
        Register all predefined load function classes.

        Function classes are loaded only when Fragua configuration
        is enabled.
        """
        if self.fg_config:
            for name, cls in LOAD_FUNCTION_CLASSES.items():
                instance = cls()
                self.add(name, instance)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Generate a summary of all registered load functions.

        Returns:
            Dict[str, Dict[str, Any]]:
                A dictionary keyed by function name containing
                high-level metadata for each load function.
        """
        result: Dict[str, Dict[str, Any]] = {}

        for name, instance in self.get_all().items():
            obj = cast(FraguaFunction, instance)
            result[name] = obj.summary()

        return result


class LoadStyleSet(FraguaSet):
    """
    Set that registers and manages load style classes.

    Load styles coordinate the execution of load functions by
    resolving parameters, applying transformations, and invoking
    the appropriate function logic.
    """

    def __init__(self, fg_config: bool, set_name: str = "styles") -> None:
        """
        Initialize the LoadStyleSet.

        Args:
            fg_config (bool):
                Flag indicating whether style classes should be loaded
                from the Fragua configuration.
            set_name (str):
                Logical name of the set within the registry.
        """
        super().__init__(set_name)
        self.fg_config = fg_config
        self._initialize_styles()

    def _initialize_styles(self) -> None:
        """
        Register all predefined load style classes.

        Style classes are loaded only when Fragua configuration
        is enabled.
        """
        if self.fg_config:
            for name, cls in LOAD_STYLE_CLASSES.items():
                instance = cls()
                self.add(name, instance)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Generate a summary of all registered load styles.

        Returns:
            Dict[str, Dict[str, Any]]:
                A dictionary keyed by style name containing
                metadata describing how each load style operates.
        """
        result: Dict[str, Dict[str, Any]] = {}

        for name, instance in self.get_all().items():
            obj = cast(FraguaStyle[Any], instance)
            result[name] = obj.summary()

        return result


class LoadAgentSet(FraguaSet):
    """
    Set that registers and manages load agent instances.

    Load agents are responsible for orchestrating the execution
    of load workflows and interacting with the warehouse layer.
    """

    def __init__(self, set_name: str = "agents") -> None:
        """
        Initialize the LoadAgentSet.

        Args:
            set_name (str):
                Logical name of the set within the registry.
        """
        super().__init__(set_name)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Generate a summary of all registered load agents.

        Returns:
            Dict[str, Dict[str, Any]]:
                A dictionary keyed by agent name containing
                runtime and configuration metadata.
        """
        result: Dict[str, Dict[str, Any]] = {}

        for name, instance in self.get_all().items():
            obj = cast(Loader[FraguaParams], instance)
            result[name] = obj.summary()

        return result
