"""Fragua Core module"""

# ------------------- Store ------------------- #
from .store import Store

# ------------------- Style ------------------- #
from .style import Style, register_style, get_style, list_styles

# ------------------- Storage ------------------- #
from .storage import Storage, register_storage, get_storage, list_storages

# ------------------- Params ------------------- #
from .params import Params, register_params

# ------------------- __all__ ------------------- #
__all__ = [
    # Store
    "Store",
    # Style
    "Style",
    "register_style",
    "get_style",
    "list_styles",
    # Storage
    "Storage",
    "register_storage",
    "get_storage",
    "list_storages",
    # Params
    "Params",
    "register_params",
]
