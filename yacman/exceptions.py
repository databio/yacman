""" Package exception types """

__all__ = ["FileFormatError", "UndefinedAliasError"]


class FileFormatError(Exception):
    """ Exception for invalid genome config file format. """
    def __init__(self, msg):
        spacing = " " if msg[-1] in ["?", ".", "\n"] else "; "
        suggest = "For config format documentation please see "
        super(FileFormatError, self).__init__(msg + spacing + suggest)


class UndefinedAliasError(Exception):
    """ Alias is is not defined. """
    pass