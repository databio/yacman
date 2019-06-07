import attmap
import os
from collections import Iterable
import oyaml as yaml
import logging

_LOGGER = logging.getLogger(__name__)


FILEPATH_KEY = "_file_path"


class YacAttMap(attmap.PathExAttMap):
    """
    A class that extends AttMap to provide yaml reading and writing
    """

    def __init__(self, entries=None):

        if isinstance(entries, str):
            # If user provides a string, it's probably a filename we should read
            fp = entries
            entries = load_yaml(entries)
        else:
            fp = None
        super(YacAttMap, self).__init__(entries or {})
        if fp:
            setattr(self, FILEPATH_KEY, fp)

    def write(self, filename=None):
        filename = filename or getattr(self, FILEPATH_KEY)
        if not filename:
            raise Exception("No filename provided.")
        with open(filename, 'w') as f:
            f.write(self.to_yaml())
        return os.path.abspath(filename)

    @property
    def _lower_type_bound(self):
        """ Most specific type to which an inserted value may be converted """
        return YacAttMap

    def _excl_from_repr(self, k, cls):
        return k == FILEPATH_KEY


def load_yaml(filename):
    with open(filename, 'r') as f:
        data = yaml.load(f, yaml.SafeLoader)
    return data


def get_first_env_var(ev):
    """
    Get the name and value of the first set environment variable

    :param str | Iterable[str] ev: a list of the environment variable names
    :return (str, str): name and the value of the environment variable
    """
    if isinstance(ev, str):
        ev = [ev]
    elif not isinstance(ev, Iterable):
        raise TypeError("Env var must be single name or collection of names; "
                        "got {}".format(type(ev)))
    # TODO: we should handle the null (not found) case, as client code is inclined to unpack, and ValueError guard is vague.
    for v in ev:
        try:
            return v, os.environ[v]
        except KeyError:
            pass


def select_config(config_filepath=None, config_env_vars=None,
                  default_config_filepath=None):
    """
    Selects the config file to load.

    This uses a priority ordering to first choose a config filepath if it's given,
    but if not, then look in a priority list of environment variables and choose
    the first available filepath to return.

    """
    selected_filepath = None

    # First priority: given file
    if config_filepath:
        if not os.path.isfile(config_filepath):
            _LOGGER.error("Config file path isn't a file: {}".
                          format(config_filepath))
            raise IOError(config_filepath)
        else:
            selected_filepath = config_filepath
    else:
        _LOGGER.debug("No local config file was provided")
        # Second priority: environment variables (in priority order)
        if config_env_vars:
            _LOGGER.debug("Checking for environment variable: {}".format(config_env_vars))

            cfg_env_var, cfg_file = get_first_env_var(config_env_vars) or ["", ""]

            if os.path.isfile(cfg_file):
                _LOGGER.debug("Found config file in {}: {}".
                             format(cfg_env_var, cfg_file))
                selected_filepath = cfg_file
            else:
                _LOGGER.info("Using default config file, no global config file provided in environment "
                             "variable(s): {}".format(str(config_env_vars)))
                selected_filepath = default_config_filepath
        else:
            _LOGGER.error("No configuration file found.")

    return selected_filepath
