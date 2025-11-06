"""Constant variables for yacman package.

This module defines all constant keys and default values used throughout
the yacman package for configuration management.
"""

FILEPATH_KEY: str = "file_path"
RO_KEY: str = "ro"
USE_LOCKS_KEY: str = "locks"
ORI_STATE_KEY: str = "ori_state"
WAIT_MAX_KEY: str = "wait_time"
ALIASES_KEY: str = "aliases"
ALIASES_KEY_RAW: str = "aliases_raw"
WRITE_VALIDATE_KEY: str = "write_validate"
SCHEMA_KEY: str = "schema"

ATTR_KEYS: tuple[str, ...] = (
    USE_LOCKS_KEY,
    FILEPATH_KEY,
    RO_KEY,
    ORI_STATE_KEY,
    WAIT_MAX_KEY,
    ALIASES_KEY,
    ALIASES_KEY_RAW,
    WRITE_VALIDATE_KEY,
    SCHEMA_KEY,
)

LOCK_PREFIX: str = "lock."
DEFAULT_RO: bool = False
DEFAULT_WAIT_TIME: int = 60
