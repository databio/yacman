"""Package exception types.

This module defines custom exception classes used throughout the yacman package
for error handling related to file formats and alias operations.
"""

__all__ = ["FileFormatError", "AliasError", "UndefinedAliasError"]


class FileFormatError(Exception):
    """Exception for invalid file format.

    Raised when a configuration file cannot be parsed or is in an
    unsupported format.
    """

    pass


class AliasError(Exception):
    """Alias related error.

    Base exception class for errors related to alias operations
    in configuration management.
    """

    pass


class UndefinedAliasError(AliasError):
    """Alias is not defined.

    Raised when attempting to access or use an alias that has not been
    defined in the configuration.
    """

    pass
