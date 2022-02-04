class VcsverError(Exception):
    '''
    Base exception for all (public) exceptinos thrown by
    vcsver.
    '''


class InvalidConfigurationError(VcsverError):
    '''
    vcsver configuration is invalid.
    '''


class RevisionInfoNotFoundError(VcsverError):
    '''
    No version source data available; vcsver can not
    create version number.
    '''
