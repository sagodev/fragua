"""Fragua execution box.

Represents the final output of a pipeline execution.
"""

from typing import Any, Dict
import pandas as pd


class FraguaBox:
    """
    Execution result container.

    A FraguaBox encapsulates the final result of a pipeline
    along with the metadata required to persist it.
    """

    def __init__(
        self,
        *,
        key: str,
        result: dict[str, pd.DataFrame],
        metadata: Dict[str, Any] | None = None,
    ) -> None:
        self.key = key
        self.result = result
        self.metadata = metadata or {}
