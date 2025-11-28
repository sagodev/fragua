"""
Base classes module.

This module contains:
- Base Agent class.
- Base Params class.
- Base Style class.
- Base FraguaFunction class.
"""

from .agent import Agent

from .function import FraguaFunction

__all__ = [
    # Agent Class
    "Agent",
    # Function class
    "FraguaFunction",
]
