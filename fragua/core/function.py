"""
Base abstract class for all function schemas used by styles in Fragua.
"""

from abc import abstractmethod
from typing import Any

from fragua.core.component import FraguaComponent


class FraguaFunction(FraguaComponent):
    """
    Abstract base class for all executable function schemas in Fragua.

    A FraguaFunction represents a reusable, action-scoped unit of logic
    that can be invoked by styles during an ETL workflow. Functions are
    registered per action (extract, transform, load) and encapsulate
    executable behavior that may operate on data, parameters, or both.
    """

    def __init__(self, function_name: str, action: str) -> None:
        """
        Initialize the function with a name and associated action.

        Args:
            function_name: Unique identifier of the function.
            action: ETL action scope where the function is applicable
                (e.g., extract, transform, load).
        """
        super().__init__(component_name=function_name)
        self.action: str = action

    @abstractmethod
    def execute(self) -> Any:
        """
        Execute the function logic.

        Concrete implementations must define the execution behavior
        and return the result produced by the function.

        Returns:
            The result of the function execution.

        Raises:
            NotImplementedError: If the method is not implemented
                by a subclass.
        """
        raise NotImplementedError("Subclasses must implement the execute method.")
