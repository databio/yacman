""" Package exception types """

__all__ = ["FileFormatError", "UndefinedAliasError"]


class FileFormatError(Exception):
    """ Exception for invalid file format. """
    pass


class UndefinedAliasError(Exception):
    """ Alias is is not defined. """
    pass