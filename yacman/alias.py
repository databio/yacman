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
        setattr(self, ALIASES_KEY, None)
        if not exact:
            if isinstance(aliases, Mapping):
                setattr(self, ALIASES_KEY, aliases())
            elif callable(aliases):
                try:
                    res = aliases()
                except Exception as e:
                    _LOGGER.warning("callable '{}' errored: {}".
                                    format(str(e), ALIASES_KEY))
                else:
                    if isinstance(res, Mapping):
                        setattr(self, ALIASES_KEY, res)
                    else:
                        _LOGGER.warning("callable '{}' did not return a Mapping".
                                        format(ALIASES_KEY))

        super(AliasedYacAttMap, self).__init__(
            entries=entries, filepath=filepath, yamldata=yamldata,
            writable=writable, wait_max=wait_max, skip_read_lock=skip_read_lock)

    def __getitem__(self, item, expand=True):
        try:
            return super(AliasedYacAttMap, self).__getitem__(item=item,
                                                             expand=expand)
        except KeyError:
            try:
                alias = self.get_key_alias(item)
            except (UndefinedAliasError, FileFormatError):
                raise KeyError(item)
            else:
                return super(AliasedYacAttMap, self).__getitem__(item=alias,
                                                                 expand=expand)

    @property
    def alias_dict(self):
        return getattr(self, ALIASES_KEY)

    def get_key_alias(self, alias):
        """
        Get the genome digest for human readable alias

        :param str alias: human-readable alias to get the genome digest for
        :return str: genome digest
        :raise GenomeConfigFormatError: if "genome_digests" section does
            not exist in the config
        :raise UndefinedAliasError: if a no digest has been defined for the
            requested alias
        """
        if self.alias_dict is None:
            raise FileFormatError("alias mapping is not defined")
        if alias not in self.alias_dict.keys():
            raise UndefinedAliasError("No alias defined for '{}'".format(alias))
        return self.alias_dict[alias]