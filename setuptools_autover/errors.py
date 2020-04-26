class AutoverError(Exception):
    '''
    Base exception for all (public) exceptinos thrown by
    setuptools_autover.
    '''


class RevisionInfoNotFoundError(AutoverError):
    '''
    No version source data available; autover can not
    create version number.
    '''
