"""
Constant variables for yacman package
"""

FILEPATH_KEY = "_file_path"
RO_KEY = "_ro"
USE_LOCKS_KEY = "_locks"
ORI_STATE_KEY = "_ori_state"
WAIT_MAX_KEY = "_wait_time"
ALIASES_KEY = "__aliases"
ALIASES_KEY_RAW = "__aliases_raw"

ATTR_KEYS = (
    USE_LOCKS_KEY,
    FILEPATH_KEY,
    RO_KEY,
    ORI_STATE_KEY,
    WAIT_MAX_KEY,
    ALIASES_KEY,
    ALIASES_KEY_RAW,
)

LOCK_PREFIX = "lock."
DEFAULT_RO = False
DEFAULT_WAIT_TIME = 60
