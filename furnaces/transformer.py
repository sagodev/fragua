import hashlib
from datetime import datetime
from typing import Optional, Dict, Any
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import logging

from .base import FurnaceBase

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

VALID_MODES = ("analysis", "load", "report", "raw", "ml_preprocess", "text_analysis")


class TransformerFurnace(FurnaceBase):
    """
    Furnace for transforming DataFrames in multiple modes:
    analysis, load, report, raw, ml_preprocess, text_analysis.
    """

    def __init__(self, name: str, mode: str = "load", fuel: Optional[Dict[str, Any]] = None):
        super().__init__(name, fuel)
        self.mode = mode.lower()
        if self.mode not in VALID_MODES:
            logger.warning(f"Unknown mode '{self.mode}', defaulting to 'raw'.")
            self.mode = "raw"

    def forge(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Execute transformation pipeline and return new DataFrame with metadata.
        """
        logger.info(f"{self.name}: Starting transformation in '{self.mode}' mode.")
        df_copy = df.copy()

        # Pipeline
        self._clean_data(df_copy)

        if self.mode == "analysis":
            self._fill_missing(df_copy, strategy="mean")
            self._standardize(df_copy)
            self._add_derived_columns(df_copy)

        elif self.mode == "load":
            self._standardize(df_copy)
            self._validate(df_copy)

        elif self.mode == "report":
            self._fill_missing(df_copy, strategy="zero")
            self._standardize(df_copy)
            self._add_derived_columns(df_copy)
            self._format_for_report(df_copy)

        elif self.mode == "raw":
            pass  # basic cleaning only

        elif self.mode == "ml_preprocess":
            self._fill_missing(df_copy, strategy="mean")
            self._standardize(df_copy)
            self._treat_outliers(df_copy)
            self._encode_categoricals(df_copy)
            self._scale_numeric(df_copy)

        elif self.mode == "text_analysis":
            self._standardize(df_copy)
            self._text_cleaning(df_copy)
            self._extract_text_features(df_copy)

        # Metadata
        checksum = hashlib.sha256(pd.util.hash_pandas_object(df_copy, index=True).values).hexdigest()
        df_copy["_transformer_name"] = self.name
        df_copy["_mode"] = self.mode
        df_copy["_transform_timestamp"] = datetime.utcnow()
        df_copy["_checksum"] = checksum

        logger.info(f"{self.name}: Transformation pipeline completed.")
        return df_copy

    # ----------------------------
    # Pipeline steps
    # ----------------------------
    def _clean_data(self, df: pd.DataFrame):
        df.drop_duplicates(inplace=True)
        df.dropna(how="all", inplace=True)
        logger.info("Basic cleaning completed.")

    def _fill_missing(self, df: pd.DataFrame, strategy: str = "mean"):
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                if strategy == "mean":
                    df[col].fillna(df[col].mean(), inplace=True)
                elif strategy == "median":
                    df[col].fillna(df[col].median(), inplace=True)
                elif strategy == "zero":
                    df[col].fillna(0, inplace=True)
            elif pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col].fillna(pd.Timestamp("1970-01-01"), inplace=True)
            else:
                df[col].fillna("unknown", inplace=True)
        logger.info("Missing values filled.")

    def _standardize(self, df: pd.DataFrame):
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].astype(str).str.strip().str.lower()
        for col in df.columns:
            if "date" in col.lower() or "fecha" in col.lower():
                df[col] = pd.to_datetime(df[col], errors="coerce")
        logger.info("Standardization completed.")

    def _add_derived_columns(self, df: pd.DataFrame):
        today = pd.Timestamp.today()
        # Ejemplo de columnas derivadas genéricas
        if {"quantity", "price"}.issubset(df.columns):
            df["total"] = df["quantity"] * df["price"]
        if {"total", "discount_rate"}.issubset(df.columns):
            df["discounted_total"] = df["total"] * (1 - df["discount_rate"])
        logger.info("Derived columns added.")

    def _validate(self, df: pd.DataFrame):
        for col in df.select_dtypes(include="number").columns:
            if (df[col] < 0).any():
                logger.warning(f"Negative values detected in '{col}'.")
        logger.info("Validation completed.")

    def _format_for_report(self, df: pd.DataFrame):
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].str.title()
        for col in df.select_dtypes(include="number").columns:
            df[col] = df[col].round(2)
        logger.info("Report formatting completed.")

    def _encode_categoricals(self, df: pd.DataFrame):
        cat_cols = df.select_dtypes(include="object").columns
        if len(cat_cols) > 0:
            df_dummies = pd.get_dummies(df[cat_cols], dummy_na=False)
            df.drop(columns=cat_cols, inplace=True)
            df[df_dummies.columns] = df_dummies
        logger.info("Categorical columns encoded.")

    def _scale_numeric(self, df: pd.DataFrame):
        num_cols = df.select_dtypes(include="number").columns
        if len(num_cols) > 0:
            scaler = MinMaxScaler()
            df[num_cols] = scaler.fit_transform(df[num_cols])
        logger.info("Numeric columns scaled with MinMaxScaler.")

    def _treat_outliers(self, df: pd.DataFrame):
        num_cols = df.select_dtypes(include="number").columns
        for col in num_cols:
            Q1, Q3 = df[col].quantile([0.25, 0.75])
            IQR = Q3 - Q1
            df[col] = np.clip(df[col], Q1 - 1.5 * IQR, Q3 + 1.5 * IQR)
        logger.info("Outliers treated using IQR method.")

    def _text_cleaning(self, df: pd.DataFrame):
        text_cols = df.select_dtypes(include="object").columns
        for col in text_cols:
            df[col] = df[col].str.replace(r"[^a-zA-Z0-9\s]", "", regex=True).str.strip()
        logger.info("Text cleaning applied.")

    def _extract_text_features(self, df: pd.DataFrame):
        text_cols = df.select_dtypes(include="object").columns
        for col in text_cols:
            df[f"{col}_word_count"] = df[col].apply(lambda x: len(str(x).split()))
        logger.info("Text feature extraction completed.")
