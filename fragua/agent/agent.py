"""
Agent class in Fragua.
Agents can take a role to work like a Miner, Blacksmith, Transporter, or Master.
"""

from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
from types import FunctionType
from typing import (
    Any,
    Optional,
    TypeVar,
    Dict,
    List,
    Literal,
    Mapping,
    Union,
    Callable,
    Concatenate,
    ParamSpec,
)
from functools import wraps

import pandas as pd
from fragua.utils.logger import get_logger
from fragua.style.style import Style, STYLE_REGISTRY
from fragua.store.storage import Storage, get_storage, list_storages
from fragua.store.store import Store
from fragua.params.params import PARAMS_REGISTRY, Params
from fragua.utils.metrics import (
    add_metadata_to_storage,
    generate_metadata,
    StorageType,
    determine_storage_type,
)
from fragua.agent.agent_roles import get_role, MasterRole

StyleT = TypeVar("StyleT", bound=Style[Any, Any])
P = ParamSpec("P")
R = TypeVar("R")
SelfT = TypeVar("SelfT")

logger = get_logger(__name__)


def restricted_to_role(
    func: Callable[Concatenate[SelfT, P], R],
) -> Callable[Concatenate[SelfT, P], R]:
    """
    Decorator to restrict access to certain methods depending on the Agent's role.
    Methods marked as restricted will raise PermissionError if not allowed.
    """
    setattr(func, "_is_restricted", True)

    @wraps(func)
    def wrapper(self: SelfT, *args: P.args, **kwargs: P.kwargs) -> R:
        role = getattr(self, "role", "unknown")
        func_name = func.__name__
        allowed = getattr(self, "allowed_functions", ())

        if role != "master" and allowed and func_name not in allowed:
            raise PermissionError(
                f"Agent '{getattr(self, 'name', 'unknown')}' with role '{role}' "
                f"is not allowed to execute '{func_name}'"
            )

        return func(self, *args, **kwargs)

    return wrapper


class Agent:  # pylint: disable=too-many-instance-attributes
    """Agent class for ETL agents."""

    def __init__(self, role: str, name: str, store: Store | None = None):
        self.role: str = role.lower()
        self.name: str = name
        self._operations: list[dict[str, Any]] = []

        # Store Manager Attr
        self._store = store
        self._movement_log: List[dict[str, object]] = []

        try:
            role_cfg = get_role(self.role)
        except KeyError as exc:
            raise ValueError(f"No role registered with name '{role}'") from exc

        self.action: str = role_cfg["action"]
        self.storage_type: str = role_cfg["storage_type"]
        self.allowed_functions: tuple[str, ...] = role_cfg.get("allowed_functions", ())

        logger.debug(
            "Initialized Agent '%s' with role '%s' (action=%s, storage=%s)",
            self.name,
            self.role,
            self.action,
            self.storage_type,
        )

    def __dir__(self) -> list[str]:
        """
        Personaliza dir() para ocultar métodos marcados con _is_restricted
        cuando no estén permitidos por el rol actual.
        """
        all_attrs = super().__dir__()
        allowed = getattr(self, "allowed_functions", ())

        core_attrs = {
            "role",
            "name",
            "allowed_functions",
            "_store",
            "_movement_log",
            "get_operations",
            "__repr__",
        }

        visible: list[str] = []
        for attr in all_attrs:
            if attr.startswith("_") or attr in core_attrs:
                visible.append(attr)
                continue

            obj = getattr(self.__class__, attr, None)
            is_restricted = False

            if isinstance(obj, FunctionType):
                is_restricted = getattr(obj, "_is_restricted", False)

            if is_restricted:
                if allowed and attr in allowed:
                    visible.append(attr)
            else:
                visible.append(attr)

        return sorted(set(visible))

    # ----------------- Helpers ----------------- #
    def _determine_origin_name(self, origin: Any) -> Optional[str]:
        """Extract a meaningful origin name for operation metadata."""
        origin_name = None
        match origin:
            case Storage():
                origin_name = origin.__class__.__name__
                logger.debug("Detected Storage origin: %s", origin_name)
            case str() | Path():
                origin_name = Path(origin).name
                logger.debug("Detected file path origin: %s", origin_name)
            case _:
                if hasattr(origin, "path") and isinstance(origin.path, (str, Path)):
                    origin_name = Path(origin.path).name
                    logger.debug(
                        "Detected object with .path attribute: %s", origin_name
                    )
                elif hasattr(origin, "data") and isinstance(origin.data, pd.DataFrame):
                    origin_name = "DataFrame"
                    logger.debug("Detected object with .data as DataFrame")
                else:
                    logger.debug("Origin type not recognized; returning None")
        return origin_name

    # ------------------- Movement Logging ------------------- #
    @restricted_to_role
    def _log_movement(
        self,
        **movement_log: Any,
    ) -> None:
        """Records a movement in the internal log."""
        now = datetime.now().astimezone()

        date_str = now.date().isoformat()
        time_str = now.time().strftime("%H:%M:%S")

        raw_offset = now.strftime("%z")
        if raw_offset and len(raw_offset) == 5:
            tz_offset = f"{raw_offset[:3]}:{raw_offset[3:]}"
        else:
            tz_offset = raw_offset or ""

        entry: dict[str, object] = {
            "date": date_str,
            "time": time_str,
            "timezone": tz_offset,
            "operation": movement_log.get("operation"),
            "storage_type": movement_log.get("storage_type"),
            "storage_name": movement_log.get("storage_name"),
            "agent_name": movement_log.get("agent_name"),
            "store_name": getattr(self._store, "store_name", None),
            "success": movement_log.get("success"),
            "details": movement_log.get("details") or {},
        }

        self._movement_log.append(entry)
        logger.info(
            "[%s] Movement logged by '%s': %s '%s' by agent '%s' at %s %s %s",
            self.name,
            self.name,
            movement_log.get("operation"),
            movement_log.get("storage_name"),
            movement_log.get("agent_name"),
            entry["date"],
            entry["time"],
            entry["timezone"],
        )

    @restricted_to_role
    def movements_log(
        self,
        storage_type: Optional[StorageType] = None,
        storage_name: Optional[str] = None,
        agent_name: Optional[str] = None,
    ) -> List[dict[str, object]]:
        """Returns movements filtered by type, object name or agent."""
        result = self._movement_log
        if storage_type:
            result = [m for m in result if m["storage_type"] == storage_type]
        if storage_name:
            result = [m for m in result if m["storage_name"] == storage_name]
        if agent_name:
            result = [m for m in result if m["agent_name"] == agent_name]
        return result

    # ----------------- Metadata----------------- #
    @restricted_to_role
    def _generate_operation_metadata(
        self, style_name: str, storage: Storage[Any], origin: Any
    ) -> None:
        """Generate metadata from operation"""
        origin_name = self._determine_origin_name(origin)
        metadata = generate_metadata(
            storage=storage,
            metadata_type="operation",
            origin_name=origin_name,
            style_name=style_name,
        )
        add_metadata_to_storage(storage, metadata)

    @restricted_to_role
    def _generate_save_metadata(
        self, storage: Storage[Any], storage_name: str, agent_name: Optional[str]
    ) -> None:
        """Generate and attach metadata to a storage object before saving."""
        metadata_kwargs: Dict[str, Any] = {
            "metadata_type": "save",
            "storage_name": storage_name,
            "agent_name": agent_name,
            "store_manager_name": self.name,
        }
        metadata = generate_metadata(storage, **metadata_kwargs)
        add_metadata_to_storage(storage, metadata)

    # ----------------- Operations ----------------- #
    @restricted_to_role
    def get_operations(self) -> pd.DataFrame:
        """Return a DataFrame with all recorded operations."""
        logger.debug(
            "[%s] Returning %d recorded operations",
            self.name,
            len(self._operations),
        )
        return pd.DataFrame(self._operations)

    # ----------------- Create Storage ----------------- #
    @restricted_to_role
    def create_storage(self, data: Any, style_name: str) -> Storage[Any]:
        """
        Convert raw style output into the appropriate storage object using registry.
        For master, deduce storage_type automatically based on style_name prefix.
        """
        storage_type = self.storage_type

        if self.role == "master":
            prefix = style_name.split("_")[0]
            storage_type = MasterRole.style_prefix_to_storage.get(prefix, "Wagon")

        try:
            storage_cls = get_storage(storage_type)
        except KeyError as exc:
            raise TypeError(
                f"Result type '{storage_type}' is not a valid registered storage"
            ) from exc

        return storage_cls(data=data)

    # ----------------- Store Manager Role Functions ----------------- #
    @restricted_to_role
    def save(self, storage: Storage[Any], **kwargs: Any) -> None:
        """Save a storage object in the store and update movement log."""

        storage_type: StorageType | None = determine_storage_type(storage=storage)
        storage_name = kwargs.get("storage_name")
        agent_name: Optional[str] = kwargs.get("agent_name")
        overwrite: bool = kwargs.get("overwrite", False)
        movement_log: Dict[str, Any] = {}

        try:
            if self._store is None:
                raise ValueError("Missing required argument: 'store'")

            if storage_type is None or storage_type not in self._store.store:
                raise ValueError(
                    f"Storage type '{storage_type}' not managed by this Store."
                )

            if not storage_name:
                raise ValueError("Missing required argument: 'storage_name'")

            if self._store.exists(storage_type, storage_name) and not overwrite:
                logger.warning(
                    "[%s] %s '%s' exists. Use overwrite=True to replace.",
                    self.name,
                    storage_type,
                    storage_name,
                )

                movement_log = {
                    "operation": "save",
                    "storage_type": storage_type,
                    "storage_name": storage_name,
                    "agent_name": agent_name,
                    "success": False,
                    " details": {"reason": "exists"},
                }
                self._log_movement(**movement_log)
                return

            self._generate_save_metadata(storage, storage_name, agent_name)

            self._store.add(
                storage_type, storage, name=storage_name, overwrite=overwrite
            )

            logger.info(
                "[%s] Saved %s '%s' by agent '%s'",
                self.name,
                storage_type,
                storage_name,
                agent_name,
            )

            movement_log = {
                "operation": "save",
                "storage_type": storage_type,
                "storage_name": storage_name,
                "agent_name": agent_name,
                "success": True,
            }
            self._log_movement(**movement_log)

        except Exception as e:
            movement_log = {
                "operation": "save",
                "storage_type": storage_type,
                "storage_name": storage_name or "unknown",
                "agent_name": agent_name,
                "success": False,
                " details": {"error": str(e)},
            }
            self._log_movement(**movement_log)
            raise

    @restricted_to_role
    def get(
        self,
        storage_type: StorageType | Literal["all"] = "all",
        storage_name: str = "all",
    ) -> Union[
        Optional[Storage[Any]],
        Mapping[str, Storage[Any]],
        Mapping[StorageType, Mapping[str, Storage[Any]]],
    ]:
        """Retrieve objects from the store and log the operation."""
        movement_log: Dict[str, Any] = {}

        try:

            if self._store is None:
                raise ValueError("Missing required argument: 'store'")

            result = self._store.get(storage_type, storage_name)
            movement_log = {
                "operation": "get",
                "storage_type": storage_type if storage_type != "all" else "all",
                "storage_name": storage_name,
                "agent_name": None,
                "success": True,
                " details": {"result_type": type(result).__name__},
            }
            self._log_movement(**movement_log)
            return result
        except Exception as e:
            movement_log = {
                "operation": "get",
                "storage_type": storage_type if storage_type != "all" else "all",
                "storage_name": storage_name,
                "agent_name": None,
                "success": False,
                " details": {"error": str(e)},
            }
            self._log_movement(**movement_log)
            raise

    @restricted_to_role
    def remove(
        self,
        storage_type: StorageType | Literal["all"] = "all",
        storage_name: str = "all",
    ) -> Union[
        Optional[Storage[Any]],
        Mapping[str, Storage[Any]],
        Mapping[StorageType, Mapping[str, Storage[Any]]],
    ]:
        """Remove storages from the store and log the operation."""
        try:

            if self._store is None:
                raise ValueError("Missing required argument: 'store'")

            removed = self._store.remove(storage_type, storage_name)
            success = bool(removed)
            details: dict[str, object] = {}
            movement_log: Dict[str, Any] = {}

            if isinstance(removed, dict):
                count = sum(
                    len(v) if isinstance(v, dict) else 1 for v in removed.values()
                )
                details["removed_count"] = count
            elif removed:
                details["removed_count"] = 1
            else:
                details["removed_count"] = 0

            movement_log = {
                "operation": "remove",
                "storage_type": storage_type,
                "storage_name": storage_name,
                "agent_name": None,
                "success": success,
                " details": details,
            }
            self._log_movement(**movement_log)

            if success:
                logger.info(
                    "[%s] Removed object(s) '%s' of type '%s'",
                    self.name,
                    storage_name,
                    storage_type,
                )
            else:
                logger.warning(
                    "[%s] Nothing removed for '%s' (%s)",
                    self.name,
                    storage_name,
                    storage_type,
                )
            return removed
        except Exception as e:
            movement_log = {
                "operation": "remove",
                "storage_type": storage_type,
                "storage_name": storage_name,
                "agent_name": None,
                "success": False,
                " details": {"error": str(e)},
            }
            self._log_movement(**movement_log)
            raise

    @restricted_to_role
    def exists(self, storage_type: StorageType, storage_name: str) -> bool:
        """Check existence of a specific object."""
        if self._store is None:
            raise ValueError("Missing required argument: 'store'")
        return self._store.exists(storage_type, storage_name)

    @restricted_to_role
    def list_all(
        self,
        storage_type: Optional[StorageType] = None,
        fields: Optional[List[str]] = None,
        all_fields: bool = False,
    ) -> Mapping[StorageType, Mapping[str, dict[str, object]]]:
        """
        Return filtered metadata for stored objects, optionally filtered by type.
        """
        default_fields = ["storage_name", "type", "rows", "columns", "checksum"]
        selected_fields = [] if all_fields else (fields or default_fields)

        if self._store is None:
            raise ValueError("Missing required argument: 'store'")

        full_metadata = self._store.list_all(storage_type)
        filtered_list: dict[StorageType, dict[str, dict[str, object]]] = {}

        for t, storages in full_metadata.items():
            filtered_storages: dict[str, dict[str, object]] = {}
            for name, metadata in storages.items():
                if all_fields:
                    filtered_storages[name] = metadata
                else:
                    filtered_storages[name] = {
                        k: v for k, v in metadata.items() if k in selected_fields
                    }
            filtered_list[t] = filtered_storages

        return filtered_list

    # ----------------- Store Manager Interaction ----------------- #
    @restricted_to_role
    def store_result(
        self,
        storage_manager: Any,
        storage: Storage[Any],
        storage_name: str,
    ) -> None:
        """Store a storage (Wagon, Box, Container) via a store manager."""
        storage_type = storage.__class__.__name__
        if storage_type not in list_storages():
            raise ValueError(f"'{storage_type}' is not a valid registered storage type")
        storage_manager.save(
            storage=storage,
            storage_name=storage_name,
            agent_name=self.name,
        )

    # ----------------- Work Pipeline ----------------- #
    @restricted_to_role
    def work(self, style_name: str, **kwargs: Any) -> Storage[Any]:
        """Execute the agent's task using the action and style defined by its role."""

        # ----------------- Deduce action & storage for master -----------------
        if self.role == "master":
            prefix = style_name.split("_")[0]
            self.action = MasterRole.style_prefix_to_action.get(prefix, "mine")
            self.storage_type = MasterRole.style_prefix_to_storage.get(prefix, "Wagon")

        # ----------------- PARAMS fallback -----------------
        params_cls: type[Params] | None = PARAMS_REGISTRY.get((self.role, style_name))
        if not params_cls and self.role == "master":
            for (_, s), params_class in PARAMS_REGISTRY.items():
                if s == style_name:
                    params_cls = params_class
                    break
        if not params_cls:
            raise ValueError(
                f"No Params class registered for ({self.role}, {style_name})"
            )

        params_instance = params_cls(**kwargs)

        # ----------------- STYLE fallback -----------------
        style_key = (self.action, style_name)
        style_cls: type[Style[Any, Any]] | None = STYLE_REGISTRY.get(
            (self.action, style_name)
        )
        if not style_cls and self.role == "master":
            for (_, s), style_class in STYLE_REGISTRY.items():
                if s == style_name:
                    style_cls = style_class
                    break
        if not style_cls:
            raise ValueError(f"No Style class registered for {style_key}")

        # ----------------- Execute style -----------------
        style_instance = style_cls(style_name=style_name)
        stylized_data = style_instance.use(params_instance)
        storage = self.create_storage(stylized_data, style_name=style_name)

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
        return storage

    def __repr__(self) -> str:
        return f"<Agent name={self.name} role={self.role}>"
