"""Load Sets Module."""

from typing import Any, Dict, cast
from fragua.core.set import FraguaSet
from fragua.load import (
    LOAD_FUNCTION_CLASSES,
    LOAD_PARAMS_CLASSES,
    LOAD_STYLE_CLASSES,
    LoadStyle,
    LoadFunction,
    LoadParams,
    Loader,
)


class LoadParamsSet(FraguaSet):
    """Set containing load parameters classes."""

    def __init__(self, fg_config: bool, set_name: str = "params") -> None:
        super().__init__(set_name)
        self.fg_config = fg_config
        self._initialize_params()

    def _initialize_params(self) -> None:
        """Load all predefined load parameter classes into the set."""
        if self.fg_config:
            for name, cls in LOAD_PARAMS_CLASSES.items():
                self.create_one(name, cls)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Summary of all load params classes.
        """
        result: Dict[str, Dict[str, Any]] = {}

        if self.fg_config:
            for name, cls in self.get_all().items():
                obj = cls.__new__(cls)
                obj = cast(LoadParams, obj)
                LoadParams.__init__(obj, style=name)

                data = obj.summary()

                result[name] = data

        return result


class LoadFunctionSet(FraguaSet):
    """Load functions set."""

    def __init__(self, fg_config: bool, set_name: str = "functions") -> None:
        super().__init__(set_name)
        self.fg_config = fg_config
        self._initialize_functions()

    def _initialize_functions(self) -> None:
        """Load all predefined load functions into the set."""
        if self.fg_config:
            for name, cls in LOAD_FUNCTION_CLASSES.items():
                self.create_one(name, cls)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Summary of all load functions.
        """
        result: Dict[str, Dict[str, Any]] = {}

        if self.fg_config:
            for name, cls in self.get_all().items():

                params = LoadParams.__new__(LoadParams)
                LoadParams.__init__(params, style=name)

                obj = cls.__new__(cls)
                obj = cast(LoadFunction, obj)
                obj.name = name
                obj.params = params

                data = obj.summary()

                result[name] = data

        return result


class LoadStyleSet(FraguaSet):
    """Set that stores all load style classes."""

    def __init__(self, fg_config: bool, set_name: str = "styles") -> None:
        super().__init__(set_name)
        self.fg_config = fg_config
        self._initialize_styles()

    def _initialize_styles(self) -> None:
        """Load predefined load style classes into the set."""
        if self.fg_config:
            for name, cls in LOAD_STYLE_CLASSES.items():
                self.create_one(name, cls)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Summary of all load style classes.
        """
        result: Dict[str, Dict[str, Any]] = {}

        if self.fg_config:
            for name, cls in self.get_all().items():

                obj = cls.__new__(cls)
                obj = cast(LoadStyle, obj)
                data = obj.summary()

                result[name] = data

        return result


class LoadAgentSet(FraguaSet):
    """Load agents set."""

    def __init__(self, set_name="agents"):
        super().__init__(set_name)

    def summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Summary of all load agents.
        """
        result: Dict[str, Dict[str, Any]] = {}

        for name, instance in self.get_all().items():

            obj = cast(Loader, instance)
            data = obj.summary()

            result[name] = data

        return result
