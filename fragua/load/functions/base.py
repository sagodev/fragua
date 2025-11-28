"""
Generic LoadFunction for Fragua.
"""

from typing import Any, Generic
from fragua.core.function import FraguaFunction
from fragua.load.params.load_params import LoadParamsT


class LoadFunction(FraguaFunction[LoadParamsT], Generic[LoadParamsT]):
    """
    Represents a Load function in the Fragua framework.
    """

    PURPOSE: str = "Load data into the target destination."

    def __init__(self, name: str, params: LoadParamsT) -> None:
        super().__init__(name=name, action="load", params=params)

    def summary(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "params_type": type(self.params).__name__,
            "purpose": self.PURPOSE,
        }
