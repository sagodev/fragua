"""
Miner agent responsible for extracting data using ExtractionStyles.

The Miner now uses ExtractionStyles to process data from sources
and stores results in Wagons via StoreManager.
"""

from __future__ import annotations

from typing import Type, Any
from fragua.styles.mine_styles import MineStyle
from fragua.store.wagon import Wagon
from fragua.core.base_agent import BaseAgent


class Miner(BaseAgent[MineStyle[Any, Any], Wagon[Any]]):
    """Agent that applies extraction styles to data sources for extraction."""

    storage_type: Type[Wagon[Any]] = Wagon
