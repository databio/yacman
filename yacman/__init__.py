import warnings

from ubiquerg import read_lock as read_lock
from ubiquerg import write_lock as write_lock

from .alias import AliasedYAMLConfigManager as AliasedYAMLConfigManager
from .const import *
from .exceptions import *
from .yacman import (
    YAMLConfigManager,
)
from .yacman import (
    load_yaml as load_yaml,
)
from .yacman import (
    select_config as select_config,
)


# Deprecated alias for backwards compatibility with v0.9.3 transition period
# Will be removed in v1.1.0
def __getattr__(name: str) -> object:
    """Handle deprecated FutureYAMLConfigManager attribute access.

    This function provides backwards compatibility by redirecting access to
    the deprecated FutureYAMLConfigManager to YAMLConfigManager with a
    deprecation warning.

    Args:
        name: The attribute name being accessed.

    Returns:
        YAMLConfigManager if name is 'FutureYAMLConfigManager'.

    Raises:
        AttributeError: If the attribute name is not recognized.
    """
    if name == "FutureYAMLConfigManager":
        warnings.warn(
            "FutureYAMLConfigManager is deprecated and will be removed in v1.1.0. "
            "Please use YAMLConfigManager instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return YAMLConfigManager
    raise AttributeError(f"module 'yacman' has no attribute '{name}'")
