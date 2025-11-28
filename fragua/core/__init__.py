"""
Base classes module.

This module contains:
- Base Agent class.
- Base Params class.
- Base Style class.
- Base FraguaFunction class.
"""

from .agent import Agent

from .params import Params

from .style import Style

from .function import FraguaFunction


__all__ = [
    # Agent Class
    "Agent",
    # Params Class
    "Params",
    # Style Class
    "Style",
    # Function Class
    "FraguaFunction",
]
