#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name="Pydatpiff",
    version="2.0.0",
    author="cbedroid",
    author_email="cbedroid1614@example.com",
    packages=find_packages(
        where=".",
        include=["pydatpiff*"],  # ["*"] by default
        exclude=["pydatpiff.tests"],  # empty by default
    ),
    url="https://pypi.org/project/pydatpiff/",
    license="LICENSE",
    description="Unofficial Datpiff Mixtape player - Download and play the newest Hip-Hop and RnB Songs.",
    long_description=open("README.md").read(),
    install_requires=open("requirements.txt").read(),
)
