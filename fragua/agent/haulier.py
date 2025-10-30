"""Haulier Class."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from fragua.agent.agent import Agent
from fragua.agent.store_manager import StoreManager
from fragua.params.params import PARAMS_REGISTRY, Params
from fragua.style.style import STYLE_REGISTRY, Style
from fragua.utils.logger import get_logger

logger = get_logger(__name__)


class Haulier(Agent):
    """Agent that applies extraction styles to data sources for extraction."""

    def __init__(self, name: str, store_manager: StoreManager):
        super().__init__(name=name, store_manager=store_manager)
        self.role: str = "haulier"
        self.action: str = "deliver"
        self.storage_type: str = "Container"

        logger.debug(
            "Initialized Agent '%s' with role '%s' (action=%s, storage=%s)",
            self.name,
            self.role,
            self.action,
            self.storage_type,
        )

    def work(
        self, /, style_name: str, storage_name: str | None = None, **kwargs: Any
    ) -> None:
        """Execute the agent's task using the action and style defined by its role."""

        # ----------------- PARAMS -----------------
        params_cls: type[Params] | None = PARAMS_REGISTRY.get((self.role, style_name))
        if not params_cls:
            raise ValueError(
                f"No Params class registered for ({self.role}, {style_name})"
            )

        params_instance = params_cls(**kwargs)

        # ----------------- STYLE -----------------
        style_key = (self.action, style_name)
        style_cls: type[Style[Any, Any]] | None = STYLE_REGISTRY.get(style_key)
        if not style_cls:
            raise ValueError(f"No Style class registered for {style_key}")

        # ----------------- Execute style -----------------
        style_instance = style_cls(style_name=style_name)
        stylized_data = style_instance.use(params_instance)

        # ----------------- Create storage -----------------
        storage = self.create_storage(stylized_data)

        # ----------------- Generate operation metadata -----------------
        self._generate_operation_metadata(
            style_name=style_name,
            storage=storage,
            origin=params_instance,
        )

        self._operations.append(
            {
                "action": self.action,
                "style_name": style_name,
                "timestamp": datetime.now(timezone.utc),
                "params": params_instance,
            }
        )

        logger.info(
            "[%s] Executed '%s' action with style '%s'",
            self.name,
            self.action,
            style_name,
        )
