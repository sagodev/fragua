"""Declarative component base."""

from abc import ABC
from typing import Any, Dict, Optional

from fragua.core.component import FraguaComponent


class FraguaClass(FraguaComponent, ABC):
    """
    Base class for declarative Fragua components.

    These components are never instantiated. All metadata lives at
    class level.
    """

    purpose: Optional[str] = None

    @classmethod
    def summary(cls) -> Dict[str, Any]:
        """
        Default class summary.
        """
        return {
            "name": cls.__name__,
            "purpose": cls.purpose,
            "type": cls.__name__,
        }
