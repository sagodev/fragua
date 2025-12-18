"""Component abstract base."""

from abc import ABC


class FraguaComponent(ABC):
    """
    Root abstract class for all Fragua components.

    A FraguaComponent represents a self-describing unit within the
    Fragua architecture, either declarative (class-level) or runtime
    (instance-level).
    """
