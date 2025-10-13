import io
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import pandas as pd
import hashlib
import logging

from .base import FurnaceBase

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


class ExtractionError(Exception):
    pass


class ExtractorFurnace(FurnaceBase):
    """
    Furnace for extracting data from various sources (Excel, CSV, JSON).

    Features:
    - Auto-detect file type from path or bytes.
    - Supports multiple Excel sheets.
    - Adds metadata and optional checksum.
    """

    SUPPORTED_FORMATS = (".xlsx", ".xls", ".csv", ".json")

    def __init__(self, name: str, fuel: Optional[Dict[str, Any]] = None, enable_checksum: bool = False):
        """
        Parameters:
        -----------
        name: str
            Name of the furnace
        fuel: dict
            Optional configuration parameters
        enable_checksum: bool
            Whether to compute a checksum for extracted data
        """
        super().__init__(name, fuel)
        self.enable_checksum = enable_checksum

    # ----------------------------
    # Public interface
    # ----------------------------
    def forge(self, source: Optional[str | Path | bytes | io.BytesIO] = None, sheet_name: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        """
        Extract data from source and return as dict of DataFrames.
        """
        logger.info(f"{self.name}: Starting extraction...")

        if source is None:
            # Devuelve un DataFrame vacío solo con metadata
            df = pd.DataFrame()
            df = self._add_metadata(
                df,
                source_type="empty",
                name="empty_data",
                checksum=None,
                source_path="<none>"
            )
            return {"empty_data": df}
        
        # Read bytes from source
        try:
            data_bytes = self._read_source(source)
        except Exception as e:
            raise ExtractionError(f"{self.name}: Failed to read source: {e}")

        # Detect format
        file_type = self._detect_format(source, data_bytes)
        if file_type not in self.SUPPORTED_FORMATS:
            raise ExtractionError(f"{self.name}: Unsupported file type: {file_type}")

        # Compute checksum if enabled
        checksum = self._compute_checksum(data_bytes) if self.enable_checksum else None

        # Dispatch to specific extractor
        if file_type in (".xlsx", ".xls"):
            return self._extract_excel(io.BytesIO(data_bytes), sheet_name, checksum)
        elif file_type == ".csv":
            return {"csv_data": self._extract_csv(io.BytesIO(data_bytes), checksum)}
        elif file_type == ".json":
            return {"json_data": self._extract_json(io.BytesIO(data_bytes), checksum)}
        else:
            raise ExtractionError(f"{self.name}: Extraction failed for format: {file_type}")

    # ----------------------------
    # Internal helpers
    # ----------------------------
    def _read_source(self, source: str | Path | bytes | io.BytesIO) -> bytes:
        if isinstance(source, (bytes, io.BytesIO)):
            return source.read() if hasattr(source, "read") else source
        elif isinstance(source, (str, Path)):
            return Path(source).read_bytes()
        else:
            raise ValueError(f"{self.name}: Unsupported source type {type(source)}")

    def _detect_format(self, source, data_bytes: bytes) -> str:
        if isinstance(source, (str, Path)):
            return Path(source).suffix.lower()
        else:
            # Try to detect from content
            header = data_bytes[:8]
            if header.startswith(b"PK\x03\x04"):
                return ".xlsx"
            elif header.strip().startswith((b"{", b"[")):
                return ".json"
            elif b"," in header or b";" in header:
                return ".csv"
            else:
                # fallback attempts
                try:
                    pd.ExcelFile(io.BytesIO(data_bytes))
                    return ".xlsx"
                except Exception:
                    pass
                try:
                    pd.read_csv(io.BytesIO(data_bytes))
                    return ".csv"
                except Exception:
                    pass
        raise ExtractionError(f"{self.name}: Could not detect file format")

    def _compute_checksum(self, data_bytes: bytes) -> str:
        return hashlib.md5(data_bytes).hexdigest()

    # ----------------------------
    # Format-specific extractors
    # ----------------------------
    def _extract_excel(self, buffer: io.BytesIO, sheet_name: Optional[str], checksum: Optional[str]) -> Dict[str, pd.DataFrame]:
        try:
            excel = pd.ExcelFile(buffer)
            sheets = [sheet_name] if sheet_name else excel.sheet_names
            result = {}
            for name in sheets:
                df = excel.parse(name)
                df = self._add_metadata(df, source_type="excel", name=name, checksum=checksum)
                result[name] = df
            return result
        except Exception as e:
            raise ExtractionError(f"{self.name}: Error reading Excel file: {e}")

    def _extract_csv(self, buffer: io.BytesIO, checksum: Optional[str]) -> pd.DataFrame:
        try:
            df = pd.read_csv(buffer)
            return self._add_metadata(df, source_type="csv", name="csv_data", checksum=checksum)
        except Exception as e:
            raise ExtractionError(f"{self.name}: Error reading CSV file: {e}")

    def _extract_json(self, buffer: io.BytesIO, checksum: Optional[str]) -> pd.DataFrame:
        try:
            df = pd.read_json(buffer)
            return self._add_metadata(df, source_type="json", name="json_data", checksum=checksum)
        except Exception as e:
            raise ExtractionError(f"{self.name}: Error reading JSON file: {e}")

    # ----------------------------
    # Metadata
    # ----------------------------
    def _add_metadata(self, df: pd.DataFrame, source_type: str, name: str, checksum: Optional[str], source_path: Optional[str] = "<buffer>") -> pd.DataFrame:
        """
        Add audit and traceability metadata to the DataFrame.
        """
        df = df.copy()
        df["_source_type"] = source_type
        df["_source_name"] = name
        df["_extractor_name"] = self.name
        df["_source_path"] = source_path
        df["_extraction_datetime"] = datetime.utcnow()
        if checksum:
            df["_checksum"] = checksum
        return df

