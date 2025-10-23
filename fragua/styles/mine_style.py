"""
Base ExtractionStyle class for Fragua Miners.
Contains common utilities for extraction workflows.
"""

from abc import abstractmethod
from typing import Any, Dict, Type, Callable, Generic
from fragua.core.base_style import BaseStyle, ResultT
from fragua.params.mine_params import MineParamsT
from fragua.utils.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------- #
# Registry for dynamic loading
# ---------------------------------------------------------------------- #
MINESTYLE_REGISTRY: Dict[str, Type["MineStyle[Any, Any]"]] = {}


def register_mine_style(
    name: str,
) -> Callable[[Type["MineStyle[Any, Any]"]], Type["MineStyle[Any, Any]"]]:
    """
    Decorator to register a MineStyle subclass.
    """

    def wrapper(
        cls: Type["MineStyle[Any, Any]"],
    ) -> Type["MineStyle[Any, Any]"]:
        MINESTYLE_REGISTRY[name] = cls
        logger.debug("Registered MineStyle: %s", name)
        return cls

    return wrapper


# ---------------------------------------------------------------------- #
# Base MineStyle
# ---------------------------------------------------------------------- #
class MineStyle(BaseStyle[MineParamsT, ResultT], Generic[MineParamsT, ResultT]):
    """
    Base class for all extraction styles in Fragua ETL.

    Standard pipeline provided by BaseStyle:
        validate_params -> _run -> validate_result -> postprocess
    """

    # ---------------------------------------------------------------------- #
    # Abstract extraction method (subclasses implement this)
    # ---------------------------------------------------------------------- #
    @abstractmethod
    def mine(self, params: MineParamsT) -> ResultT:
        """
        Extract data according to source parameters.
        Must be implemented by subclasses.
        """
        raise NotImplementedError

    # ---------------------------------------------------------------------- #
    # Optional parameter validation hook
    # ---------------------------------------------------------------------- #

    def validate_params(self, params: MineParamsT) -> MineParamsT:
        """Validate extraction-specific input parameters."""
        super().validate_params(params)
        return params

    # ---------------------------------------------------------------------- #
    # Internal _run implementation for BaseStyle
    # ---------------------------------------------------------------------- #
    def _run(self, params: MineParamsT) -> ResultT:
        """
        Executes the MineStyle extraction step.

        This method is called by BaseStyle.use().
        """
        logger.debug("Starting MineStyle '%s' extraction.", self.style_name)
        result = self.mine(params)
        logger.debug("MineStyle '%s' extraction completed.", self.style_name)
        return result
