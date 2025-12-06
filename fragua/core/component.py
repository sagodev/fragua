"""Component abstract class."""

from abc import ABC, abstractmethod


class FraguaComponent(ABC):
    """Fragua component abstract class."""

    def __init__(self):
        """Initialize component."""

    @abstractmethod
    def _ignore_this(self):
        """Ignore this class."""
