import collections


RevisionInfo = collections.namedtuple(
    'RevisionInfo',
    ('latest_tag', 'distance', 'commit', 'dirty'),
)


VersionInfo = collections.namedtuple(
    'VersionInfo',
    ('latest_release', 'distance', 'commit', 'dirty'),
)
