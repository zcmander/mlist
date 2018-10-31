#!/usr/bin/env python
from setuptools import setup, find_packages

setup(name='mlist',
      version='0.41',
      install_requires=[          
          'django',
          'django-crispy-forms',
          'django-ember',
          'django-tastypie',
          'django-taggit',
          'django-debug-toolbar',
          'requests',
          'Whoosh',
          'mimeparse',
          'pytz',
          'django-haystack',
          'simplejson',
          'pylint-django',
          'unicodecsv',
      ],
      packages=find_packages(),
      scripts=['manage.py'])
