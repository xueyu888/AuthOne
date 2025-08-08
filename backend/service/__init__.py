"""Service package initialisation.

This package exposes the ``AuthService`` class which provides all
business operations for managing permissions, roles, groups,
accounts and resources.  See ``backend.service.auth_service`` for
details.
"""

from __future__ import annotations

from .auth_service import AuthService

__all__ = ["AuthService"]