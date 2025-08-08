"""Top-level package for AuthOne.

This module aggregates the primary entry points of the AuthOne
library.  Consumers should import from this module rather than from
submodules wherever possible.  Only symbols listed in ``__all__`` are
considered part of the public API; others are considered internal
implementation details and may change without notice.
"""

from __future__ import annotations

from ._version import __version__  # type: ignore[F401]
from .config import Settings
from .models import AccessCheckRequest, AccessCheckResponse
from .service import AuthService

__all__: list[str] = [
    "__version__",
    "Settings",
    "AccessCheckRequest",
    "AccessCheckResponse",
    "AuthService",
]