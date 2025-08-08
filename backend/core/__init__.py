"""Core package initialisation.

This package exposes the ``AuthEngine`` which wraps the Casbin
engine.  See ``backend.core.auth_engine`` for details.
"""

from __future__ import annotations

from .auth_engine import AuthEngine

__all__ = ["AuthEngine"]