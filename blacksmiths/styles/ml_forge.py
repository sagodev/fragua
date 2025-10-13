"""MLForge: transformations for machine learning preprocessing."""

import numpy as np
from sklearn.preprocessing import MinMaxScaler
import hashlib
from datetime import datetime
import logging
import pandas as pd
from storage.bagons import Bagon
from blacksmiths.styles.base_style import ForgeStyle

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class MLForge(ForgeStyle):
    """
    Prepares Bagons for ML:
    - Fill missing with mean
    - Standardize string columns
    - Encode categoricals
    - Scale numeric columns
    - Treat outliers
    """

    def transform(self, bagon: Bagon) -> Bagon:
        df = bagon.data.copy()

        self._fill_missing(df)
        self._standardize(df)
        self._encode_categoricals(df)
        self._treat_outliers(df)
        self._scale_numeric(df)
        self._add_metadata(df)

        return Bagon(name=bagon.name, data=df)

    def _fill_missing(self, df: pd.DataFrame):
        for col in df.columns:
            if pd.api.types.is_numeric_dtype(df[col]):
                df[col].fillna(df[col].mean(), inplace=True)
            else:
                df[col].fillna("unknown", inplace=True)
        logger.info("MLForge: Missing values filled.")

    def _standardize(self, df: pd.DataFrame):
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].astype(str).str.strip().str.lower()
        logger.info("MLForge: String columns standardized.")

    def _encode_categoricals(self, df: pd.DataFrame):
        cat_cols = df.select_dtypes(include="object").columns
        if len(cat_cols) > 0:
            df_dummies = pd.get_dummies(df[cat_cols], dummy_na=False)
            df.drop(columns=cat_cols, inplace=True)
            df[df_dummies.columns] = df_dummies
        logger.info("MLForge: Categoricals encoded.")

    def _scale_numeric(self, df: pd.DataFrame):
        num_cols = df.select_dtypes(include="number").columns
        if len(num_cols) > 0:
            scaler = MinMaxScaler()
            df[num_cols] = scaler.fit_transform(df[num_cols])
        logger.info("MLForge: Numeric columns scaled.")

    def _treat_outliers(self, df: pd.DataFrame):
        num_cols = df.select_dtypes(include="number").columns
        for col in num_cols:
            Q1, Q3 = df[col].quantile([0.25, 0.75])
            IQR = Q3 - Q1
            df[col] = np.clip(df[col], Q1 - 1.5 * IQR, Q3 + 1.5 * IQR)
        logger.info("MLForge: Outliers treated.")

    def _add_metadata(self, df: pd.DataFrame):
        checksum = hashlib.sha256(
            pd.util.hash_pandas_object(df, index=True).values
        ).hexdigest()
        df["_forge_name"] = "MLForge"
        df["_transform_timestamp"] = datetime.utcnow()
        df["_checksum"] = checksum
