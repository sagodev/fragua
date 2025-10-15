"""
Unified storage backend for Fragua ETL.
Handles Wagons, Boxes, and Containers efficiently with metadata tracking.
"""

from typing import Any, Dict
from agents.extraction.wagons import Wagon
from agents.transformation.boxes import Box
from agents.loading.containers import Container


class Storage:
    """
    Central in-memory storage for Fragua pipeline.

    Responsible for storing, retrieving, and managing all Wagons, Boxes, and Containers.
    """

    def __init__(self):
        self._wagons: Dict[str, Wagon] = {}
        self._boxes: Dict[str, Box] = {}
        self._containers: Dict[str, Container] = {}

    # -----------------------
    # Generic Access Methods
    # -----------------------
    def _save(self, collection: Dict[str, Any], name: str, item: Any):
        collection[name] = item

    def _load(self, collection: Dict[str, Any], name: str) -> Any:
        return collection.get(name)

    def _remove(self, collection: Dict[str, Any], name: str) -> bool:
        return collection.pop(name, None) is not None

    def _exists(self, collection: Dict[str, Any], name: str) -> bool:
        return name in collection

    # -----------------------
    # Wagons
    # -----------------------
    def save_wagon(self, name: str, wagon: Wagon):
        self._save(self._wagons, name, wagon)

    def load_wagon(self, name: str):
        return self._load(self._wagons, name)

    def remove_wagon(self, name: str):
        return self._remove(self._wagons, name)

    def has_wagon(self, name: str):
        return self._exists(self._wagons, name)

    # -----------------------
    # Boxes
    # -----------------------
    def save_box(self, name: str, box: Box):
        self._save(self._boxes, name, box)

    def load_box(self, name: str):
        return self._load(self._boxes, name)

    def remove_box(self, name: str):
        return self._remove(self._boxes, name)

    def has_box(self, name: str):
        return self._exists(self._boxes, name)

    # -----------------------
    # Containers
    # -----------------------
    def save_container(self, name: str, container: Container):
        self._save(self._containers, name, container)

    def load_container(self, name: str):
        return self._load(self._containers, name)

    def remove_container(self, name: str):
        return self._remove(self._containers, name)

    def has_container(self, name: str):
        return self._exists(self._containers, name)

    # -----------------------
    # Metadata and Reporting
    # -----------------------
    def list_all(self):
        return {
            "wagons": list(self._wagons.keys()),
            "boxes": list(self._boxes.keys()),
            "containers": list(self._containers.keys()),
        }

    def metadata_report(self):
        return {
            "wagons": {n: w.metadata for n, w in self._wagons.items()},
            "boxes": {n: b.metadata for n, b in self._boxes.items()},
            "containers": {n: c.metadata for n, c in self._containers.items()},
        }
