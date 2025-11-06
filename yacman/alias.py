import logging
from collections.abc import Mapping
from inspect import getfullargspec
from typing import Any, Callable
from warnings import warn

from .const import *
from .exceptions import *
from .yacman import YAMLConfigManager

_LOGGER = logging.getLogger(__name__)


class AliasedYAMLConfigManager(YAMLConfigManager):
    """A class that extends YAMLConfigManager to provide alias feature.

    The items in the object can be accessed using the original key or an alias,
    if defined in the aliases Mapping.
    """

    def __init__(
        self,
        entries: dict[str, Any] | list[Any] | None = None,
        wait_max: int = DEFAULT_WAIT_TIME,
        aliases: dict[str, list[str]] | Callable | None = None,
        exact: bool = False,
        aliases_strict: bool | None = None,
    ) -> None:
        """Object constructor.

        Args:
            entries: YAML collection of key-value pairs.
            wait_max: How long to wait for creating an object when the file
                that data will be read from is locked.
            aliases: Aliases mapping to use or a callable that produces such
                a mapping out of the object to set the aliases for.
            exact: Whether aliases should not be used, even if defined.
            aliases_strict: How to handle aliases mapping issues. None for
                warning, True for AliasError, False to disregard.
        """

        super(AliasedYAMLConfigManager, self).__init__(
            entries=entries,
            wait_max=wait_max,
        )
        setattr(self, ALIASES_KEY_RAW, {})
        if not exact:
            if isinstance(aliases, Mapping) and is_aliases_mapping_valid(
                aliases, aliases_strict
            ):
                setattr(self, ALIASES_KEY_RAW, aliases)
            elif callable(aliases):
                if len(getfullargspec(aliases).args) != 1:
                    _emit_msg(
                        aliases_strict,
                        "Provided function '{}' must be a one-arg function".format(
                            aliases.__name__
                        ),
                    )
                try:
                    res = aliases(self)
                except Exception as e:
                    _emit_msg(
                        aliases_strict,
                        "Provided function '{}' errored: {}".format(
                            aliases.__name__, getattr(e, "message", repr(e))
                        ),
                    )
                else:
                    if is_aliases_mapping_valid(res):
                        setattr(self, ALIASES_KEY_RAW, res)
                    else:
                        _emit_msg(
                            aliases_strict,
                            "callable '{}' did not return a Mapping".format(
                                aliases.__name__
                            ),
                        )
            else:
                _LOGGER.info("No aliases provided")

        # convert the original, condensed mapping to a data structure with
        # optimal time complexity
        setattr(self, ALIASES_KEY, {})
        for k, v in getattr(self, ALIASES_KEY_RAW).items():
            for alias in v:
                getattr(self, ALIASES_KEY)[alias] = k

    def __getitem__(self, item: str) -> object:
        """Get item by key or alias.

        This item accession method will try to access the value by a literal
        key. If the key is not defined in the object it will try to access the
        key by its alias, if defined. If both fail, a KeyError is raised.

        Args:
            item: The key or alias to look up.

        Returns:
            The value associated with the key or alias.

        Raises:
            KeyError: If neither the key nor its alias is defined.
        """
        try:
            return super(AliasedYAMLConfigManager, self).__getitem__(item)
        except KeyError:
            try:
                key = self.get_key(item)
            except UndefinedAliasError:
                raise KeyError(item)
            else:
                return super(AliasedYAMLConfigManager, self).__getitem__(key)

    def __contains__(self, key: object) -> bool:
        """Check if key or alias exists in the object.

        This containment verification method will first try the literal key.
        If the key is not defined in the object it will try to use its alias.
        If both fail, a negative decision is returned; otherwise -- positive.

        Args:
            key: The key or alias to check for.

        Returns:
            True if the key or alias exists, False otherwise.
        """
        if not isinstance(key, str):
            return False
        try:
            self.__getitem__(key)
        except (UndefinedAliasError, KeyError):
            try:
                alias_key = self.get_key(key)
            except (UndefinedAliasError, KeyError):
                return False
            else:
                try:
                    self.__getitem__(alias_key)
                except (UndefinedAliasError, KeyError):
                    return False
                else:
                    return True
        else:
            return True

    def __delitem__(self, key: str) -> None:
        """Delete item by key or alias.

        This item deletion method will try to remove the item by the literal
        key or by its alias, if defined.

        Args:
            key: The key or alias to delete.
        """
        try:
            # check whether an alias was used
            alias_key = self.get_key(alias=key)
        except (UndefinedAliasError, KeyError):
            # alias was not used, try to delete the literal key
            super(AliasedYAMLConfigManager, self).__delitem__(key)
        else:
            # alias was used, try to delete the alias
            super(AliasedYAMLConfigManager, self).__delitem__(alias_key)

    def get_aliases(self, key: str) -> list[str]:
        """Get the alias for key in the object.

        Args:
            key: Key to find an alias for.

        Returns:
            List of aliases matched by the key.

        Raises:
            UndefinedAliasError: If no alias has been defined for the
                requested key.
        """
        aliases = []
        for a, k in getattr(self, ALIASES_KEY).items():
            if k == key:
                aliases.append(a)
        if aliases:
            return aliases
        raise UndefinedAliasError("No alias defined for: {}".format(key))

    def get_key(self, alias: str) -> str:
        """Get the key for alias in the object.

        Args:
            alias: Alias to find a key for.

        Returns:
            Key matched by the alias.

        Raises:
            UndefinedAliasError: If no key has been defined for the
                requested alias.
        """
        # try:
        #     # first try to use the parent method (doesn't try to use aliases) to
        #     # check if the __internal key is defined.
        #     # Otherwise we would end up in an infinite recursion loop.
        #     super(AliasedYAMLConfigManager, self).__getitem__(IK)
        # except KeyError:
        #     # raise UndefinedAliasError, which is caught in the updated __getitem__ method
        #     raise UndefinedAliasError()
        if alias in getattr(self, ALIASES_KEY).keys():
            return getattr(self, ALIASES_KEY)[alias]
        raise UndefinedAliasError("No key defined for: {}".format(alias))

    def set_aliases(
        self, key: str, aliases: str | list[str], overwrite: bool = False, reset_key: bool = False
    ) -> tuple[list[str], list[str]]:
        """Assign an alias to a key in the object.

        Args:
            key: Name of the key to assign to an alias for.
            aliases: Alias or list of aliases to use.
            overwrite: Whether to force overwrite the key for an already
                defined alias.
            reset_key: Whether to force remove existing aliases for a key.

        Returns:
            Tuple of (list of set aliases, list of removed aliases).
        """
        removed_aliases = []
        if reset_key:
            try:
                current_aliases = self.get_aliases(key)
            except UndefinedAliasError:
                pass
            else:
                for a in current_aliases:
                    del getattr(self, ALIASES_KEY)[a]
                    removed_aliases.append(a)

        set_aliases: list[str] = []
        aliases_list = _make_list_of_aliases(aliases)
        if aliases_list is None:
            return set_aliases, removed_aliases
        for alias in aliases_list:
            if alias in getattr(self, ALIASES_KEY):
                if overwrite:
                    getattr(self, ALIASES_KEY)[alias] = key
                    set_aliases.append(alias)
            else:
                getattr(self, ALIASES_KEY)[alias] = key
                set_aliases.append(alias)
        _LOGGER.debug("Added aliases ({}: {})".format(key, set_aliases))
        return set_aliases, removed_aliases

    def remove_aliases(self, key: str, aliases: str | list[str] | None = None) -> list[str]:
        """Remove an alias from the object.

        Args:
            key: Name of the key to remove aliases for.
            aliases: List of aliases to remove. If None, removes all aliases
                for the key.

        Returns:
            List of removed aliases.
        """
        removed: list[str] = []
        aliases_list = _make_list_of_aliases(aliases)
        try:
            current_aliases = self.get_aliases(key)
        except UndefinedAliasError:
            return removed
        else:
            existing_aliases = (
                list(set(aliases_list) & set(current_aliases))
                if aliases_list
                else current_aliases
            )
            for alias in existing_aliases:
                del getattr(self, ALIASES_KEY)[alias]
                removed.append(alias)
            return removed


def is_aliases_mapping_valid(aliases: Any, strictness: bool | None = None) -> bool:
    """Determine if the aliases mapping is formatted properly.

    The expected format is {"k": ["v"]}, where keys map to lists of aliases.

    Args:
        aliases: Mapping to verify.
        strictness: How to handle format issues. None for warning, True for
            AliasError, False to disregard.

    Returns:
        Whether the mapping adheres to the correct format.
    """
    if isinstance(aliases, Mapping):
        if all([isinstance(v, list) for k, v in aliases.items()]):
            return True
    _emit_msg(strictness, "Provided aliases mapping is invalid; Mapping[list] required")
    return False


def _make_list_of_aliases(aliases: str | list[str] | None) -> list[str] | None:
    """Check and/or produce a proper aliases input.

    Args:
        aliases: Alias or collection of aliases to check.

    Returns:
        List of aliases.

    Raises:
        AliasError: If the input format does not meet the requirements.
    """

    def _raise_alias_class(x: Any) -> AliasError:
        return AliasError(
            "A string or a list of strings is required, "
            "got: {}".format(x.__class__.__name__)
        )

    if aliases is None:
        return aliases
    if isinstance(aliases, str):
        aliases = [aliases]
    elif isinstance(aliases, list):
        if not all([isinstance(x, str) for x in aliases]):
            raise _raise_alias_class(aliases)
    else:
        raise _raise_alias_class(aliases)
    return aliases


def _emit_msg(strictness: bool | None, msg: str) -> None:
    """Emit a message based on the selected strictness level.

    Args:
        strictness: None for warning, True for AliasError, False for debug log.
        msg: A message to emit.
    """
    if strictness:
        raise AliasError(msg)
    elif strictness is None:
        warn(msg)
    else:
        _LOGGER.debug(msg)
