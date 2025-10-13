"""Centralized metrics registry for Fragua."""

from typing import Dict, List, Any
from collections import defaultdict
from core.logger import get_logger

logger = get_logger("fragua.metrics")


class MetricsRegistry:
    """Registry to record and report metrics for Fragua agents."""

    def __init__(self):
        # agent_name -> list of events
        self._registry: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    def record_event(self, agent: str, action: str, bagon_name: str, **kwargs):
        """Record an event from an agent."""
        event = {"agent": agent, "action": action, "bagon_name": bagon_name, **kwargs}
        self._registry[agent].append(event)
        logger.info("Recorded event: %s", event)

    def get_agent_events(self, agent: str) -> List[Dict[str, Any]]:
        """Return all events for a given agent."""
        return self._registry.get(agent, [])

    def report_summary(self):
        """Print a summary of all metrics."""
        logger.info("==== Metrics Summary ====")
        for agent, events in self._registry.items():
            total_events = len(events)
            total_rows = sum(e.get("rows", 0) for e in events)
            total_duration = sum(e.get("duration_sec", 0) for e in events)
            logger.info(
                "Agent: %s | Events: %d | Total Rows: %d | Total Duration: %.2f sec",
                agent,
                total_events,
                total_rows,
                total_duration,
            )
        logger.info("==== End of Metrics Summary ====")
