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

from .function import FraguaFunction


__all__ = [
    # Agent Class
    "Agent",
    # Params class
    "Params",
    # Function class
    "FraguaFunction",
]
