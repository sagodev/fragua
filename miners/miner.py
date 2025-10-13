"""Miner: orchestrates extraction with auto-selection of Pickaxe, retries, logging, and metrics."""

from typing import Iterable, List, Optional
from time import sleep, time
from pathlib import Path
import io

from miners.pickaxes.base_pickaxe import Pickaxe
from miners.pickaxes.csv_pickaxe import CSVPickaxe
from miners.pickaxes.excel_pickaxe import ExcelPickaxe
from storage.bagons import Bagon
from core.logger import get_logger
from core.metrics import MetricsRegistry

logger = get_logger(__name__)


class Miner:
    """
    Coordinator for extraction. Can auto-select Pickaxe based on source type.
    Handles retries, logging, and metrics.
    """

    SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".json"}

    def __init__(
        self,
        name: str = "miner",
        max_retries: int = 3,
        retry_delay: float = 1.0,
        metrics: Optional[MetricsRegistry] = None,
    ):
        self.name = name
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = get_logger(f"fragua.miner.{self.name}")
        self.metrics = metrics or MetricsRegistry()

    # ----------------------------
    # Public interface
    # ----------------------------
    def exact(
        self,
        sources: Iterable[str | Path | bytes | io.BytesIO],
        sheet_name: Optional[str] = None,
    ) -> List[Bagon]:
        """
        Extract multiple sources automatically selecting the correct Pickaxe.
        Returns a list of Bagons.
        """
        bagons = []

        for src in sources:
            pickaxe = self._select_pickaxe(src, sheet_name)
            if pickaxe:
                bagons.extend(self.manual_extract([pickaxe]))
            else:
                self.logger.warning("Could not select Pickaxe for source: %s", src)

        return bagons

    def manual_extract(self, pickaxes: Iterable[Pickaxe]) -> List[Bagon]:
        """
        Execute each pickaxe with retry logic, logging, and metrics.
        Returns a list of successfully extracted Bagons.
        """
        bagons = []
        errors = []
        total_start = time()

        for pickaxe in pickaxes:
            attempt = 0
            success = False
            pickaxe_start = time()
            while attempt < self.max_retries and not success:
                attempt += 1
                try:
                    self.logger.info(
                        "Extraction attempt %d for pickaxe: %s", attempt, pickaxe.name
                    )
                    result = pickaxe.extract()
                    if not isinstance(result, Bagon):
                        from fragua.storage.bagons import Bagon as _Bagon

                        result = _Bagon(
                            name=getattr(pickaxe, "name", "unknown"), data=result
                        )
                    duration = time() - pickaxe_start
                    result.metadata.update(
                        {
                            "attempts": attempt,
                            "duration_sec": duration,
                            "status": "success",
                        }
                    )
                    self.metrics.record_event(
                        agent=f"miner.{self.name}",
                        action="extract",
                        bagon_name=result.name,
                        rows=result.metadata.get("rows", 0),
                        duration_sec=duration,
                        attempts=attempt,
                        status="success",
                    )
                    self.logger.info(
                        "Extraction successful: %s rows in %.2f sec",
                        result.metadata.get("rows"),
                        duration,
                    )
                    bagons.append(result)
                    success = True
                except Exception as e:
                    self.logger.warning(
                        "Attempt %d failed for pickaxe %s: %s", attempt, pickaxe.name, e
                    )
                    if attempt < self.max_retries:
                        delay = self.retry_delay * (2 ** (attempt - 1))
                        self.logger.info("Retrying in %.1f seconds...", delay)
                        sleep(delay)
                    else:
                        duration = time() - pickaxe_start
                        errors.append(
                            {
                                "pickaxe": pickaxe.name,
                                "error": str(e),
                                "attempts": attempt,
                                "duration_sec": duration,
                            }
                        )
                        self.logger.error(
                            "Extraction failed after %d attempts for pickaxe %s",
                            attempt,
                            pickaxe.name,
                        )
                        self.metrics.record_event(
                            agent=f"miner.{self.name}",
                            action="extract",
                            bagon_name=getattr(pickaxe, "name", "unknown"),
                            rows=0,
                            duration_sec=duration,
                            attempts=attempt,
                            status="failed",
                            error=str(e),
                        )

        total_duration = time() - total_start
        self.logger.info("Mining session completed in %.2f sec", total_duration)
        self.logger.info("Bagons extracted: %d, Failures: %d", len(bagons), len(errors))
        if errors:
            self.logger.warning("Errors summary: %s", errors)

        return bagons

    # ----------------------------
    # Internal helpers
    # ----------------------------
    def _select_pickaxe(
        self, source: str | Path | bytes | io.BytesIO, sheet_name: Optional[str] = None
    ) -> Optional[Pickaxe]:
        """
        Detect the type of source and return the corresponding Pickaxe.
        """
        ext = None
        if isinstance(source, (str, Path)):
            ext = Path(source).suffix.lower()
        elif isinstance(source, (bytes, io.BytesIO)):
            if hasattr(source, "read"):
                header = source.read(8)
                source.seek(0)
            else:
                header = source[:8]
            if header.startswith(b"PK\x03\x04"):
                ext = ".xlsx"
            elif header.strip().startswith((b"{", b"[")):
                ext = ".json"
            elif b"," in header or b";" in header:
                ext = ".csv"

        if ext not in self.SUPPORTED_EXTENSIONS:
            self.logger.warning("Unsupported source type or format: %s", source)
            return None

        # Instantiate Pickaxe
        if ext in (".xlsx", ".xls"):
            return ExcelPickaxe(
                source=source, name=f"excel:{source}", sheet_name=sheet_name
            )
        elif ext == ".csv":
            return CSVPickaxe(path=source, name=f"csv:{source}")
        elif ext == ".json":
            from fragua.miners.pickaxes.json_pickaxe import (
                JSONPickaxe,
            )  # suponiendo que exista

            return JSONPickaxe(path=source, name=f"json:{source}")
        else:
            return None
