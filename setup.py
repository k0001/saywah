#!/usr/bin/env python
try:
    from setuptools import setup, find_packages
except ImportError:
    from distribute_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import sys

def get_requires():
    requires = ['httplib2', 'louie']
    if sys.version_info < (2, 6):
        requires.append('simplejson')
    return requires

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
      requires=get_requires(),
      scripts=['scripts/saywah']
 )

