#!/usr/bin/env python
import os
from setuptools import setup, find_packages


def recursive_path(pack, path):
    matches = []
    for root, dirnames, filenames in os.walk(os.path.join(pack, path)):
        for filename in filenames:
            matches.append(os.path.join(root, filename)[len(pack) + 1:])
    return matches


try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    long_description = "Add unittest cell magics to IPython for easily running tests"

setup(
    name="ipython_unittest",
    version="0.2.4",
    description="Add unittest cell magics to IPython for easily running tests",
    long_description=long_description,
    packages=find_packages(exclude=["tests_*", "tests"]),
    package_data={
        "ipython_unittest": recursive_path("ipython_unittest", "resources")},
    author=("Joao Pimentel",),
    author_email="joaofelipenp@gmail.com",
    license="MIT",
    keywords="ipython jupyter unittest tdd dojo",
    url="https://github.com/JoaoFelipe/ipython-unittest"
)
