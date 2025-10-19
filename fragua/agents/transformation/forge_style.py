"""
Base ForgeStyle class for Fragua Blacksmiths.
Contains common utilities for transformations.
"""

from abc import abstractmethod
from typing import Any, Generic, Dict, Type, Callable, Literal
from datetime import datetime, timezone
from pandas import DataFrame
from pandas.api.types import is_numeric_dtype

from fragua.utils.metrics import calculate_checksum
from fragua.core.base_style import BaseStyle, DataT, ResultT
from fragua.utils.logger import get_logger

logger = get_logger(__name__)

FORGESTYLE_REGISTRY: Dict[str, Type["ForgeStyle[Any, Any]"]] = {}


def register_forge_style(
    name: str,
) -> Callable[[Type["ForgeStyle[DataT, ResultT]"]], Type["ForgeStyle[DataT, ResultT]"]]:
    """
    Decorator to register a ForgeStyle subclass dynamically.
    """

    def wrapper(
        cls: Type["ForgeStyle[DataT, ResultT]"],
    ) -> Type["ForgeStyle[DataT, ResultT]"]:
        FORGESTYLE_REGISTRY[name] = cls
        logger.debug("Registered ForgeStyle: %s", name)
        return cls

    return wrapper


class ForgeStyle(BaseStyle[DataT, ResultT], Generic[DataT, ResultT]):
    """
    Base class for ForgeStyles.

    Provides common utilities for transformations.
    """

    def __init__(self, style_name: str) -> None:
        super().__init__(style_name)
        self.metadata: Dict[str, Any] = {}

    def use(self, source_params: DataT) -> ResultT:
        """
        Main transformation pipeline: forge -> validate -> postprocess.
        """
        if source_params is None:
            raise ValueError("Input data cannot be None")

        logger.debug(
            "Starting ForgeStyle '%s' transformation pipeline.", self.style_name
        )

        try:
            result: ResultT = self._apply_pipeline(source_params)
            return result

        except Exception as e:
            self.log_error(e)
            raise

    def _apply_pipeline(self, source_params: DataT) -> ResultT:
        """
        Internal method to apply the transformation pipeline generically.
        """
        transformed = self.forge(source_params)
        logger.debug("%s: forge() step completed.", self.style_name)

        validated = self.validate(transformed)
        logger.debug("%s: validate() step completed.", self.style_name)

        result = self.postprocess(validated)
        logger.debug("%s: postprocess() step completed.", self.style_name)

        return result

    @abstractmethod
    def forge(self, source_params: DataT) -> ResultT:
        """
        Must be implemented by subclasses to transform data.

        Args:
            source_params (DataT): Input data

        Returns:
            ResultT: Transformed result
        """
        raise NotImplementedError

    # ------------------ Utilities for DataFrames ------------------ #

    def _fill_missing(
        self,
        df: DataFrame,
        numeric_fill: Literal["mean", "zero"] = "mean",
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
