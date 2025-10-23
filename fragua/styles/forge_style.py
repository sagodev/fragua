"""
Base ForgeStyle class for Fragua Blacksmiths.
Contains common utilities for transformations.
"""

from abc import abstractmethod
from typing import Any, Generic, Dict, Type, Callable
from pandas import DataFrame
from pandas.api.types import is_numeric_dtype
from fragua.core.base_style import BaseStyle, ResultT
from fragua.params.forge_params import ForgeParamsT
from fragua.utils.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------- #
# Registry for dynamic loading
# ---------------------------------------------------------------------- #
FORGESTYLE_REGISTRY: Dict[str, Type["ForgeStyle[Any, Any]"]] = {}


def register_forge_style(
    name: str,
) -> Callable[[Type["ForgeStyle[Any, Any]"]], Type["ForgeStyle[Any, Any]"]]:
    """Decorator to register a ForgeStyle subclass dynamically."""

    def wrapper(
        cls: Type["ForgeStyle[ForgeParamsT, ResultT]"],
    ) -> Type["ForgeStyle[ForgeParamsT, ResultT]"]:
        FORGESTYLE_REGISTRY[name] = cls
        logger.debug("Registered ForgeStyle: %s", name)
        return cls

    return wrapper


# ---------------------------------------------------------------------- #
# Base ForgeStyle
# ---------------------------------------------------------------------- #
class ForgeStyle(BaseStyle[ForgeParamsT, ResultT], Generic[ForgeParamsT, ResultT]):
    """
    Base class for ForgeStyles.

    Standard pipeline provided by BaseStyle:
        validate_params -> _run -> validate_result -> postprocess
    """

    # ---------------------------------------------------------------------- #
    # Abstract forge method (subclasses implement this)
    # ---------------------------------------------------------------------- #
    @abstractmethod
    def forge(self, params: ForgeParamsT) -> ResultT:
        """
        Transform the input data according to params.
        Must be implemented by subclasses.
        """
        raise NotImplementedError

    # ---------------------------------------------------------------------- #
    # Optional parameter validation hook
    # ---------------------------------------------------------------------- #
    def validate_params(self, params: ForgeParamsT) -> ForgeParamsT:
        """Validate input parameters before forging."""
        super().validate_params(params)
        return params

    # ---------------------------------------------------------------------- #
    # Internal _run implementation for BaseStyle
    # ---------------------------------------------------------------------- #
    def _run(self, params: ForgeParamsT) -> ResultT:
        """
        Executes the ForgeStyle transformation step.

        This method is called by BaseStyle.use().
        """
        logger.debug("Starting ForgeStyle '%s' transformation.", self.style_name)
        result = self.forge(params)
        logger.debug("ForgeStyle '%s' transformation completed.", self.style_name)
        return result

    # ---------------------------------------------------------------------- #
    # Utilities for DataFrames
    # ---------------------------------------------------------------------- #
    def _fill_missing(
        self,
        df: DataFrame,
        numeric_fill: str = "mean",
        categorical_fill: str = "unknown",
    ) -> None:
        """Fill missing values in DataFrame."""
        for col in df.columns:
            if is_numeric_dtype(df[col]):
                fill_value = df[col].mean() if numeric_fill == "mean" else 0
                df[col] = df[col].fillna(fill_value)
            else:
                df[col] = df[col].fillna(categorical_fill)
        logger.info("%s: Missing values filled.", self.style_name)

    def _standardize(self, df: DataFrame) -> None:
        """Standardize string columns (strip spaces and lowercase)."""
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].astype(str).str.strip().str.lower()
        logger.info("%s: String columns standardized.", self.style_name)
