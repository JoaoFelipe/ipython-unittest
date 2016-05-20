#!/usr/bin/env python
from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    long_description = "Add unittest cell magics to IPython for easily running tests"

setup(
    name="ipython_unittest",
    version="0.0.3",
    description="Add unittest cell magics to IPython for easily running tests",
    long_description=long_description,
    packages=find_packages(exclude=["tests_*", "tests"]),
    author=("Joao Pimentel",),
    author_email="joaofelipenp@gmail.com",
    license="MIT",
    keywords="ipython jupyter unittest tdd dojo",
    url="https://github.com/JoaoFelipe/ipython-unittest"
)
