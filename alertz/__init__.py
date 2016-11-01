# ~/dev/py/alertz/alertz/__init__.py

"""
Alert message system.
"""

from io import StringIO

import fieldz
from fieldz.field_types import FieldTypes as F, FieldStr as FS
from fieldz import msg_spec as M
from fieldz import typed as T

from alertzProtoSpec import ALERTZ_PROTO_SPEC
from fieldz.parser import StringProtoSpecParser
from fieldz.chan import Channel
from fieldz.msg_impl import make_msg_class, make_field_class

__all__ = ['__version__', '__version_date__',
           'ALERTZ_MAX_MSG', 'ALERTZ_PORT', 'BUFSIZE',
           'Namespace',
           'STR_OBJ_MODEL', 'PROTO_NAME',
           'ZoneMismatchMsg', 'CorruptListMsg', 'SHUTDOWN_MSG',
           ]

__version__ = '0.2.10'
__version_date__ = '2016-11-01'

BUFSIZE = 16 * 1024                   # must allow for all using protocols

# SYNTACTIC MACHINERY -----------------------------------------------
PROTO_TEXT = StringIO(ALERTZ_PROTO_SPEC)       # file-like
STR_PS_PARSER = StringProtoSpecParser(PROTO_TEXT)
# object model from string serialization
STR_OBJ_MODEL = STR_PS_PARSER.parse()
# the dotted name of the protocol
PROTO_NAME = STR_OBJ_MODEL.name

ZoneMismatchMsg = make_msg_class(STR_OBJ_MODEL, 'zoneMismatch')
CorruptListMsg = make_msg_class(STR_OBJ_MODEL, 'corruptList')
SHUTDOWN_MSG = make_msg_class(STR_OBJ_MODEL, 'shutdown')

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
            err_msg = "'%s' object has no attribute '%s'" % (
                type(self).__name__, name)
            raise AttributeError(err_msg)

    def __setattr__(self, name, value):
        self[name] = value
