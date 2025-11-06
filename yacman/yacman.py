import logging
import os
import yaml

from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any, Callable
from jsonschema import validate as _validate
from jsonschema.exceptions import ValidationError
from ubiquerg import (
    expandpath,
    is_url,
    ThreeLocker,
    ensure_locked,
    locked_read_file,
    READ,
    WRITE,
)

from ._version import __version__

_LOGGER = logging.getLogger(__name__)
_LOGGER.debug(f"Using yacman version {__version__}")

# Custom YAML Loader for String Keys
#
# We use a custom loader to ensure all dictionary keys are strings, even when
# they appear as numbers in the YAML source. This provides consistent access
# patterns: config["2"] always works, even if the YAML has `2: value`.
#
# Credit: Based on approach from https://stackoverflow.com/questions/50045617


class YacmanLoader(yaml.SafeLoader):
    """Custom YAML loader that forces all dict keys to be strings.

    This ensures consistent key access patterns in config files, even when
    keys look like numbers (e.g., 2, 3.14) in the YAML source.

    Example:
        YAML source `2: value` loads as {"2": "value"} not {2: "value"}
    """

    pass


def _construct_mapping_string_keys(
    loader: yaml.Loader, node: yaml.Node
) -> dict[str, object]:
    """Construct a mapping with all keys coerced to strings.

    Args:
        loader: The YAML loader instance.
        node: The YAML node to construct.

    Returns:
        Dictionary with all keys converted to strings.
    """
    # Use the parent class's construct_pairs to get key-value tuples
    loader.flatten_mapping(node)
    pairs = loader.construct_pairs(node)

    # Convert all numeric keys to strings
    return {
        (str(key) if isinstance(key, (int, float)) else key): value
        for key, value in pairs
    }


# Register the custom constructor for mappings
YacmanLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping_string_keys
)

# Constants: to do, remove these

DEFAULT_WAIT_TIME = 60
# LOCK_PREFIX = "lock."
SCHEMA_KEY = "schema"
FILEPATH_KEY = "file_path"

from collections.abc import MutableMapping

# Since read and write are now different context managers, we have to
# separate them like this, instead of using __enter__ and __exit__ on the class
# itself, which only allows one type of context manager.


class YAMLConfigManager(MutableMapping):
    """A YAML configuration manager.

    Provides file locking, loading, writing, etc. for YAML configuration files.
    """

    def __init__(
        self,
        entries: dict[str, Any] | list[Any] | None = None,
        wait_max: int = DEFAULT_WAIT_TIME,
        strict_ro_locks: bool = False,
        schema_source: str | Path | None = None,
        validate_on_write: bool = False,
    ) -> None:
        """Object constructor.

        Args:
            entries: YAML collection of key-value pairs.
            wait_max: How long to wait for creating an object when the file
                that data will be read from is locked.
            strict_ro_locks: By default, we allow RO filesystems that can't
                be locked. Turn on strict_ro_locks to error if locks cannot
                be enforced on readonly filesystems.
            schema_source: Path or a URL to a jsonschema in YAML format to use
                for optional config validation. If this argument is provided
                the object is always validated at least once, at the object
                creation stage.
            validate_on_write: A boolean indicating whether the object should
                be validated every time the `write` method is executed, which
                is a way of preventing invalid config writing.
        """

        # Settings for this config object
        self.filepath: str | None = None
        self.wait_max: int = wait_max
        self.schema_source: str | Path | None = schema_source
        self.validate_on_write: bool = validate_on_write
        self.strict_ro_locks: bool = strict_ro_locks
        self.locker: Any = None  # ThreeLocker type not available

        # We store the values in a dict under .data
        # Note: entries can be list/dict/etc but data is always dict for MutableMapping protocol
        self.data: dict[str, Any]
        if isinstance(entries, list):
            self.data = {
                str(i): v for i, v in enumerate(entries)
            }  # Convert list to dict
        else:
            self.data = dict(entries or {})
        if schema_source is not None:
            assert isinstance(schema_source, str), TypeError(
                f"Path to the schema to validate the config must be a string"
            )
            sp = expandpath(schema_source)
            assert os.path.exists(sp), FileNotFoundError(
                f"Provided schema file does not exist: {schema_source}."
                f" Also tried: {sp}"
            )
            # validate config
            setattr(self, SCHEMA_KEY, load_yaml(sp))
            self.validate()

    @classmethod
    def from_obj(
        cls, entries: dict[str, Any] | list[Any] | None, **kwargs
    ) -> "YAMLConfigManager":
        """Initialize from a Python object (dict, list, or primitive).

        Args:
            entries: Object to initialize from.
            **kwargs: Keyword arguments to pass to the constructor.

        Returns:
            New instance of the class.
        """
        return cls(entries, **kwargs)

    @classmethod
    def from_yaml_data(cls, yamldata: str, **kwargs) -> "YAMLConfigManager":
        """Initialize from a YAML string.

        Args:
            yamldata: YAML-formatted string.
            **kwargs: Keyword arguments to pass to the constructor.

        Returns:
            New instance of the class.
        """
        entries = yaml.load(yamldata, YacmanLoader)
        return cls(entries, **kwargs)

    @classmethod
    def from_yaml_file(
        cls, filepath: str | Path, create_file: bool = False, **kwargs
    ) -> "YAMLConfigManager":
        """Initialize from a YAML file.

        Args:
            filepath: Path to the YAML config file.
            create_file: Create a file at filepath if it doesn't exist.
            **kwargs: Keyword arguments to pass to the constructor.

        Returns:
            New instance of the class.
        """

        file_contents = locked_read_file(filepath, create_file=create_file)
        entries = yaml.load(file_contents, YacmanLoader)
        ref = cls(entries, **kwargs)
        ref.locker = ThreeLocker(filepath)
        ref.filepath = str(filepath)
        return ref

    def update_from_yaml_file(
        self, filepath: str | Path | None = None
    ) -> "YAMLConfigManager":
        """Update the object's data from a YAML file.

        Args:
            filepath: Path to the YAML file to update from. If provided and
                the object's filepath is not set, sets the object's filepath.
        """
        if filepath is not None:  # set filepath to update filepath if uninitialized
            if self.filepath is None:
                self.filepath = str(filepath)
            self.data.update(load_yaml(filepath))
        return self

    def update_from_yaml_data(self, yamldata: str | None = None) -> "YAMLConfigManager":
        """Update the object's data from a YAML string.

        Args:
            yamldata: YAML-formatted string to update from.
        """
        if yamldata is not None:
            self.data.update(yaml.load(yamldata, YacmanLoader))
        return self

    def update_from_obj(
        self, entries: dict[str, Any] | None = None
    ) -> "YAMLConfigManager":
        """Update the object's data from a Python object.

        Args:
            entries: Object (dict, list, or primitive) to update from.
        """
        if entries is not None:
            self.data.update(entries)
        return self

    @property
    def locked(self) -> bool:
        """Check if the file is currently locked.

        Returns:
            True if the locker exists and is locked, False otherwise.
        """
        if self.locker is None:
            return False
        return self.locker.locked

    @property
    def settings(self) -> dict[str, Any]:
        """Get the configuration settings for this object.

        Returns:
            Dictionary containing wait_max, schema_source, validate_on_write,
            locked, and strict_ro_locks settings.
        """
        return {
            "wait_max": self.wait_max,
            "schema_source": self.schema_source,
            "validate_on_write": self.validate_on_write,
            "locked": self.locked,
            "strict_ro_locks": self.strict_ro_locks,
        }

    def __del__(self) -> None:
        """Destructor that cleans up the locker if it exists."""
        if hasattr(self, "locker"):
            del self.locker

    def __repr__(self) -> str:
        """Return string representation of the object.

        Returns:
            YAML representation of the object's data.
        """
        # Render the data in a nice way
        return self.to_yaml()

    def __enter__(self):
        """Context manager entry not supported.

        Raises:
            NotImplementedError: Always raised; use 'read_lock' and 'write_lock'
                context managers instead.
        """
        raise NotImplementedError(
            "Use the 'read_lock' and 'write_lock' context managers."
        )

    def __exit__(self):
        """Context manager exit not supported.

        Raises:
            NotImplementedError: Always raised; use 'read_lock' and 'write_lock'
                context managers instead.
        """
        raise NotImplementedError(
            "Use the 'read_lock' and 'write_lock' context managers."
        )

    @ensure_locked(READ)
    def rebase(self, filepath: str | Path | None = None) -> "YAMLConfigManager":
        """Reload the object from file, then update with current information.

        Args:
            filepath: Path to the file that should be read. If not provided,
                uses the object's current filepath.

        Returns:
            Self for chaining.
        """
        assert self.locker is not None
        fp = filepath or self.locker.filepath
        if fp is not None:
            local_data = self.data
            self.data = load_yaml(fp)
            _LOGGER.debug(f"Rebased {local_data} with {self.data} from {fp}")
            if self.data is None:
                self.data = local_data
            else:
                deep_update(self.data, local_data)
        else:
            _LOGGER.warning("Rebase has no effect if no filepath given")

        return self

    @ensure_locked(READ)
    def reset(self, filepath: str | Path | None = None) -> "YAMLConfigManager":
        """Reset dict contents to file contents, or to empty dict if no filepath found.

        Args:
            filepath: Path to the file that should be read. If not provided,
                uses the object's current filepath.

        Returns:
            Self for chaining.
        """
        assert self.locker is not None
        fp = filepath or self.locker.filepath
        if fp is not None:
            self.data = load_yaml(fp)
        else:
            self.data = {}
        return self

    def validate(
        self, schema: dict[str, Any] | None = None, exclude_case: bool = False
    ) -> bool:
        """Validate the object against a schema.

        Args:
            schema: A schema object to use to validate. It overrides the one
                that has been provided at object construction stage.
            exclude_case: Whether to exclude validated objects from the error.
                Useful when used with large configs.

        Raises:
            ValidationError: If the object does not pass schema validation.
        """
        try:
            _validate(self.to_dict(expand=True), schema or getattr(self, SCHEMA_KEY))
        except ValidationError as e:
            _LOGGER.error(
                f"{self.__class__.__name__} object did not pass schema validation"
            )
            # if getattr(self, FILEPATH_KEY, None) is not None:
            # need to unlock locked files in case of validation error so that no
            # locks are left in place
            # self.make_readonly()
            # commented out because I think this is taken care of my context managers now
            if not exclude_case:
                raise
            raise ValidationError(
                f"{self.__class__.__name__} object did not pass schema validation: "
                f"{e.message}"
            )
        _LOGGER.debug("Validated successfully")
        return True

    @ensure_locked(WRITE)
    def write(
        self, schema: dict[str, Any] | None = None, exclude_case: bool = False
    ) -> str:
        """Write the contents to the file backing this object.

        Args:
            schema: A schema object to use to validate. It overrides the one
                that has been provided at object construction stage.
            exclude_case: Whether to exclude validated objects from the error.
                Useful when used with large configs.

        Returns:
            The absolute path to the written file.

        Raises:
            OSError: When the object has been created in a read only mode or
                other process has locked the file, or when the write is called
                on an object with no write capabilities or when writing to a
                file that is locked by a different object.
            TypeError: When the filepath cannot be determined.
        """
        assert self.locker is not None
        if not self.locker.filepath:
            raise OSError("Must provide a filepath to write.")

        _check_filepath(self.locker.filepath)
        _LOGGER.debug(f"Writing to file '{self.locker.filepath}'")
        with open(self.locker.filepath, "w") as f:
            f.write(self.to_yaml())

        if schema is not None or self.validate_on_write:
            self.validate(schema=schema, exclude_case=exclude_case)

        abs_path = os.path.abspath(self.locker.filepath)
        _LOGGER.debug(f"Wrote to a file: {abs_path}")
        return os.path.abspath(abs_path)

    def write_copy(self, filepath: str | Path) -> str:
        """Write the contents to an external file.

        Args:
            filepath: A file path to write to.

        Returns:
            The filepath that was written to.
        """

        _LOGGER.debug(f"Writing to file '{filepath}'")
        with open(filepath, "w") as f:
            f.write(self.to_yaml())
        return str(filepath)

    def to_yaml(self, trailing_newline: bool = False, expand: bool = False) -> str:
        """Get text for YAML representation.

        Args:
            trailing_newline: Whether to add trailing newline.
            expand: Whether to expand paths in values.

        Returns:
            YAML text representation of this instance.
        """

        if expand:
            return yaml.dump(self.exp, default_flow_style=False)
        return yaml.dump(self.data, default_flow_style=False) + (
            "\n" if trailing_newline else ""
        )

    def to_dict(self, expand: bool = True) -> dict[str, Any]:
        """Convert the object to a dictionary.

        Args:
            expand: Whether to expand paths in values (currently unused,
                kept for backwards compatibility).

        Returns:
            The object's data as a dictionary.
        """
        # Seems like it's probably not necessary; can just use the object now.
        # but for backwards compatibility.
        return self.data

    def __setitem__(self, item: str, value: object) -> None:
        """Set a key-value pair in the configuration.

        Args:
            item: The key to set.
            value: The value to set for the key.
        """
        self.data[item] = value

    def __getitem__(self, item: str) -> object:
        """Fetch the value of given key.

        Args:
            item: Key for which to fetch value.

        Returns:
            Value mapped to given key, if available.

        Raises:
            KeyError: If the requested key is unmapped.
        """
        return self.data[item]

    @property
    def exp(self) -> dict[str, Any]:
        """Get data with environment and user variables expanded.

        Returns a copy of the object's data elements with env vars and user vars
        expanded. Use it like: object.exp["item"]

        Returns:
            Dictionary with expanded paths and variables.
        """
        return _safely_expand_path(self.data)

    def __iter__(self) -> Iterator[str]:
        """Return an iterator over the configuration keys."""
        return iter(self.data)

    def __len__(self) -> int:
        """Return the number of configuration entries."""
        return len(self.data)

    def __delitem__(self, key: str) -> None:
        """Delete a key-value pair from the configuration.

        Args:
            key: The key to delete.
        """
        value = self[key]
        del self.data[key]
        self.pop(value, None)

    def priority_get(
        self,
        arg_name: str,
        env_var: str | None = None,
        default: str | None = None,
        override: str | None = None,
        strict: bool = False,
    ) -> str | None:
        """Select a value with priority: override > config > env_var > default.

        Helper function to select a value from a config, or, if missing, then
        go to an env var.

        Args:
            arg_name: Argument to retrieve from config.
            env_var: Environment variable to retrieve from if missing from config.
            default: Default value if not found in config or environment.
            override: Override value that takes precedence over all other sources.
            strict: Should missing args raise an error? If False, shows warning.

        Returns:
            The value from the highest priority source, or None if not found
            and strict is False.

        Raises:
            Exception: If strict is True and the value cannot be determined.
        """
        if override:
            return override
        if isinstance(self.data, dict) and self.data.get(arg_name) is not None:
            result = self.data[arg_name]
            if not isinstance(result, str):
                raise TypeError(
                    f"Config value for '{arg_name}' must be a string, got {type(result).__name__}"
                )
            return result
        if env_var is not None:
            arg = os.getenv(env_var, None)
            if arg is not None:
                _LOGGER.debug(f"Value '{arg}' sourced from '{env_var}' env var")
                return expandpath(arg)
        if default is not None:
            return default
        if strict:
            message = (
                "Value for required argument '{arg_name}' could not be determined."
            )
            _LOGGER.warning(message)
            raise Exception(message)
        return None


# A big issue here is: if you route the __getitem__ through this,
# then it returns a copy of the data, rather than the data itself.
# That's the point, so we don't adjust it. But then you can't use multi-level
# item setting, like ycm["x"]["y"] = value, because ycm['x'] returns a different
# dict, and so you're updating that copy of it.
# The solution is that we have to route expansion through a separate property,
# so the setitem syntax can remain intact while preserving original values.
def _safely_expand_path(x: Any) -> Any:
    """Recursively expand paths in strings and mappings without modifying originals.

    Args:
        x: The value to expand. Can be a string, mapping, or other type.

    Returns:
        The expanded value. Strings are expanded, mappings are recursively
        expanded, and other types are returned unchanged.
    """
    if isinstance(x, str):
        return expandpath(x)
    elif isinstance(x, Mapping):
        return {k: _safely_expand_path(v) for k, v in x.items()}
    return x


def _unsafely_expand_path(x: Any) -> Any:
    """Recursively expand paths in strings and mappings by modifying in place.

    Args:
        x: The value to expand. Can be a string, mapping, or other type.

    Returns:
        The expanded value. Strings are expanded, mappings are modified in place
        and returned, and other types are returned unchanged.
    """
    if isinstance(x, str):
        return expandpath(x)
    elif isinstance(x, Mapping):
        for k in x.keys():
            x[k] = _safely_expand_path(x[k])  # type: ignore
        return x
        # return {k: _safely_expand_path(v) for k, v in x.items()}
    return x


def _check_filepath(filepath: Any) -> str:
    """Validate if the filepath is a str.

    Args:
        filepath: Object to validate.

    Returns:
        Validated filepath.

    Raises:
        TypeError: If the filepath is not a string.
    """
    # might be useful if we want to have multiple locked paths in the future
    # def _check_string(obj):
    #     """ check if object is a string or a list of strings """
    #     return bool(obj) and all(isinstance(elem, str) for elem in obj)
    if not isinstance(filepath, str):
        raise TypeError(
            f"No valid filepath provided. It must be a str, got: {filepath.__class__.__name__}"
        )
    return filepath


def load_yaml(filepath: str | Path) -> dict[str, Any]:
    """Load a local or remote YAML file into a Python dict.

    Args:
        filepath: Path to the file to read (can be a local path or URL).

    Returns:
        Loaded YAML data as a dictionary.

    Raises:
        ConnectionError: If the remote YAML file reading fails.
    """
    if is_url(filepath):
        _LOGGER.debug(f"Got URL: {filepath}")
        from urllib.request import urlopen

        try:
            response = urlopen(str(filepath))
        except Exception as e:
            raise ConnectionError(
                f"Could not load remote file: {filepath}. "
                f"Original exception: {getattr(e, 'message', repr(e))}"
            )
        data = response.read().decode("utf-8")
        return yaml.load(data, YacmanLoader)
    else:
        with open(os.path.abspath(filepath), "r") as f:
            data = yaml.load(f, YacmanLoader)
        return data


def select_config(
    config_filepath: str | None = None,
    config_env_vars: str | list[str] | None = None,
    default_config_filepath: str | None = None,
    check_exist: bool = True,
    on_missing: Callable[[str], Exception | str] = lambda fp: IOError(fp),
    strict_env: bool = False,
    config_name: str | None = None,
) -> str | None:
    """Select the config file to load using priority ordering.

    This uses a priority ordering to first choose a config filepath if it's given,
    but if not, then look in a priority list of environment variables and choose
    the first available filepath to return.

    Priority order:
        1. config_filepath (if provided and exists)
        2. config_env_vars (first existing file from environment variables)
        3. default_config_filepath (if provided)

    Args:
        config_filepath: Direct filepath specification.
        config_env_vars: Names of environment variables to try for config
            filepaths. Can be a string or list of strings.
        default_config_filepath: Default value if no other alternative
            resolution succeeds.
        check_exist: Whether to check for path existence as file.
        on_missing: What to do with a filepath if it doesn't exist.
            Should be a callable that takes a filepath and returns an object.
        strict_env: Whether to raise an exception if no file path provided
            and environment variables do not point to any files.
        config_name: Name to use in log messages for this config.

    Returns:
        The absolute path to the selected config file, or None if no file
        could be found and strict_env is False.

    Raises:
        OSError: When strict environment variables validation is not passed.
    """

    # First priority: given file
    if type(config_name) is str:
        config_name = f"{config_name} "
    else:
        config_name = ""

    if type(config_env_vars) is str:
        config_env_vars = [config_env_vars]

    if config_filepath:
        config_filepath = os.path.expandvars(config_filepath)
        if not check_exist or os.path.isfile(config_filepath):
            return os.path.abspath(config_filepath)
        _LOGGER.error(f"{config_name}config file path isn't a file: {config_filepath}")
        result = on_missing(config_filepath)
        if isinstance(result, Exception):
            raise result
        return os.path.abspath(result)

    _LOGGER.debug(f"No local {config_name}config file was provided.")
    selected_filepath = None

    # Second priority: environment variables (in order)
    if config_env_vars:
        _LOGGER.debug(
            f"Checking environment variables '{config_env_vars}' for {config_name}config"
        )

        for env_var in config_env_vars:
            result = os.environ.get(env_var)  # type: ignore
            if result == None:
                _LOGGER.debug(f"Env var '{env_var}' not set.")
                continue
            elif result == "":
                _LOGGER.debug(f"Env var '{env_var}' exists, but value is empty.")
                continue
            elif not os.path.isfile(result):  # type: ignore
                _LOGGER.debug(f"Env var '{env_var}' file not found: {result}")
                continue
            else:
                _LOGGER.debug(f"Found {config_name}config file in {env_var}: {result}")
                selected_filepath = result

    if selected_filepath is None:
        # Third priority: default filepath
        if default_config_filepath:
            _LOGGER.info(
                f"Using default {config_name}config. You may specify in env var: {str(config_env_vars)}"
            )
            return default_config_filepath
        else:
            if strict_env:
                raise OSError("Unable to select config file.")

            _LOGGER.info(f"Could not locate {config_name}config file.")
            return None
    return (
        os.path.abspath(selected_filepath) if selected_filepath else selected_filepath  # type: ignore
    )


def deep_update(old: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    """Recursively update nested dict, modifying source.

    Args:
        old: The dictionary to update (modified in place).
        new: The dictionary with new values to merge in.

    Returns:
        The updated old dictionary.
    """
    for key, value in new.items():
        if isinstance(value, Mapping) and value:
            old[key] = deep_update(old.get(key, {}), value)  # type: ignore
        else:
            old[key] = new[key]
    return old
