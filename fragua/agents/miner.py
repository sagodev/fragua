"""
Miner agent responsible for extracting data using ExtractionStyles.

The Miner now uses ExtractionStyles to process data from sources
and stores results in Wagons via StoreManager.
"""

from __future__ import annotations

from typing import Type, Any
from fragua.styles.mine_style import (
    MineStyle,
    MINESTYLE_REGISTRY,
)
from fragua.store.wagon import Wagon
from fragua.core.base_agent import BaseAgent


class Miner(BaseAgent[MineStyle[Any, Any], Wagon[Any]]):
    """Agent that applies extraction styles to data sources for extraction."""

    style_registry: dict[str, Type[MineStyle[Any, Any]]] = MINESTYLE_REGISTRY
    result_type: Type[Wagon[Any]] = Wagon

    def work(self, *args: Any, **kwargs: Any) -> Wagon[Any]:
        return self.apply_style(*args, **kwargs)
