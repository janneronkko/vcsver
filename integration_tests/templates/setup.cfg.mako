[metadata]
name = ${name}
% if version is not None:
version = ${version}
% endif
description = vcsver test project
author = Janne Rönkkö
author_email = janne.ronkko@iki.fi
license = MIT
classifiers =
    Development Status :: 3 - Alpha
    Intended Audience :: Developers
    License :: OSI Approved :: MIT License
    Operating System :: OS Independent
    Programming Language :: Python :: 3.7
    Programming Language :: Python :: 3.8
    Programming Language :: Python :: 3.9
    Programming Language :: Python :: 3.10
    Topic :: System :: Archiving :: Packaging

[options]
py_modules = vcsvertest
python_requires = >=3.7
