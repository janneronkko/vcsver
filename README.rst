==================
setuptools_autover
==================

About
=====

A package allowing generating PEP-440 compatible version numbers from version
control.

Currently only git is supported but it is possible to add support for other
version control systems.

The goal of the project is to provide reasonable defaults and an easy way to
customize how version numbers are generated from version control system.

The code is currently considered stable and ready for production use. The API
should not change in such way that the change would break current usage.

Usage
=====

setup.py
--------

1. Add *setuptools_autover* to *setup_requires* argument
2. Set *use_autover* argument
    The value can be mapping, (a dict, for example) containing configuration or
    any Python value that evaluates as True.

Use with default settings

.. code:: python

    import setuptools

    setup(
        name='example-package',
        use_autover=True,
        setup_requires=['setuptools_autover'],
    )

Use with custom settings

.. code:: python

    import setuptools

    setup(
        name='example-package',
        use_autover={
          'root_version': '0.0',
          'parse_tag': lambda tag: tag.lstrip('v'),
          'create_version': lambda ver: '{}.post{}'.format(ver.latest_version, ver.distance),
        },
        setup_requires=['setuptools_autover'],
    )

Note that if the *setup* function is called for source tree not having version info available,
*setuptools_autover.RevisionInfoNotFoundError* is raised.

From Python Code
----------------

.. code:: python

    from setuptools_autover import get_version

    # Using default settings
    version = get_version()

    # Using custom settings
    version = get_version(root_version='0.0')

Version Number Generation
=========================

If setup.py is not run on code in a repository, version information is read from *PKG-INFO* to
allow *sdist* to work.

When running setup.py on code in a repository, *setuptools_autover.RevisionInfo* object is filled
based on current revision.

If latest tag is available, latest release version is read from it by using *parse_tag*
function. Otherwise *root_version* is used as latest version and distance is the number
of commits since the start of the commit history.

The version string is generated based on the above info using the *create_version* function.

Configuration
=============

The *use_autover* argument can be used for configuring version generation behaviour
by proving the configuration as mapping.

**root_version**
  If repository does not contain any tags, this string is used.

  Default value: :code:`'0'`

**read_revision_info**
  Callable used for reading revision information from VCS (or other source).

  The function should not take any arguments and should return instance of *setuptools_autover.RevisionInfo*
  or None in case revision info is not available.

  By default :code:`setuptools_autover.GitRevisionInfoReader` instance with default arguments is used.

**parse_tag**
  Function parsing version string from a tag.

  The function takes one string argument (the tag) and returns version extracted from
  the tag as string

  Default value: :code:`lambda tag: tag`

**create_version**
  Function creating version string from *setuptools_autover.VersionInfo*.

  The function takes one argument of type *setuptools_autover.VersionInfo*. 

  Default value: :code:`setuptools_autover.pep440.create_post_with_dev`

Configuration matching the default settings:

.. code:: python

    {
        'root_version': '0',
        'read_revision_info': setuptools_autover.GitRevisionInfoReader(),
        'parse_tag': lambda tag: tag,
        'create_version': setuptools_autover.pep440.create_post_with_dev,
    }

API
===

Functions
---------


**setuptools_autover.config_to_get_version_kwargs(config)**
  Return kwargs dictionary for *setuptools_autover.get_version* based on the given configuration.

**setuptools_autover.get_version(root_version='0', parse_tag=lambda tag: tag, create_version=pep440.create_post_with_dev)**
  The arguments are the same as the configurations passed for *use_autover* argument from *setup.py*

  Return generated version

**setuptools_autover.pep440.create_post_with_dev**
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

setuptools_autover.GitRevisionInfoReader
****************************************

Read revision info from Git repository.

Constructor arguments:

**path**
  Path to repository root. If *None*, current working directory is used.

  Default value: :code:`None`

Members:

**__call__(self)**
  Return setuptools_autover.RevisionInfo generated from Git history of *HEAD*.

Exceptions
----------

**setuptools_autover.AutoverError**
  Base class for exceptions thrown by *setuptools_autover*

**setuptools_autover.InvalidConfigError**
  The configuration dict is not valid.

**setuptools_autover.RevisionInfoNotFoundError**
  Version could not be generated because revision info was not found

Types
-----

**setuptools_autover.RevisionInfo**
  Named tuple containing revision info:

  - **latest_tag**: The most recent tag (None if there is no tags before the current revision)
  - **distance**: Number of commits since the most recent tag (0 if current revision is tagged)
  - **commit**: Commit identifier for current revision
  - **dirty**: Is the source tree dirty (not exactly the same as the code in the current revision).
    If there is no commits, the *lastest_tag* and *commit* should be :code:`None` and dirty should be
    set to :code:`True`

**setuptools_autover.VersionInfo**
  Named tuple containing version info:

  - **latest_version**: The most recent version (None if there is no released version before the current revision)
  - **distance**: Number of commits since the most recent tag (0 if current revision is tagged)
  - **commit**: Commit identifier for current revision
  - **dirty**: Is the source tree dirty (not exactly the same as the code in the current revision)

*RevisionInfo* is information returned by VCS readers and is turned into *VersionInfo* using the *parse_tag* function.
