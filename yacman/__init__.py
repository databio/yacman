import warnings

from ._version import __version__
from .alias import AliasedYAMLConfigManager
from .const import *
from .exceptions import *
from .yacman import YAMLConfigManager, select_config, load_yaml
from ubiquerg import read_lock, write_lock


# Deprecated alias for backwards compatibility with v0.9.3 transition period
# Will be removed in v1.1.0
def __getattr__(name):
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
            stacklevel=2
        )
        return YAMLConfigManager
    raise AttributeError(f"module 'yacman' has no attribute '{name}'")
