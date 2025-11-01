"""Blacksmith Class."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from fragua.agents.agent import Agent
from fragua.agents.store_manager import StoreManager
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class Blacksmith(Agent):
    """Agent that applies forge styles to data for transformation."""

    def __init__(self, name: str, store_manager: StoreManager):
        super().__init__(name=name, store_manager=store_manager)
        self.role: str = "blacksmith"
        self.action: str = "forge"
        self.storage_type: str = "Box"

        logger.debug(
            "Initialized Agent '%s' with role '%s' (action=%s, storage=%s)",
            self.name,
            self.role,
            self.action,
            self.storage_type,
        )

    def work(
        self,
        /,
        style: str,
        apply_to: str | None = None,
        save_as: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Execute the agent's task using the action and style defined by its role."""

        # ----------------- Get data from store -----------------
        data = self.get_from_store(apply_to)

        # ----------------- Params Instance -----------------
        kwargs["data"] = data
        params_instance = self._get_params(style, **kwargs)

        # ----------------- Style Instance -----------------
        style_instance = self._get_style(style)

        # ----------------- Apply Style -----------------
        stylized_data = style_instance.use(params_instance)

        # ----------------- Create Storage -----------------
        storage = self.create_storage(stylized_data)

        # ----------------- Generate Operation Metadata -----------------
        self._generate_operation_metadata(
            style_name=style,
            storage=storage,
            origin=params_instance,
        )

        self._operations.append(
            {
                "action": self.action,
                "style_name": style,
                "timestamp": datetime.now(timezone.utc),
                "params": params_instance,
            }
        )

        # ----------------- Auto-store -----------------
        if save_as is not None:
            self.add_to_store(storage, save_as)
        else:
            generated_name = self._generate_storage_name(style)
            self.add_to_store(storage, generated_name)
