======
vcsver
======

About
=====

A package allowing generating PEP-440 compatible version numbers based on
version control system. The goal is that each commit has unique version number
that can be traced back to the commit easily.

Currently only git is supported but it is possible to add support for other
version control systems.

Usage
=====

setup.py
--------

1. Add *vcsver* to *setup_requires* argument
2. Set *vcsver* argument
    The value can be mapping, (a dict, for example) containing configuration or
    any Python value that evaluates as True.

Use with default settings

.. code:: python

    import setuptools

    setup(
        name='example-package',
        vcsver=True,
        setup_requires=['vcsver'],
    )

Use with custom settings

.. code:: python

    import setuptools

    setup(
        name='example-package',
        vcsver={
          'root_version': '0.0',
          'parse_tag': lambda tag: tag.lstrip('v'),
          'create_version': lambda ver: '{}.post{}'.format(ver.latest_version, ver.distance),
        },
        setup_requires=['vcsver'],
    )

Note that if the *setup* function is called for source tree not having version info available,
*vcsver.RevisionInfoNotFoundError* is raised.

From Python Code
----------------

.. code:: python

    from vcsver import get_version

    # Using default settings
    version = get_version()

    # Using custom settings
    version = get_version(root_version='0.0')

Version Number Generation
=========================

If setup.py is not run on code in a repository, version information is read from *PKG-INFO* to
allow *sdist* to work.

When running setup.py on code in a repository, *vcsver.RevisionInfo* object is filled
based on current revision.

If latest tag is available, latest release version is read from it by using *parse_tag*
function. Otherwise *root_version* is used as latest version and distance is the number
of commits since the start of the commit history.

The version string is generated based on the above info using the *create_version* function.

Configuration
=============

The *vcsver* argument can be used for configuring version generation behaviour
by proving the configuration as mapping.

The items in the mapping can either be actual Python objects or identifiers (strings)
that are mapped to actual values.

**root_version**
  If repository does not contain any tags, this string is used.

  Default value: :code:`'0'`

**read_revision_info**
  Callable used for reading revision information from VCS (or other source).

  The function should not take any arguments and should return instance of *vcsver.RevisionInfo*
  or None in case revision info is not available.

  Default value: :code:`vcsver.GitRevisionInfoReader()`

  Available identifiers:

  - :code:`git` Use *vcsvver.GitRevisionInfoReader* instance with default arguments

**parse_tag**
  Function parsing version string from a tag.

  The function takes one string argument (the tag) and returns version extracted from
  the tag as string

  Default value: :code:`lambda tag: tag`

  Available identifiers:

  - :code:`plain` Use the tag as it is in the version control system

**create_version**
  Function creating version string from *vcsver.VersionInfo*.

  The function takes one argument of type *vcsver.VersionInfo*. 

  Default value: :code:`vcsver.pep440.post`

  Available identifiers:

  - :code:`pep440.post` PEP 440 string using postN
  - :code:`pep440.post_with_dev` PEP 440 string using post0+devN

Configuration matching the default settings:

.. code:: python

    {
        'root_version': '0',
        'read_revision_info': vcsver.GitRevisionInfoReader(),
        'parse_tag': lambda tag: tag,
        'create_version': vcsver.pep440.post,
    }

The same configuration can also be defined without importing *vcsver*:

.. code:: python

    {
        'root_version': '0',
        'read_revision_info': 'git',
        'parse_tag': 'plain',
        'create_version': 'pep440.post',
    }

API
===

Functions
---------

**vcsver.get_version(root_version='0', parse_tag=lambda tag: tag, create_version=pep440.post)**
  The arguments are the same as the configurations passed for *vcsver* argument from *setup.py*

  Return generated version

**vcsver.pep440.post**
  Create version that uses *post* patr for version between releases.

  The version is created using the following rules:

  - :code:`distance == 0 and not dirty` ⇒ :code:`{latest_version}`
      Released version
  - :code:`distance == 0 and dirty` ⇒ :code:`{latest_version+dirty}`
      Released version with modified source tree
  - :code:`distance > 0 and not dirty` ⇒ :code:`{latest_version}.post{distance}+{commit}`
      Released version
  - :code:`distance > 0 and dirty` ⇒ :code:`{latest_version+dirty}.post{distance}+{commit}-dirty`
      Released version with modified source tree

**vcsver.pep440.post_with_dev**
  Create version that uses *post* and *dev* parts for version between releases.

  The version is created using the following rules:

  - :code:`distance == 0 and not dirty` ⇒ :code:`{latest_version}`
      Released version
  - :code:`distance == 0 and dirty` ⇒ :code:`{latest_version+dirty}`
      Released version with modified source tree
  - :code:`distance > 0 and not dirty` ⇒ :code:`{latest_version}.post0.dev{distance}+{commit}`
      Released version
  - :code:`distance > 0 and dirty` ⇒ :code:`{latest_version+dirty}.post0.dev{distance}+{commit}-dirty`
      Released version with modified source tree

Classes
-------

vcsver.GitRevisionInfoReader
****************************************

Read revision info from Git repository.

Constructor arguments:

**path**
  Path to repository root. If *None*, current working directory is used.

  Default value: :code:`None`

Members:

**__call__(self)**
  Return vcsver.RevisionInfo generated from Git history of *HEAD*.

Exceptions
----------

**vcsver.VcsverError**
  Base class for exceptions thrown by *vcsver*

**vcsver.RevisionInfoNotFoundError**
  Version could not be generated because revision info was not found

Types
-----

**vcsver.RevisionInfo**
  Named tuple containing revision info:

  - **latest_tag**: The most recent tag (None if there is no tags before the current revision)
  - **distance**: Number of commits since the most recent tag (0 if current revision is tagged)
  - **commit**: Commit identifier for current revision
  - **dirty**: Is the source tree dirty (not exactly the same as the code in the current revision).
    If there is no commits, the *lastest_tag* and *commit* should be :code:`None` and dirty should be
    set to :code:`True`

**vcsver.VersionInfo**
  Named tuple containing version info:

  - **latest_version**: The most recent version (None if there is no released version before the current revision)
  - **distance**: Number of commits since the most recent tag (0 if current revision is tagged)
  - **commit**: Commit identifier for current revision
  - **dirty**: Is the source tree dirty (not exactly the same as the code in the current revision)

*RevisionInfo* is information returned by VCS readers and is turned into *VersionInfo* using the *parse_tag* function.
