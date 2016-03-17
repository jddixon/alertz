#!/usr/bin/python3

# ~/dev/py/alertz/setup.py

import re
from distutils.core import setup
__version__ = re.search("__version__\s*=\s*'(.*)'",
                        open('alertz/__init__.py').read()).group(1)

# see http://docs.python.org/distutils/setupscript.html

setup(name='alertz',
      version=__version__,
      author='Jim Dixon',
      author_email='jddixon@gmail.com',
      #
      # wherever we have a .py file that will be imported, we
      # list it here, without the extension but SQuoted
      py_modules=['alertzProtoSpec'],
      #
      # a package has a subdir and an __init__.py
      packages=['alertz', ],
      #
      # following could be in scripts/ subdir; SQuote
      scripts=['alertzd', ],
      # MISSING url
      )
