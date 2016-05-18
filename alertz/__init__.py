# ~/dev/py/alertz/alertz/__init__.py

__version__ = '0.2.5'
__version_date__ = '2016-05-17'

__all__ = ['__version__', '__version_date__',
           'ALERTZ_MAX_MSG', 'ALERTZ_PORT', 'BUFSIZE',
           'Namespace',
           'sOM', 'protoName',
           'ZoneMismatchMsg', 'CorruptListMsg', 'ShutdownMsg',
           ]


from io import StringIO

import fieldz
from fieldz import fieldTypes as F
from fieldz import msgSpec as M
from fieldz import typed as T

from alertzProtoSpec import ALERTZ_PROTO_SPEC
from fieldz.parser import StringProtoSpecParser
from fieldz.chan import Channel
from fieldz.msgImpl import makeMsgClass, makeFieldClass

BUFSIZE = 16 * 1024                   # must allow for all using protocols

# SYNTACTIC MACHINERY -----------------------------------------------
protoText = StringIO(ALERTZ_PROTO_SPEC)       # file-like
p = StringProtoSpecParser(protoText)
sOM = p.parse()                 # object model from string serialization
protoName = sOM.name                  # the dotted name of the protocol

ZoneMismatchMsg = makeMsgClass(sOM, 'zoneMismatch')
CorruptListMsg = makeMsgClass(sOM, 'corruptList')
ShutdownMsg = makeMsgClass(sOM, 'shutdown')

# the maximum number of bytes in a message
ALERTZ_MAX_MSG = 512
ALERTZ_PORT = 55555

# -- NAME SPACE -----------------------------------------------------
# code.activestate.com/recipes/577887-a-simple-namespace-class offers
# a seemingly neat solution, but it just doesn't work


class Namespace(dict):

    def __init__(self, pairs={}):
        super(Namespace, self).__init__(pairs)

    def __getattribute__(self, name):
        try:
            return self[name]
        except KeyError:
            errMsg = "'%s' object has no attribute '%s'" % (
                type(self).__name__, name)
            raise AttributeError(errMsg)

    def __setattr__(self, name, value):
        self[name] = value
