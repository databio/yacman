from .yacman import YacAttMap
from .const import *
from .exceptions import *
from collections.abc import Mapping
import logging

_LOGGER = logging.getLogger(__name__)


class AliasedYacAttMap(YacAttMap):
    """
    A class that extends YacAttMap to provide alias feature.

    The items in the object can be accessed using the original key or an alias,
    if defined in the aliases Mapping.
    """
    def __init__(self, entries=None, filepath=None, yamldata=None,
                 writable=False, wait_max=DEFAULT_WAIT_TIME,
                 skip_read_lock=False, aliases=None, exact=False):
        """
        Object constructor

        :param Iterable[(str, object)] | Mapping[str, object] entries: YAML
            collection of key-value pairs.
        :param str filepath: YAML filepath to the config file.
        :param str yamldata: YAML-formatted string
        :param bool writable: whether to create the object with write
            capabilities
        :param int wait_max: how long to wait for creating an object when the
            file that data will be read from is locked
        :param bool skip_read_lock: whether the file should not be locked for
            reading when object is created in read only mode
        :param Mapping | callable() -> Mapping aliases: aliases mapping to use
            or a callable that produces such a mapping.
        :param bool exact: whether aliases should not be used, even if defined
        """
        setattr(self, ALIASES_KEY, {})
        if not exact:
            if isinstance(aliases, Mapping):
                setattr(self, ALIASES_KEY, aliases)
            elif callable(aliases):
                try:
                    res = aliases()
                except Exception as e:
                    _LOGGER.warning(
                        "Provided callable aliases '{}' errored: {}".format(
                            aliases.__name__, getattr(e, 'message', repr(e))))
                else:
                    if isinstance(res, Mapping):
                        setattr(self, ALIASES_KEY, res)
                    else:
                        _LOGGER.warning("callable '{}' did not return a Mapping".
                                        format(ALIASES_KEY))

        super(AliasedYacAttMap, self).__init__(
            entries=entries, filepath=filepath, yamldata=yamldata,
            writable=writable, wait_max=wait_max, skip_read_lock=skip_read_lock
        )

    def __getitem__(self, item, expand=True):
        """
        This item accession method will try to access the value by a literal
        key. If the key is not defined in the object it will try to access the
        key by it's alias, if defined. If both fail, a KeyError is raised.
        """
        try:
            return super(AliasedYacAttMap, self).__getitem__(item=item,
                                                             expand=expand)
        except KeyError:
            try:
                key = self.get_key(item)
            except (UndefinedAliasError):
                raise KeyError(item)
            else:
                return super(AliasedYacAttMap, self).__getitem__(item=key,
                                                                 expand=expand)

    def __contains__(self, key):
        """
        This containment verification method will first try the  literal key.
        If the key is not defined in the object it will try to use its alias.
        If both fail, a negative decision is returned; otherwise -- positive.
        """
        try:
            self.__getitem__(key, expand=False)
        except (UndefinedAliasError, KeyError):
            try:
                alias_key = self.get_key(key)
            except (UndefinedAliasError, KeyError):
                return False
            else:
                try:
                    self.__getitem__(alias_key, expand=False)
                except (UndefinedAliasError, KeyError):
                    return False
                else:
                    return True
        else:
            return True

    def __delitem__(self, key):
        """
        This item deletion method will try to remove the item by the literal
        key or by its alias, if defined.
        """
        try:
            # check whether an alias was used
            alias_key = self.get_key(alias=key)
        except (UndefinedAliasError, KeyError):
            # alias was not used, try to delete the literal key
            super(AliasedYacAttMap, self).__delitem__(key=key)
        else:
            # alias was used, try to delete the alias
            super(AliasedYacAttMap, self).__delitem__(key=alias_key)

    @property
    def alias_dict(self):
        """
        Get the alias mapping bound to the object
        """
        return self[ALIASES_KEY]

    def get_alias(self, key):
        """
        Get the alias for key in the object

        :param str key: key to find an alias for
        :return str: alias match by the key
        :raise GenomeConfigFormatError: if aliases mapping has not been defined
            for this object
        :raise UndefinedAliasError: if no alias has been defined for the
            requested key
        """
        if key in self.alias_dict.keys():
            return self.alias_dict[key]
        raise UndefinedAliasError("No alias defined for: {}".format(key))

    def get_key(self, alias):
        """
        Get the key for alias in the object

        :param str alias: alias to find a key for
        :return str: key match by the alias
        :raise GenomeConfigFormatError: if aliases mapping has not been defined
            for this object
        :raise UndefinedAliasError: if a no key has been defined for the
            requested alias
        """
        for k, v in self.alias_dict.items():
            if v == alias:
                return k
        raise UndefinedAliasError("No key defined for: {}".format(alias))

    def set_alias(self, key, alias, force=False):
        """
        Assign an alias to a key in the object.

        :param str key: name of the key to assign to an alias for
        :param str alias: alias to use
        :param bool force: whether to force overwrite if the alias exists
        :return bool: whether the alias has been set
        """
        if key in self.alias_dict.keys():
            _LOGGER.debug("'{}' already in aliases ({})".
                            format(key, self.alias_dict[key]))
            if not force:
                return False
        self[ALIASES_KEY][key] = alias
        _LOGGER.debug("Added alias ({}: {})".format(key, alias))
        return True

    def remove_alias(self, key):
        """
        Remove an alias from the object.

        :param str key: name of the key to remove
        :return bool: whether the alias has been removed
        """
        if key in self.alias_dict.keys():
            del self[ALIASES_KEY][key]
            return True
        return False
