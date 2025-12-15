"""Component abstract class."""

from abc import ABC, abstractmethod
from typing import Any, Dict


class FraguaComponent(ABC):
    """
    Abstract base class for all Fragua components.

    A FraguaComponent represents a named, self-describing unit within
    the Fragua architecture. All concrete components must provide a
    structured summary that exposes their current state and metadata
    for introspection, debugging, and documentation purposes.
    """

    # pylint: disable=too-few-public-methods
    def __init__(self, component_name: str):
        """
        Initialize the component with a unique name.

        Args:
            component_name: Identifier used to reference the component
                within the environment and summaries.
        """
        self.name = component_name

    @abstractmethod
    def summary(self) -> Dict[str, Any]:
        """
        Return a structured summary describing the component state.

        Implementations should return serializable data only and avoid
        heavy objects. The summary is intended for diagnostics,
        observability, and external inspection.

        Returns:
            A dictionary representing the component summary.
        """
