#!/usr/bin/env python

from setuptools import find_packages, setup

setup(
    name="Pydatpiff",
    version="2.0.0",
    author="cbedroid",
    author_email="cbedroid1614@example.com",
    url="https://pypi.org/project/pydatpiff/",
    description="Unofficial Datpiff Mixtape player - Download and play the newest Hip-Hop and RnB Songs.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    packages=find_packages(
        where=".",
        include=["pydatpiff*"],  # ["*"] by default
        exclude=["pydatpiff.tests"],  # empty by default
    ),
    tests_require=["pytest==5.2.4"],
    install_requires=open("requirements.txt").readlines(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Multimedia :: Sound/Audio :: Players",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    zip_safe=False,
)
