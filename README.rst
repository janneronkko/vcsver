======
vcsver
======

Overview
========

Automate your project's version numbering; just create annotated tag in Git and
always have correct version number with your built packages. You don't need to
spend time updating version numbers in source code anymore, just tag and you are
good to go. And you are always able to go back to the commit from which a package
has been built.

Currently only Git and PEP-440 compatible version numbers with setuptools are
supported but the design allows adding other version control systems and other
versioning schemes.

Usage
=====

To enable automatic version in PEP 517 compatible way with setuptools, add the following
to *pyproject.toml*:

.. code:: toml

  [build-system]
  requires = [
    "setuptools",
    "vcsver",
  ]
  build-backend = "setuptools.build_meta"

  [tool.vcsver]
  source = "git"

Setuptools without pyproject.toml
---------------------------------

**Note that this method is deprecated and will be removed in the future releases.**

1. Add *vcsver* to *setup_requires*
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

Configuration
*************

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


Version Number Generation
=========================

When building package from code in a repository, *vcsver.RevisionInfo* object is filled
based on current revision.

If latest tag is available, latest release version is read from it by using *parse_tag*
function. Otherwise *root_version* is used as latest version and distance is the number
of commits since the start of the commit history.

The version string is generated based on the above info using the *create_version* function.

If package is being built from extracted *sdist*, version information is read from *PKG-INFO*.

API
===

Functions
---------

.. code:: python

  def get_version(
      root_version: str = '0',
      read_revision_info: types.RevisionInfoReader = git.GitRevisionInfoReader(),
      parse_tag: types.TagParser = lambda tag: tag,
      create_version: types.VersionStringFactory = pep440.post,
  ) -> str:

Get version using *read_revision_info* or from Python's PKG-INFO file (to support building
Python sdists).

*Arguments*

- **root_version**: Version string used as root version if no releases are found from VCS
- **read_revision_info**: Callable that return *RevisionInfo* object based on VCS
- **parse_tag**: Callable returning version string from tag found from VCS
- **create_version**: Callable returning version string based on *VersionInfo*

If *read_revision_info* returns :code:`None`, the :code:`distance` part of *RevisionInfo* is
assumed to contain the amount of commit since start of history. In this case the value of
:code:`root_version` is used as value for :code:`VersionInfo.latest_release` , i.e. *parse_tag*
is not used for mapping the latest tag into version string.

.. code:: python

  def post(
      version_info: types.VersionInfo,
  ) -> str:

Create version that uses *post* part for version between releases.

The version is created using the following rules:

- :code:`distance == 0 and not dirty` ⇒ :code:`{latest_version}`
    Released version
- :code:`distance == 0 and dirty` ⇒ :code:`{latest_version+dirty}`
    Released version with modified source tree
- :code:`distance > 0 and not dirty` ⇒ :code:`{latest_version}.post{distance}+{commit}`
    Released version
- :code:`distance > 0 and dirty` ⇒ :code:`{latest_version+dirty}.post{distance}+{commit}-dirty`
    Released version with modified source tree

.. code:: python

  def post_with_dev(
      version_info: types.VersionInfo,
  ) -> str:

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
****************************

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

**vcsver.InvalidConfigurationError**
  The configuration is invalid

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

**RevisionInfoReader**

.. code:: python

  typing.Callable[
      [],
      typing.Optional[RevisionInfo],
  ]

**RevisionInfoReaderFactory**

.. code:: python

  typing.Callable[
      [],
      RevisionInfoReader,
  ]

**TagParser**

.. code:: python

  typing.Callable[
      [str],
      str,
  ]

**VersionStringFactory**

.. code:: python

  typing.Callable[
      [VersionInfo],
      str,
  ]

Contributing
============

You can create PRs in GitHub.

Currently there is no CI but you can run tests and checks using `tox`; you should at least run static analyzers
(mypy, pycodestyle and pylint) and tests (unit tests and integration tests) for the latest Python version. For example,
to run static analyzers and tests with Python 3.10, run

.. code:: shell

  tox -emypy -epycodestyle -epylint -epy310-unittest -epy310-integrationtest

Quick Checklist For Your Change
-------------------------------

- Tests and checks pass
- Tests are added/modified for changes
- Commit messages have subject line and description (if needed) that use present tense
- Commits are logical changes (rewrite history, i.e. `git rebase -i`, when fixing review findings)

If you are not familiar with history rewriting, push the new commits and ask someone to squash the commits into
logical pieces.
