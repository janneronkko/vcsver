import setuptools

import setuptools_autover


with open('README.rst', 'rt') as readme_file:
    long_desc = readme_file.read()

setuptools.setup(
    name='setuptools_autover',
    version=setuptools_autover.get_version(),
    description='Automatic package version numbering from version control',
    long_description=long_desc,
    long_description_content_type='text/x-rst',
    url='https://github.com/jannero/setuptools_autover',
    author='Janne Rönkkö',
    author_email='janne.ronkko@iki.fi',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
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
    packages=['setuptools_autover'],
    python_requires='>=3.5',
    entry_points={
        'distutils.setup_keywords': [
            'version = setuptools_autover.autover:handle_version',
            'use_autover = setuptools_autover.autover:handle_use_autover',
        ],
    },
)
