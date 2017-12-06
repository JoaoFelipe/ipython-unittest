#!/usr/bin/env python
"""Setup script"""
import os
from setuptools import setup, find_packages


def recursive_path(pack, path):
    """Find paths recursively"""
    matches = []
    for root, _, filenames in os.walk(os.path.join(pack, path)):
        for filename in filenames:
            matches.append(os.path.join(root, filename)[len(pack) + 1:])
    return matches


try:
    import pypandoc
    LONG = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    LONG = "Add unittest cell magics to IPython for easily running tests"

setup(
    name="ipython_unittest",
    version="0.3.1",
    description="Add unittest cell magics to IPython for easily running tests",
    long_description=LONG,
    packages=find_packages(exclude=["tests_*", "tests"]),
    package_data={
        "ipython_unittest": recursive_path("ipython_unittest", "resources")},
    author=("Joao Pimentel",),
    author_email="joaofelipenp@gmail.com",
    license="MIT",
    keywords="ipython jupyter unittest tdd dojo",
    url="https://github.com/JoaoFelipe/ipython-unittest"
)
