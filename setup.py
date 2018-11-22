#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='mlist',
      version='0.41',
      install_requires=[
          # Django
          'django',
          'django-crispy-forms',
          'django-tastypie',
          'django-taggit',
          'django-debug-toolbar',
          'django-haystack',

          # Other required libraries
          'requests',
          'Whoosh',
          'mimeparse',
          'pytz',
          'simplejson',
          'unicodecsv',

          # Code quality
          'flake8',
          'mock',
          'coverage',

          # CI/CD
          'coveralls'
      ],
      packages=find_packages(),
      scripts=['manage.py'])
