#!/usr/bin/env python3

# ~/dev/py/fieldz/testAlertzProto.py

import time
import unittest
from io import StringIO

# import fieldz
from fieldz import parser

from fieldz.parser import StringProtoSpecParser
from fieldz.field_types import FieldTypes as F, FieldStr as FS
import fieldz.msg_spec as M
import fieldz.typed as T
import fieldz.reg as R

from fieldz import reg

# PROTOCOLS ---------------------------------------------------------
from alertzProtoSpec import ALERTZ_PROTO_SPEC

# TESTS -------------------------------------------------------------


class TestAlertzProto(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # actual unit tests #############################################

    def testAlertzProto(self):
        """ this is in fact the current spec for a log entry """
        PROTO_NAME = 'org.xlattice.alertz'
        node_reg = R.NodeReg()
        proto_reg = R.ProtoReg(PROTO_NAME, node_reg)
        msgReg = R.MsgReg(proto_reg)
        proto_spec = M.ProtoSpec(PROTO_NAME, proto_reg)
        self.assertEqual(PROTO_NAME, proto_spec.name)

        msg_name = 'zoneMismatch'

        fields = [
            M.FieldSpec(msgReg, 'timestamp', F.F_UINT32, M.Q_REQUIRED, 0),
            M.FieldSpec(msgReg, 'seq_nbr', F.V_UINT32, M.Q_REQUIRED, 1),
            M.FieldSpec(msgReg, 'zone_name', F.L_STRING, M.Q_REQUIRED, 2),
            M.FieldSpec(
                msgReg,
                'expected_serial',
                F.V_UINT32,
                M.Q_REQUIRED,
                3),
            M.FieldSpec(msgReg, 'actual_serial', F.V_UINT32, M.Q_REQUIRED, 4),
        ]
        msg_spec = M.MsgSpec(msg_name, proto_spec, msgReg)
        self.assertEqual(msg_name, msg_spec.name)
        for file in fields:
            msg_spec.add_field(file)

        # This is supposedly already done in __init__()
        proto_spec.add_msg(msg_spec)

        self.roundTripProtoSpecViaString(proto_spec)             # GEEP

    def roundTripProtoSpecViaString(self, match):
        """
        Convert a MsgSpec object model to canonical string form,
        parse that to make a clone, and verify that the two are
        """
        canonical_spec = str(match.__repr__())
        # DEBUG
        print("### roundTrip: SPEC IN CANONICAL FORM:\n" + canonical_spec)
        print("### END SPEC IN CANONICAL FORM #######")
        # END
        STR_PS_PARSER = StringProtoSpecParser(StringIO(canonical_spec))
        cloned_spec = STR_PS_PARSER.parse()
        self.assertIsNone(cloned_spec.parent)
        self.assertIsNotNone(cloned_spec.reg)

        # DEBUG
        clone_repr = cloned_spec.__repr__()
        print("### CLONED SPEC IN CANONICAL FORM:\n" + clone_repr)
        print("### END CLONED SPEC ##############")
        # END

        # crude tests of __eq__ AKA ==
        self.assertFalse(match is None)
        self.assertTrue(match == match)

        # one way of saying it ------------------
        # XXX NEXT LINE FAILS
        self.assertTrue(match.__eq__(cloned_spec))

        self.assertTrue(cloned_spec.__eq__(match))
        # this is the same test -----------------
        self.assertTrue(match == cloned_spec)
        self.assertTrue(cloned_spec == match)

    def test_parse_and_write_proto_spec(self):
        data = StringIO(ALERTZ_PROTO_SPEC)
        STR_PS_PARSER = StringProtoSpecParser(
            data)   # data should be file-like
        # object model from string serialization
        STR_OBJ_MODEL = STR_PS_PARSER.parse()
        self.assertIsNotNone(STR_OBJ_MODEL)
        self.assertTrue(isinstance(STR_OBJ_MODEL, M.ProtoSpec))
        self.assertEqual('org.xlattice.alertz', STR_OBJ_MODEL.name)
        self.assertEqual(0, len(STR_OBJ_MODEL.enums))
        self.assertEqual(16, len(STR_OBJ_MODEL.msgs))
        self.assertEqual(0, len(STR_OBJ_MODEL.seqs))

        msg_spec = STR_OBJ_MODEL.msgs[0]
        self.assertEqual(msg_spec.field_name(0), 'timestamp')
        self.assertEqual(msg_spec.field_type_name(0), 'fuint32')
        self.assertEqual(msg_spec.field_name(1), 'seq_nbr')
        self.assertEqual(msg_spec.field_type_name(1), 'vuint32')

        self.assertEqual(msg_spec.field_name(2), 'zone_name')
        self.assertEqual(msg_spec.field_type_name(2), 'lstring')
        self.assertEqual(msg_spec.field_name(3), 'expected_serial')
        self.assertEqual(msg_spec.field_type_name(3), 'vuint32')
        self.assertEqual(msg_spec.field_name(4), 'actual_serial')
        self.assertEqual(msg_spec.field_type_name(4), 'vuint32')

if __name__ == '__main__':
    unittest.main()
