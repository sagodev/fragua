"""
Base ForgeStyle class for Fragua Blacksmiths.
Contains common utilities for transformations.
"""

from abc import abstractmethod
from typing import Any, Generic, Dict, Type, Callable
from datetime import datetime, timezone
from pandas import DataFrame
from pandas.api.types import is_numeric_dtype

from fragua.utils.metrics import calculate_checksum
from fragua.core.base_style import BaseStyle, ResultT
from fragua.params.forge_params import ForgeParamsT
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


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


class ForgeStyle(BaseStyle[ForgeParamsT, ResultT], Generic[ForgeParamsT, ResultT]):
    """
    Base class for ForgeStyles.

    Provides a pipeline: validate_params -> forge -> validate_result -> postprocess.
    """

    def __init__(self, style_name: str) -> None:
        super().__init__(style_name)
        self.metadata: Dict[str, Any] = {}

    # ---------------------------------------------------------------------- #
    # Abstract transformation
    # ---------------------------------------------------------------------- #
    @abstractmethod
    def forge(self, params: ForgeParamsT) -> ResultT:
        """Transform the input data according to params."""
        raise NotImplementedError

    # ---------------------------------------------------------------------- #
    # Validation hooks
    # ---------------------------------------------------------------------- #
    def validate_params(self, params: ForgeParamsT) -> ForgeParamsT:
        """Validate input parameters before forging."""
        super().validate_params(params)
        return params

    # ---------------------------------------------------------------------- #
    # Main pipeline
    # ---------------------------------------------------------------------- #
    def use(self, params: ForgeParamsT) -> ResultT:
        """Main Forge pipeline: validate_params -> forge -> validate_result -> postprocess."""
        if params is None:
            raise ValueError("Input params cannot be None")

        logger.debug("Starting ForgeStyle '%s' pipeline.", self.style_name)

        try:
            # Validate input parameters
            params = self.validate_params(params)
            logger.debug("%s: validate_params() step completed.", self.style_name)

            # Transform / forge
            result = self.forge(params)
            logger.debug("%s: forge() step completed.", self.style_name)

            # Validate result
            result = self.validate_result(result)
            logger.debug("%s: validate_result() step completed.", self.style_name)

            # Optional postprocess
            result = self.postprocess(result)
            logger.debug("%s: postprocess() step completed.", self.style_name)

        except Exception as e:
            self.log_error(e)
            raise

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

    def _add_metadata(self, df: DataFrame) -> DataFrame:
        """Add metadata columns to the transformed dataframe."""
        checksum_value = calculate_checksum(df)
        df["_forge_name"] = self.style_name
        df["_transform_timestamp"] = datetime.now(timezone.utc)
        df["_checksum"] = checksum_value

        self.metadata["checksum"] = checksum_value
        logger.debug(
            "%s: Metadata added with checksum %s.", self.style_name, checksum_value
        )
        return df
