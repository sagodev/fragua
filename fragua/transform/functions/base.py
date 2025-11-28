"""
Generic TransformFunction class.
"""

from typing import Generic
from fragua.core.function import FraguaFunction
from fragua.transform.params.generic_types import TransformParamsT


class TransformFunction(FraguaFunction[TransformParamsT], Generic[TransformParamsT]):
    """
    Represents a Transform function in the Fragua framework.
    Used to define transformations applied to extracted data.
    """

    def __init__(self, name: str, params: TransformParamsT) -> None:
        super().__init__(name=name, action="transform", params=params)
