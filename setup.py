#!/usr/bin/env python
from distutils.core import setup
from fiftystates import __version__

long_description = open('README.rst').read()

setup(name="python-fiftystates",
      version=__version__,
      py_modules=["fiftystates"],
      description="Library for interacting with the Fifty State Project API",
      author="Michael Stephens",
      author_email="mstephens@sunlightfoundation.com",
      license="BSD",
      url="http://github.com/sunlightlabs/python-fiftystates",
      long_description=long_description,
      platforms=["any"],
      classifiers=["Development Status :: 4 - Beta",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: BSD License",
                   "Natural Language :: English",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   ],
      install_requires=["simplejson >= 1.8",
                        "remoteobjects >= 1.1"]
      )
