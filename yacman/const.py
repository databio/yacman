"""
Constant variables for yacman package
"""

FILEPATH_KEY = "__file_path"
RO_KEY = "__ro"
USE_LOCKS_KEY = "__locks"
ORI_STATE_KEY = "__ori_state"
WAIT_MAX_KEY = "__wait_time"
ALIASES_KEY = "__aliases"
ALIASES_KEY_RAW = "__aliases_raw"
WRITE_VALIDATE_KEY = "__write_validate"
SCHEMA_KEY = "__schema"

ATTR_KEYS = (
    USE_LOCKS_KEY,
    FILEPATH_KEY,
    RO_KEY,
    ORI_STATE_KEY,
    WAIT_MAX_KEY,
    ALIASES_KEY,
    ALIASES_KEY_RAW,
    WRITE_VALIDATE_KEY,
    SCHEMA_KEY
)

LOCK_PREFIX = "lock."
DEFAULT_RO = False
DEFAULT_WAIT_TIME = 60
