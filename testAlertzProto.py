#!/usr/bin/python3

# ~/dev/py/fieldz/testAlertzProto.py

import time
import unittest
from io import StringIO

# import fieldz
from fieldz import parser

from fieldz.parser import StringProtoSpecParser
import fieldz.fieldTypes as F
import fieldz.msgSpec as M
import fieldz.typed as T
import fieldz.reg as R

from fieldz import reg

# PROTOCOLS ---------------------------------------------------------
from alertzProtoSpec import ALERTZ_PROTO_SPEC

# TESTS -------------------------------------------------------------


class TestAlertzProto (unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # actual unit tests #############################################

    def testAlertzProto(self):
        """ this is in fact the current spec for a log entry """
        protoName = 'org.xlattice.alertz'
        nodeReg = R.NodeReg()
        protoReg = R.ProtoReg(protoName, nodeReg)
        msgReg = R.MsgReg(protoReg)
        protoSpec = M.ProtoSpec(protoName, protoReg)
        self.assertEqual(protoName, protoSpec.name)

        msgName = 'zoneMismatch'

        fields = [
            M.FieldSpec(msgReg, 'timestamp', F._F_UINT32, M.Q_REQUIRED, 0),
            M.FieldSpec(msgReg, 'seqNbr', F._V_UINT32, M.Q_REQUIRED, 1),
            M.FieldSpec(msgReg, 'zoneName', F._L_STRING, M.Q_REQUIRED, 2),
            M.FieldSpec(
                msgReg,
                'expectedSerial',
                F._V_UINT32,
                M.Q_REQUIRED,
                3),
            M.FieldSpec(msgReg, 'actualSerial', F._V_UINT32, M.Q_REQUIRED, 4),
        ]
        msgSpec = M.MsgSpec(msgName, protoSpec, msgReg)
        self.assertEqual(msgName, msgSpec.name)
        for f in fields:
            msgSpec.addField(f)

        # protoSpec.addMsg(msgSpec)     # ALREADY DONE in __init__
        self.roundTripProtoSpecViaString(protoSpec)             # GEEP

    def roundTripProtoSpecViaString(self, m):
        """
        Convert a MsgSpec object model to canonical string form,
        parse that to make a clone, and verify that the two are
        """
        canonicalSpec = str(m.__repr__())
        # DEBUG
        print("### roundTrip: SPEC IN CANONICAL FORM:\n" + canonicalSpec)
        print("### END SPEC IN CANONICAL FORM #######")
        # END
        p = StringProtoSpecParser(StringIO(canonicalSpec))
        clonedSpec = p.parse()
        self.assertIsNone(clonedSpec.parent)
        self.assertIsNotNone(clonedSpec.reg)

        # DEBUG
        cloneRepr = clonedSpec.__repr__()
        print("### CLONED SPEC IN CANONICAL FORM:\n" + cloneRepr)
        print("### END CLONED SPEC ##############")
        # END

        # crude tests of __eq__ AKA ==
        self.assertFalse(m is None)
        self.assertTrue(m == m)

        # one way of saying it ------------------
        # XXX NEXT LINE FAILS
        self.assertTrue(m.__eq__(clonedSpec))

        self.assertTrue(clonedSpec.__eq__(m))
        # this is the same test -----------------
        self.assertTrue(m == clonedSpec)
        self.assertTrue(clonedSpec == m)

    def testParseAndWriteProtoSpec(self):
        data = StringIO(ALERTZ_PROTO_SPEC)
        p = StringProtoSpecParser(data)   # data should be file-like
        sOM = p.parse()             # object model from string serialization
        self.assertIsNotNone(sOM)
        self.assertTrue(isinstance(sOM, M.ProtoSpec))
        self.assertEqual('org.xlattice.alertz', sOM.name)
        self.assertEqual(0, len(sOM.enums))
        self.assertEqual(16, len(sOM.msgs))
        self.assertEqual(0, len(sOM.seqs))

        msgSpec = sOM.msgs[0]
        self.assertEqual(msgSpec.fName(0), 'timestamp')
        self.assertEqual(msgSpec.fTypeName(0), 'fuInt32')
        self.assertEqual(msgSpec.fName(1), 'seqNbr')
        self.assertEqual(msgSpec.fTypeName(1), 'vuInt32')

        self.assertEqual(msgSpec.fName(2), 'zoneName')
        self.assertEqual(msgSpec.fTypeName(2), 'lString')
        self.assertEqual(msgSpec.fName(3), 'expectedSerial')
        self.assertEqual(msgSpec.fTypeName(3), 'vuInt32')
        self.assertEqual(msgSpec.fName(4), 'actualSerial')
        self.assertEqual(msgSpec.fTypeName(4), 'vuInt32')

if __name__ == '__main__':
    unittest.main()
