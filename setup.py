#!/usr/bin/env python
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import sys

requires = []
if sys.version_info < (2, 6):
    requires.append('simplejson')

def get_packages(start):
    out = [start]
    out.extend('%s.%s' % (start, p) for p in find_packages(start))
    return out

setup(name=u'Saywah',
      version=u'0.0.1',
      description=u'Microblogging client',
      author=u'Renzo Carbonara',
      author_email=u'gnuk0001@gmail.com',
      url=u'http://github.com/k0001/saywah',
      packages=get_packages('saywah'),
      requires=requires,
 )

