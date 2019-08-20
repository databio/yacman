import attmap
import os
from collections import Iterable
import oyaml as yaml
import logging

_LOGGER = logging.getLogger(__name__)


FILEPATH_KEY = "_file_path"


### Hack for string indexes of both ordered and unordered yaml representations
# Credit: Anthon
# https://stackoverflow.com/questions/50045617
# https://stackoverflow.com/questions/5121931
# The idea is: if you have yaml keys that can be interpreted as an int or a float,
# then the yaml loader will convert them into an int or a float, and you would
# need to access them with dict[2] instead of dict['2']. But since we always
# expect the keys to be strings, this doesn't work. So, here we are adjusting
# the loader to keep everything as a string. This happens in 2 ways, so that
# it's compatible with both yaml and oyaml, which is the orderedDict version.
# this will go away in python 3.7, because the dict representations will be
# ordered by default.
def my_construct_mapping(self, node, deep=False):
    data = self.construct_mapping_org(node, deep)
    return {(str(key) if isinstance(key, float) or isinstance(key, int) else key): data[key] for key in data}

def my_construct_pairs(self, node, deep=False):
    # if not isinstance(node, MappingNode):
    #     raise ConstructorError(None, None,
    #             "expected a mapping node, but found %s" % node.id,
    #             node.start_mark)
    pairs = []
    for key_node, value_node in node.value:
        key = str(self.construct_object(key_node, deep=deep))
        value = self.construct_object(value_node, deep=deep)
        pairs.append((key, value))
    return pairs

yaml.SafeLoader.construct_mapping_org = yaml.SafeLoader.construct_mapping
yaml.SafeLoader.construct_mapping = my_construct_mapping
yaml.SafeLoader.construct_pairs = my_construct_pairs
### End hack


class YacAttMap(attmap.PathExAttMap):
    """
    A class that extends AttMap to provide yaml reading and writing.

    The YacAttMap class is a YAML Configuration Attribute Map. Think of it as a
    python representation of your YAML configuration file, that can do a lot of
    cool stuff. You can access the hierarchical YAML attributes with dot
    notation or dict notation. You can read and write YAML config files with
    easy functions. It also retains memory of the its source filepath. If both a
    filepath and an entries dict are provided, it will first load the file
    and then updated it with values from the dict.

    :param str | Iterable[(str, object)] | Mapping[str, object] entries: YAML
        filepath or collection of key-value pairs.
    :param str filepath: YAML filepath to the config file.
    """

    def __init__(self, entries=None, filepath=None, yamldata=None):

        if isinstance(entries, str):
            # If user provides a string, it's probably a filename we should read
            # This should be removed at a major version release now that the
            # filepath argument exists, but we retain it for backwards
            # compatibility
            _LOGGER.debug("The entries argument should be a dict. If you want"
            " to read a file, use the filepath arg")
            filepath = entries
            entries = None

        if filepath:
            file_contents = load_yaml(filepath)
            if entries:
                file_contents.update(entries)

            entries = file_contents

        if yamldata:
            entries = yaml.load(yamldata, yaml.SafeLoader)

        super(YacAttMap, self).__init__(entries or {})
        if filepath:
            setattr(self, FILEPATH_KEY, filepath)

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

    def __repr__(self):
        # Here we want to render the data in a nice way; and we want to indicate
        # the class if it's NOT a YacAttMap. If it is a YacAttMap we just want
        # to give you the data without the class name.
        return self._render(self._simplify_keyvalue(
            self._data_for_repr(), self._new_empty_basic_map),
            exclude_class_list="YacAttMap")


def load_yaml(filename):
    with open(filename, 'r') as f:
        data = yaml.safe_load(f)
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


def select_config(config_filepath=None,
                  config_env_vars=None,
                  default_config_filepath=None,
                  check_exist=True,
                  on_missing=lambda fp: IOError(fp)):
    """
    Selects the config file to load.

    This uses a priority ordering to first choose a config filepath if it's given,
    but if not, then look in a priority list of environment variables and choose
    the first available filepath to return.

    :param str | NoneType config_filepath: direct filepath specification
    :param Iterable[str] | NoneType config_env_vars: names of environment
        variables to try for config filepaths
    :param str default_config_filepath: default value if no other alternative
        resolution succeeds
    :param bool check_exist: whether to check for path existence as file
    :param function(str) -> object on_missing: what to do with a filepath if it
        doesn't exist
    """

    # First priority: given file
    if config_filepath:
        if not check_exist or os.path.isfile(config_filepath):
            return config_filepath
        _LOGGER.error("Config file path isn't a file: {}".
                      format(config_filepath))
        result = on_missing(config_filepath)
        if isinstance(result, Exception):
            raise result
        return result

    _LOGGER.debug("No local config file was provided")
    selected_filepath = None

    # Second priority: environment variables (in order)
    if config_env_vars:
        _LOGGER.debug("Checking for environment variable: {}".format(config_env_vars))

        cfg_env_var, cfg_file = get_first_env_var(config_env_vars) or ["", ""]

        if not check_exist or os.path.isfile(cfg_file):
            _LOGGER.debug("Found config file in {}: {}".
                          format(cfg_env_var, cfg_file))
            selected_filepath = cfg_file
        else:
            _LOGGER.info("Using default config. No config found in env "
                         "var: {}".format(str(config_env_vars)))
            selected_filepath = default_config_filepath
    else:
        _LOGGER.error("No configuration file found.")

    return selected_filepath


def single_folder_writeable(d):
    return os.access(d, os.W_OK) and os.access(d, os.X_OK)


def writeable(outdir, strict_exists=False):
    """
    Recursively checks to make sure a folder exists and can be  written to.  
    """
    outdir = outdir or "."
    if os.path.exists(outdir):
        return _single_folder_writeable(outdir)
    elif strict_exists:
        raise MissingFolderError(outdir)
    return writeable(os.path.dirname(outdir), strict_exists)

