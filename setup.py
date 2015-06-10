#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2015 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


import os
from setuptools import setup, find_packages


THISDIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(THISDIR)


VERSION = open("version.txt").readline().strip()
DOWNLOAD_BASEURL = "https://pypi.python.org/packages/source/a/btctxstore/"
DOWNLOAD_URL = DOWNLOAD_BASEURL + "btctxstore-%s.tar.gz" % VERSION


setup(
    name='btctxstore',
    version=VERSION,
    description=('Library to read/write data to bitcoin transaction outputs.'),
    long_description=open("README.rst").read(),
    keywords=("Bitcoin, OP_RETURN, store, tx, transaction"),
    url='https://github.com/F483/btctxstore/',
    author='Fabian Barkhau',
    author_email='fabian.barkhau@gmail.com',
    license='MIT',
    packages=find_packages(),
    download_url = DOWNLOAD_URL,
    test_suite="tests",
    install_requires=[
        'pycoin == 0.52',
        'six == 1.9.0',
        'ecdsa'
    ],
    tests_require=[
        'coverage',
        'coveralls',
        'ipython',
        'pudb'  # import pudb; pu.db # set break point
    ],
    zip_safe=False,
    classifiers=[
        # "Development Status :: 1 - Planning",
        # "Development Status :: 2 - Pre-Alpha",
        # "Development Status :: 3 - Alpha",
        "Development Status :: 4 - Beta",
        # "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
