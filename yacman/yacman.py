import os
from collections.abc import Iterable
import oyaml as yaml
import logging
import warnings

import attmap
from ubiquerg import make_lock_path, mkabs, is_url, create_lock, remove_lock

from .const import *

_LOGGER = logging.getLogger(__name__)


# Hack for string indexes of both ordered and unordered yaml representations
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
    return {
        (str(key) if isinstance(key, float) or isinstance(key, int) else key): data[key]
        for key in data
    }


def my_construct_pairs(self, node, deep=False):
    pairs = []
    for key_node, value_node in node.value:
        key = str(self.construct_object(key_node, deep=deep))
        value = self.construct_object(value_node, deep=deep)
        pairs.append((key, value))
    return pairs


yaml.SafeLoader.construct_mapping_org = yaml.SafeLoader.construct_mapping
yaml.SafeLoader.construct_mapping = my_construct_mapping
yaml.SafeLoader.construct_pairs = my_construct_pairs
# End hack


class YacAttMap(attmap.PathExAttMap):
    """
    A class that extends AttMap to provide yaml reading and race-free writing in multi-user contexts.

    The YacAttMap class is a YAML Configuration Attribute Map. Think of it as a python representation of your YAML
    configuration file, that can do a lot of cool stuff. You can access the hierarchical YAML attributes with dot
    notation or dict notation. You can read and write YAML config files with easy functions. It also retains memory
    of the its source filepath. If both a filepath and an entries dict are provided, it will first load the file
    and then updated it with values from the dict.
    """

    def __init__(
        self,
        entries=None,
        filepath=None,
        yamldata=None,
        writable=False,
        wait_max=DEFAULT_WAIT_TIME,
        skip_read_lock=False,
    ):
        """
        Object constructor

        :param Iterable[(str, object)] | Mapping[str, object] entries: YAML collection of key-value pairs.
        :param str filepath: YAML filepath to the config file.
        :param str yamldata: YAML-formatted string
        :param bool writable: whether to create the object with write capabilities
        :param int wait_max: how long to wait for creating an object when the file that data will be read from is locked
        :param bool skip_read_lock: whether the file should not be locked for reading when object is created in read only mode
        """
        if writable:
            if filepath:
                create_lock(filepath, wait_max)
            else:
                warnings.warn(
                    "Argument 'writable' is disregarded when the object is created with 'entries' rather than"
                    " read from the 'filepath'",
                    UserWarning,
                )
        if filepath:
            if not skip_read_lock and not writable and os.path.exists(filepath):
                create_lock(filepath, wait_max)
                file_contents = load_yaml(filepath)
                remove_lock(filepath)
            else:
                file_contents = load_yaml(filepath)
            if entries:
                file_contents.update(entries)
            entries = file_contents
        elif yamldata:
            entries = yaml.load(yamldata, yaml.SafeLoader)
        super(YacAttMap, self).__init__(entries or {})
        if filepath:
            # to make this python2 compatible, the attributes need to be set here.
            # prevents: AttributeError: _OrderedDict__root
            setattr(self, WAIT_MAX_KEY, wait_max)
            setattr(self, FILEPATH_KEY, mkabs(filepath))
            setattr(self, RO_KEY, not writable)

    def __del__(self):
        if hasattr(self, FILEPATH_KEY) and not getattr(self, RO_KEY, True):
            self.make_readonly()

    def __repr__(self):
        # Here we want to render the data in a nice way; and we want to indicate
        # the class if it's NOT a YacAttMap. If it is a YacAttMap we just want
        # to give you the data without the class name.
        return self._render(
            self._simplify_keyvalue(self._data_for_repr(), self._new_empty_basic_map),
            exclude_class_list="YacAttMap",
        )

    def __enter__(self):
        setattr(self, ORI_STATE_KEY, getattr(self, RO_KEY, True))
        if self.writable:
            return self
        else:
            self.make_writable()
            return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.write()
        if getattr(self, ORI_STATE_KEY, False):
            self.make_readonly()

    def _reinit(self, filepath=None):
        """
        Re-initialize the object

        :param str filepath: path to the file that should be read
        """
        if filepath is not None:
            self.__init__(filepath=filepath, skip_read_lock=True)
        else:
            self.__init__(entries={}, skip_read_lock=True)

    def _excl_from_repr(self, k, cls):
        return k in ATTR_KEYS

    @property
    def _lower_type_bound(self):
        """ Most specific type to which an inserted value may be converted """
        return YacAttMap

    def write(self, filepath=None):
        """
        Write the contents to a file.

        Make sure that the object has been created with write capabilities

        :param str filepath: a file path to write to
        :raise OSError: when the object has been created in a read only mode or other process has locked the file
        :raise TypeError: when the filepath cannot be determined.
            This takes place only if YacAttMap initialized with a Mapping as an input, not read from file.
        :raise OSError: when the write is called on an object with no write capabilities
            or when writing to a file that is locked by a different object
        :return str: the path to the created files
        """
        if getattr(self, RO_KEY, False):
            raise OSError(
                "You can't call write on an object that was created in read-only mode."
            )
        filepath = _check_filepath(filepath or getattr(self, FILEPATH_KEY, None))
        lock = make_lock_path(filepath)
        if filepath != getattr(self, FILEPATH_KEY, None):
            if os.path.exists(filepath):
                if not os.path.exists(lock):
                    warnings.warn(
                        "Writing to a non-locked, existing file. Beware of collisions.",
                        UserWarning,
                    )
                else:
                    raise OSError(
                        "The file '{}' is locked by a different process".format(
                            filepath
                        )
                    )
            if getattr(self, FILEPATH_KEY, None):
                self.make_readonly()
            setattr(self, FILEPATH_KEY, filepath)
            create_lock(filepath, getattr(self, WAIT_MAX_KEY, DEFAULT_WAIT_TIME))
        setattr(self, RO_KEY, False)
        with open(filepath, "w") as f:
            f.write(self.to_yaml())
        _LOGGER.debug("Wrote to a file: {}".format(os.path.abspath(filepath)))
        return os.path.abspath(filepath)

    @staticmethod
    def _remove_lock(filepath):
        """
        Remove lock

        :param str filepath: path to the file to remove the lock for. Not the path to the lock!
        :return bool: whether the lock was found and removed
        """
        lock = make_lock_path(_check_filepath(filepath))
        if os.path.exists(lock):
            os.remove(lock)
            return True
        return False

    def make_readonly(self):
        """
        Remove lock and make the object read only.

        :return bool: a logical indicating whether any locks were removed
        """
        if self._remove_lock(getattr(self, FILEPATH_KEY, None)):
            setattr(self, RO_KEY, True)
            _LOGGER.debug("Made object read-only")
            return True
        return False

    def make_writable(self, filepath=None):
        """
        Grant write capabilities to the object and re-read the file.

        Any changes made to the attributes are overwritten so that the object
        reflects the contents of the specified config file

        :param str filepath: path to the file that the contents will be written to
        :return YacAttMap: updated object
        """
        if not getattr(self, RO_KEY, True):
            _LOGGER.info(
                "Object is already writable, path: {}".format(
                    getattr(self, FILEPATH_KEY, None)
                )
            )
            return self
        ori_fp = getattr(self, FILEPATH_KEY, None)
        if filepath and ori_fp != filepath:
            # file path has changed, unlock the previously used file if exists
            if ori_fp:
                self._remove_lock(ori_fp)
        filepath = _check_filepath(filepath or ori_fp)
        create_lock(filepath, getattr(self, WAIT_MAX_KEY, DEFAULT_WAIT_TIME))
        try:
            self._reinit(filepath)
        except OSError:
            _LOGGER.debug("File '{}' not found".format(filepath))
            pass
        except Exception as e:
            self._reinit()
            _LOGGER.info(
                "File '{}' was not read, got an exception: {}".format(filepath, e)
            )
        setattr(self, RO_KEY, False)
        setattr(self, FILEPATH_KEY, filepath)
        _LOGGER.debug("Made object writable")
        return self

    @property
    def file_path(self):
        """
        Return the path to the config file or None if not set

        :return str | None: path to the file the object will would to
        """
        return getattr(self, FILEPATH_KEY, None)

    @property
    def writable(self):
        """
        Return writability flag or None if not set

        :return bool | None: whether the object is writable now
        """
        attr = getattr(self, RO_KEY, None)
        return attr if attr is None else not attr


def _check_filepath(filepath):
    """
    Validate if the filepath attr/arg is a str

    :param str filepath: object to validate
    :return str: validated filepath
    :raise TypeError: if the filepath is not a string
    """
    # might be useful if we want to have multiple locked paths in the future
    # def _check_string(obj):
    #     """ check if object is a string or a list of strings """
    #     return bool(obj) and all(isinstance(elem, str) for elem in obj)
    if not isinstance(filepath, str):
        raise TypeError(
            "No valid filepath provided. It has to be a str, "
            "got: {}".format(filepath.__class__.__name__)
        )
    return filepath


def load_yaml(filepath):
    """ Load a yaml file into a python dict """

    def read_yaml_file(filepath):
        """
        Read a YAML file

        :param str filepath: path to the file to read
        :return dict: read data
        """
        with open(filepath, "r") as f:
            data = yaml.safe_load(f)
        return data

    if is_url(filepath):
        _LOGGER.debug("Got URL: {}".format(filepath))
        try:  # python3
            from urllib.request import urlopen
            from urllib.error import HTTPError
        except:  # python2
            from urllib2 import urlopen
            from urllib2 import URLError as HTTPError
        try:
            response = urlopen(filepath)
        except HTTPError as e:
            raise e
        data = response.read()  # a `bytes` object
        text = data.decode("utf-8")
        return yaml.safe_load(text)
    else:
        return read_yaml_file(filepath)


def get_first_env_var(ev):
    """
    Get the name and value of the first set environment variable

    :param str | Iterable[str] ev: a list of the environment variable names
    :return (str, str): name and the value of the environment variable
    """
    if isinstance(ev, str):
        ev = [ev]
    elif not isinstance(ev, Iterable):
        raise TypeError(
            "Env var must be single name or collection of names; "
            "got {}".format(type(ev))
        )
    # TODO: we should handle the null (not found) case, as client code is inclined to unpack, and ValueError guard is vague.
    for v in ev:
        try:
            return v, os.environ[v]
        except KeyError:
            pass


def select_config(
    config_filepath=None,
    config_env_vars=None,
    default_config_filepath=None,
    check_exist=True,
    on_missing=lambda fp: IOError(fp),
    strict_env=False,
):
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
    :param bool strict_env: whether to raise an exception if no file path provided
        and environment variables do not point to any files
    raise: OSError: when strict environment variables validation is not passed
    """

    # First priority: given file
    if config_filepath:
        config_filepath = os.path.expandvars(config_filepath)
        if not check_exist or os.path.isfile(config_filepath):
            return os.path.abspath(config_filepath)
        _LOGGER.error("Config file path isn't a file: {}".format(config_filepath))
        result = on_missing(config_filepath)
        if isinstance(result, Exception):
            raise result
        return os.path.abspath(result)

    _LOGGER.debug("No local config file was provided")
    selected_filepath = None

    # Second priority: environment variables (in order)
    if config_env_vars:
        _LOGGER.debug("Checking for environment variable: {}".format(config_env_vars))

        cfg_env_var, cfg_file = get_first_env_var(config_env_vars) or ["", ""]

        if not check_exist or os.path.isfile(cfg_file):
            _LOGGER.debug("Found config file in {}: {}".format(cfg_env_var, cfg_file))
            selected_filepath = cfg_file
        if selected_filepath is None and cfg_file and strict_env:
            raise OSError(
                "Environment variable ({}) does not point to any existing file: {}".format(
                    ", ".join(config_env_vars), cfg_file
                )
            )
    if selected_filepath is None:
        # Third priority: default filepath
        _LOGGER.info(
            "Using default config. No config found in env var: {}".format(
                str(config_env_vars)
            )
        )
        return default_config_filepath
    return (
        os.path.abspath(selected_filepath) if selected_filepath else selected_filepath
    )
