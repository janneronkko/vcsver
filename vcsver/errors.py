class VcsverError(Exception):
    '''
    Base exception for all (public) exceptinos thrown by
    vcsver.
    '''


class RevisionInfoNotFoundError(VcsverError):
    '''
    No version source data available; vcsver can not
    create version number.
    '''
