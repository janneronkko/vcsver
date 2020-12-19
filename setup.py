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


with open('README.rst', 'rt') as readme_file:
    long_desc = readme_file.read()  # pylint: disable=invalid-name

setuptools.setup(
    name='vcsver',
    version=VERSION,
    description='Automatic package version numbering from version control',
    long_description=long_desc,
    long_description_content_type='text/x-rst',
    url='https://github.com/janneronkko/vcsver',
    author='Janne Rönkkö',
    author_email='janne.ronkko@iki.fi',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: System :: Archiving :: Packaging',
    ],
    keywords='setuptools development git version',
    packages=['vcsver'],
    python_requires='>=3.5',
    entry_points={
        'distutils.setup_keywords': [
            'vcsver = vcsver.setuptools:vcsver',
        ],
    },
)
