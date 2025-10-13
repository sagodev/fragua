"""Miner: orchestrates extraction using pickaxes with retries, metrics, and logging."""

from typing import Iterable, List
from time import sleep, time
from miners.pickaxes.base_pickaxe import Pickaxe
from storage.bagons import Bagon
from core.logger import get_logger
from core.metrics import MetricsRegistry

logger = get_logger(__name__)


class Miner:
    """
    Coordinator for extraction. Executes a series of Pickaxes, handling retries,
    collecting metrics in Bagons and registering events globally.
    """

    def __init__(
        self,
        name: str = "miner",
        max_retries: int = 3,
        retry_delay: float = 1.0,
        metrics: MetricsRegistry = None,
    ):
        """
        Args:
            name: Name of the miner.
            max_retries: Number of times to retry a pickaxe on failure.
            retry_delay: Initial delay between retries in seconds (exponential backoff).
            metrics: Optional MetricsRegistry to log events.
        """
        self.name = name
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = get_logger(f"fragua.miner.{self.name}")
        self.metrics = metrics or MetricsRegistry()

    def extract(self, pickaxes: Iterable[Pickaxe]) -> List[Bagon]:
        """
        Execute each pickaxe's extract() method with retry logic, logging, and metrics.

        Returns:
            List of successfully extracted Bagons.
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
                    # Wrap in Bagon if needed
                    if not isinstance(result, Bagon):
                        from storage.bagons import Bagon as _Bagon

                        result = _Bagon(
                            name=getattr(pickaxe, "name", "unknown"), data=result
                        )
                    # Add metrics
                    duration = time() - pickaxe_start
                    result.metadata.update(
                        {
                            "attempts": attempt,
                            "duration_sec": duration,
                            "status": "success",
                        }
                    )
                    # Record in MetricsRegistry
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
                        # Record failure in metrics
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
