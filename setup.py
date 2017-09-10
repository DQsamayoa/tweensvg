"""
Setup script for TweenSVG
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='TweenSVG',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.1.0a1',

    description='A library for tweening pairs of Scalable Vector Graphics (SVG) files',
    long_description=long_description,

    # The project's main homepage.
    #url='TODO',

    # Author details
    author='Daniel Bailey',
    author_email='tweensvg-d@nielbailey.com',

    # Choose your license
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',

        'License :: OSI Approved :: MIT License',

        # TODO - Aiming to support all of python 3, test if they are all supported
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Operating System :: OS Independent',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',
    ],

    keywords='SVG tween tweening',

    packages=['TweenSVG'], #find_packages(exclude=['contrib', 'docs', 'tests']),

    install_requires=[
        'defusedxml>=0.5.0'
    ],

    python_requires='~=3.0',

    # TODO - Might need some of these later
    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    #extras_require={
    #    'dev': ['check-manifest'],
    #    'test': ['coverage'],
    #},

)
