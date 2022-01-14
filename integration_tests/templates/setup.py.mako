import setuptools


setuptools.setup(
    name='${name}',
    author='Author',
    author_email='author@example.org',
    url='https://example.org',
    % for arg, value in setup_kwargs:
    ${arg}=${repr(value)},
    % endfor
    py_modules=[
        'vcsvertest',
    ],
)
