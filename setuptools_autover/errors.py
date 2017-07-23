class AutoverError(Exception):
    '''
    Base exception for all (public) exceptinos thrown by
    setuptools_autover.
    '''


class InvalidConfigError(AutoverError):
    '''
    The configuration is invalid
    '''

    def __init__(self, description, invalid_items):
        super().__init__(description)

        self.invalid_items = invalid_items


class RevisionInfoNotFoundError(AutoverError):
    '''
    No version source data available; autover can not
    create version number.
    '''
