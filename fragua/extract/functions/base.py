"""
Generic ExtractFunction for Fragua.
"""

from typing import Any, Dict, Generic

from fragua.core.function import FraguaFunction
from fragua.extract.params import ExtractParamsT


class ExtractFunction(FraguaFunction[ExtractParamsT], Generic[ExtractParamsT]):
    """
    Generic ExtractFunction for Fragua, typed by the specific ExtractParams subclass.
    """

    def __init__(self, name: str, params: ExtractParamsT) -> None:
        super().__init__(name=name, action="extract", params=params)

    def summary(self) -> Dict[str, Any]:
        return {
            "function": self.name,
            "params_type": type(self.params).__name__,
            "purpose": "Generic extract function",
        }
