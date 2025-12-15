"""
Transform Sets Module.

Defines the collection sets used to register and organize all transformation-
related components in the Fragua ETL framework, including parameters,
functions, styles, and agents.
"""

from typing import Any, Dict, cast
from fragua.core.set import FraguaSet
from fragua.transform import (
    TRANSFORM_FUNCTION_CLASSES,
    TRANSFORM_PARAMS_CLASSES,
    TRANSFORM_STYLE_CLASSES,
    TransformStyle,
    TransformFunction,
    TransformParams,
    Transformer,
)


class TransformParamsSet(FraguaSet):
    """
    Set that registers transformation parameter classes.

    This set contains all parameter definitions required to configure
    transformation pipelines. Each entry maps a transformation style
    name to its corresponding parameter class.
    """

    def __init__(self, fg_config: bool, set_name: str = "params") -> None:
        """
        Initialize the TransformParamsSet.

        Args:
            fg_config (bool):
                Indicates whether built-in Fragua parameter classes
                should be automatically registered.
            set_name (str):
                Logical name of the set within the registry.
        """
        super().__init__(set_name)
        self.fg_config = fg_config
        self._initialize_params()

    def _initialize_params(self) -> None:
        """
        Register all predefined transformation parameter classes.

        Parameter classes are loaded only when framework configuration
        is enabled.
        """
        if self.fg_config:
            for name, cls in TRANSFORM_PARAMS_CLASSES.items():
                instance = cls(name)
                self.add(name, instance)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Generate a structured summary of all transform parameter classes.

        Each parameter class is instantiated in order to extract its
        metadata and declared field descriptions.

        Returns:
            Dict[str, Dict[str, Any]]:
                A mapping of parameter names to their summary metadata.
        """
        result: Dict[str, Dict[str, Any]] = {}
        for name, instance in self.get_all().items():
            obj = cast(TransformParams, instance)
            result[name] = obj.summary()

        return result


class TransformFunctionSet(FraguaSet):
    """
    Set that registers transformation function classes.

    Transformation functions define the executable logic applied
    during a transformation pipeline.
    """

    def __init__(self, fg_config: bool, set_name: str = "functions") -> None:
        """
        Initialize the TransformFunctionSet.

        Args:
            fg_config (bool):
                Indicates whether built-in Fragua transform functions
                should be automatically registered.
            set_name (str):
                Logical name of the set within the registry.
        """
        super().__init__(set_name)
        self.fg_config = fg_config
        self._initialize_functions()

    def _initialize_functions(self) -> None:
        """
        Register all predefined transformation function classes.

        Functions are only registered when framework configuration
        is enabled.
        """
        if self.fg_config:
            for name, cls in TRANSFORM_FUNCTION_CLASSES.items():
                instance = cls()
                self.add(name, instance)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Generate a structured summary of all transform functions.

        Each function class is instantiated in order to expose
        its declared purpose and execution steps.

        Returns:
            Dict[str, Dict[str, Any]]:
                A mapping of function names to their summary metadata.
        """
        result: Dict[str, Dict[str, Any]] = {}
        for name, instance in self.get_all().items():
            obj = cast(TransformFunction, instance)
            result[name] = obj.summary()

        return result


class TransformStyleSet(FraguaSet):
    """
    Set that registers transformation style classes.

    Styles define how transformation functions are orchestrated
    and applied within a pipeline.
    """

    def __init__(self, fg_config: bool, set_name: str = "styles") -> None:
        """
        Initialize the TransformStyleSet.

        Args:
            fg_config (bool):
                Indicates whether built-in Fragua styles
                should be automatically registered.
            set_name (str):
                Logical name of the set within the registry.
        """
        super().__init__(set_name)
        self.fg_config = fg_config
        self._initialize_styles()

    def _initialize_styles(self) -> None:
        """
        Register all predefined transformation style classes.

        Styles are only registered when framework configuration
        is enabled.
        """
        if self.fg_config:
            for name, cls in TRANSFORM_STYLE_CLASSES.items():
                instance = cls()
                self.add(name, instance)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Generate a structured summary of all transform styles.

        Returns:
            Dict[str, Dict[str, Any]]:
                A mapping of style names to their summary metadata.
        """
        result: Dict[str, Dict[str, Any]] = {}
        for name, instance in self.get_all().items():
            obj = cast(TransformStyle[TransformParams], instance)
            result[name] = obj.summary()

        return result


class TransformAgentSet(FraguaSet):
    """
    Set that stores transformation agent instances.

    Agents are responsible for executing transformation workflows
    using resolved styles, functions, and parameters.
    """

    def __init__(self, set_name: str = "agents"):
        """
        Initialize the TransformAgentSet.

        Args:
            set_name (str):
                Logical name of the set within the registry.
        """
        super().__init__(set_name)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Generate a structured summary of all registered transform agents.

        Returns:
            Dict[str, Dict[str, Any]]:
                A mapping of agent names to their runtime summary metadata.
        """
        result: Dict[str, Dict[str, Any]] = {}

        for name, instance in self.get_all().items():
            obj = cast(Transformer[TransformParams], instance)
            result[name] = obj.summary()

        return result
