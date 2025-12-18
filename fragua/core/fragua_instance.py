"""Runtime component base."""

from abc import ABC, abstractmethod
from typing import Any, Dict

from fragua.core.component import FraguaComponent


class FraguaInstance(FraguaComponent, ABC):
    """
    Base class for runtime Fragua components.

    These components represent live, stateful objects created
    during pipeline execution.
    """

    @abstractmethod
    def summary(self) -> Dict[str, Any]:
        """
        Return a structured summary of the instance state.

        Must reflect runtime configuration and execution status.
        """
