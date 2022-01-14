import os

import setuptools

try:
    import vcsver
    VERSION = vcsver.get_version()

except ImportError:
    if 'TOX_WORK_DIR' not in os.environ:
        # When running inside TOX, vcsver is not installed in
        # the virtual environment created by TOX because we can not depend
        # on ourself when installing
        raise

    VERSION = '0.0+tox'


setuptools.setup(
    version=VERSION,
)
