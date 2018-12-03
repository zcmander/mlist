#!/usr/bin/env python
from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(name='mlist',
      version='0.41',
      install_requires=requirements,
      packages=find_packages(),
      scripts=['manage.py'])
