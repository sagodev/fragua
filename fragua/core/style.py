"""
Base class for all styles used by ETL agents in Fragua.
"""

from abc import abstractmethod
from typing import Generic, Dict, Any

from fragua.core.component import FraguaComponent
from fragua.utils.logger import get_logger
from fragua.core.params import FraguaParamsT

logger = get_logger(__name__)


class FraguaStyle(FraguaComponent, Generic[FraguaParamsT]):
    """
    Abstract base class for all styles in Fragua.

    A FraguaStyle encapsulates a concrete data-processing strategy
    executed by an agent during an ETL workflow. Styles are responsible
    for applying a specific behavior using a validated Params schema
    and returning the resulting data to be persisted or further processed.
    """

    def __init__(self) -> None:
        """
        Initialize the style component.

        The component name is automatically derived from the class name.
        """
        super().__init__(component_name=self.__class__.__name__)

    @abstractmethod
    def _run(self, params: FraguaParamsT) -> Any:
        """
        Execute the core logic of the style.

        This method contains the actual implementation and must be
        provided by concrete subclasses.

        Args:
            params: Params instance containing validated configuration
                required by the style.

        Returns:
            The data produced by the style execution.

        Raises:
            NotImplementedError: If not implemented by a subclass.
        """
        raise NotImplementedError

    def use(self, params: FraguaParamsT) -> Any:
        """
        Execute the style using the standard execution pipeline.

        This public method acts as the stable entry point for agents
        and delegates execution to the internal `_run` implementation.

        Args:
            params: Params instance containing the configuration for
                the style execution.

        Returns:
            The data produced by the style execution.
        """
        return self._run(params)

    def summary(self) -> Dict[str, Any]:
        """
        Generate a structured summary describing the style.

        The summary includes the style type, name, and detailed
        field-level information provided by the concrete implementation.

        Returns:
            A dictionary representing the style summary.
        """
        return {
            "type": "style",
            "name": self.__class__.__name__,
            "fields": self.summary_fields(),
        }

    @abstractmethod
    def summary_fields(self) -> Dict[str, Any]:
        """
        Describe the behavior and expectations of the style.

        Implementations should return a dictionary detailing:
        - Purpose and intent of the style
        - Internal functions or pipelines involved
        - Expected Params schema and key fields
        - Execution behavior and side effects

        Returns:
            A dictionary describing the style characteristics.
        """
        raise NotImplementedError

    # ------------------------------------------------------------
    def __repr__(self) -> str:
        """
        Return a concise string representation of the style.

        Returns:
            A string identifying the style class and name.
        """
        return f"<{self.__class__.__name__} style_name={self.name}>"
