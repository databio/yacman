from ._version import __version__
from .alias import *
from .alias_future import AliasedYAMLConfigManager

# Original version (deprecated, kept for backwards compat)
from .yacman import *

# Primary class: YAMLConfigManager now points to FutureYAMLConfigManager
from .yacman_future import FutureYAMLConfigManager as YAMLConfigManager

# Deprecated alias -- downstream code doing `from yacman import FutureYAMLConfigManager` still works
from .yacman_future import FutureYAMLConfigManager

# Utility functions (from the future module)
from .yacman_future import load_yaml, select_config

# Locking context managers
from ubiquerg import read_lock, write_lock
