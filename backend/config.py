"""Configuration module for AuthOne.

This module defines a simple ``Settings`` dataclass containing
configuration parameters for the application.  The defaults provided
here are suitable for development but should be overridden via
environment variables or other configuration mechanisms in
production.
"""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["Settings"]


@dataclass
class Settings:
    """Application configuration.

    :param db_url: Database connection string in SQLAlchemy URL format.
    :param log_level: Logging level string (e.g. ``INFO``).
    :param casbin_model_path: Path to the Casbin model configuration file.
    :param casbin_policy_table: Table name for storing Casbin policy rules
        (used by the SQL adapter).  This default matches our migration.
    """

    db_url: str = (
        "postgresql+asyncpg://postgres:123@199.199.199.8:5432/authone"
    )
    log_level: str = "INFO"
    casbin_model_path: str = "rbac_model.conf"
    casbin_policy_table: str = "casbin_rules"

    def override(self, **kwargs: object) -> "Settings":
        """Return a new Settings instance overriding specified fields.

        This method creates a new ``Settings`` by copying this instance's
        fields using ``asdict`` (which supports dataclasses with slots)
        and applying any keyword overrides.  It avoids relying on
        ``__dict__`` so that ``Settings`` can be defined with or without
        ``slots=True``.
        """
        from dataclasses import asdict

        data = asdict(self)
        data.update(kwargs)
        return Settings(**data)