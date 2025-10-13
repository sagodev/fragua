"""TextAnalysisForge: transformations for text data."""

import hashlib
from datetime import datetime
import logging
import pandas as pd
from blacksmiths.styles.base_style import ForgeStyle
from storage.bagons import Bagon

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class TextAnalysisForge(ForgeStyle):
    """
    Prepares Bagons for text analysis:
    - Standardize string columns
    - Clean text
    - Extract features such as word count
    """

    def transform(self, bagon: Bagon) -> Bagon:
        df = bagon.data.copy()

        self._standardize(df)
        self._text_cleaning(df)
        self._extract_text_features(df)
        self._add_metadata(df)

        return Bagon(name=bagon.name, data=df)

    def _standardize(self, df: pd.DataFrame):
        for col in df.select_dtypes(include="object").columns:
            df[col] = df[col].astype(str).str.strip().str.lower()
        logger.info("TextAnalysisForge: String columns standardized.")

    def _text_cleaning(self, df: pd.DataFrame):
        text_cols = df.select_dtypes(include="object").columns
        for col in text_cols:
            df[col] = df[col].str.replace(r"[^a-zA-Z0-9\s]", "", regex=True).str.strip()
        logger.info("TextAnalysisForge: Text cleaned.")

    def _extract_text_features(self, df: pd.DataFrame):
        text_cols = df.select_dtypes(include="object").columns
        for col in text_cols:
            df[f"{col}_word_count"] = df[col].apply(lambda x: len(str(x).split()))
        logger.info("TextAnalysisForge: Text features extracted.")

    def _add_metadata(self, df: pd.DataFrame):
        checksum = hashlib.sha256(
            pd.util.hash_pandas_object(df, index=True).values
        ).hexdigest()
        df["_forge_name"] = "TextAnalysisForge"
        df["_transform_timestamp"] = datetime.utcnow()
        df["_checksum"] = checksum
