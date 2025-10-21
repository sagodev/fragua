"""
Base abstract class for all parameter schemas used by styles in Fragua.
"""

from pydantic import BaseModel


class BaseParams(BaseModel):
    """Base configuration model shared by all params."""

    class Config:
        """Configuration for the BaseParams model."""

        arbitrary_types_allowed = True  # Allows DataFrame
        extra = "forbid"  # Forbid unexpected fields (strict)
