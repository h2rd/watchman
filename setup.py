#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='watchman',
    author='Igor Skrynkovskyy',
    author_email='skrynkovskyy@gmail.com',
    description='Watchman',
    long_description=long_description,
    license="MIT",
    url='http://github/h2rd/watchman',
    version='0.1.0',
    py_modules=['watchman'],
    entry_points={ 'console_scripts': ['watchman = watchman:main'] },
    install_requires=['requests']
)
