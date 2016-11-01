#!/usr/bin/env python3

# testAlertzSerialization.py
import time
import unittest
from io import StringIO

from rnglib import SimpleRNG

from fieldz.parser import StringProtoSpecParser
from fieldz.field_types import FieldTypes as F, FieldStr as FS
import fieldz.msg_spec as M
import fieldz.typed as T
from fieldz.chan import Channel
from fieldz.msg_impl import make_msg_class, make_field_class, MsgImpl

from alertzProtoSpec import ALERTZ_PROTO_SPEC

BUFSIZE = 16 * 1024
RNG = SimpleRNG(time.time())


class TestAlertzSerialization(unittest.TestCase):

    def setUp(self):
        data = StringIO(ALERTZ_PROTO_SPEC)
        STR_PS_PARSER = StringProtoSpecParser(
            data)   # data should be file-like
        # object model from string serialization
        self.STR_OBJ_MODEL = STR_PS_PARSER.parse()
        self.PROTO_NAME = self.STR_OBJ_MODEL.name  # the dotted name of the protocol

    def tearDown(self):
        pass

    # utility functions #############################################
    def zone_mismatch_fields(self):
        """ returns a list """
        timestamp = RNG.next_int32()
        seq_nbr = RNG.next_int32()
        zone_name = RNG.next_file_name(8)
        expected_serial = RNG.next_int32()
        actual_serial = RNG.next_int32()
        while actual_serial == expected_serial:
            actual_serial = RNG.next_int32()

        # NOTE that this is a list
        return [timestamp, seq_nbr, zone_name, expected_serial, actual_serial]

    def corrupt_list_fields(self):
        timestamp = RNG.next_int32()
        seq_nbr = RNG.next_int32()
        remarks = RNG.next_file_name(16)  # so 1 to 16 characters
        return [timestamp, seq_nbr, remarks]

    # actual unit tests #############################################

    def test_zone_mismatch_msg(self):
        # -----------------------------------------------------------
        # XXX This code has been crudely hacked from another test
        # module, and so needs careful review
        # -----------------------------------------------------------

        # verify that this adds 1 (msg) + 3 (field count) to the number
        # of entries in getters, putters, etc

        self.assertIsNotNone(self.STR_OBJ_MODEL)
        self.assertTrue(isinstance(self.STR_OBJ_MODEL, M.ProtoSpec))
        self.assertEqual('org.xlattice.alertz', self.STR_OBJ_MODEL.name)

        self.assertEqual(0, len(self.STR_OBJ_MODEL.enums))
        self.assertEqual(16, len(self.STR_OBJ_MODEL.msgs))
        self.assertEqual(0, len(self.STR_OBJ_MODEL.seqs))

        msg_spec = self.STR_OBJ_MODEL.msgs[0]
        msg_name = msg_spec.name
        self.assertEqual('zoneMismatch', msg_name)

        # Create a channel ------------------------------------------
        # its buffer will be used for both serializing # the instance
        # data and, by deserializing it, for creating a second instance.
        chan = Channel(BUFSIZE)
        buf = chan.buffer
        self.assertEqual(BUFSIZE, len(buf))

        # create the ZoneMismatchMsg class ------------------------------
        ZoneMismatchMsg = make_msg_class(self.STR_OBJ_MODEL, msg_name)

        # create a message instance ---------------------------------
        values = self.zone_mismatch_fields()        # list of quasi-random values
        zmm_msg = ZoneMismatchMsg(values)

        self.assertEqual(msg_spec.name, zmm_msg._name)
        # we don't have any nested enums or messages
        self.assertEqual(0, len(zmm_msg.enums))
        self.assertEqual(0, len(zmm_msg.msgs))

        self.assertEqual(5, len(zmm_msg.field_classes))
        self.assertEqual(5, len(zmm_msg))        # number of fields in instance
        self.assertEqual(values[0], zmm_msg.timestamp)
        self.assertEqual(values[1], zmm_msg.seq_nbr)
        self.assertEqual(values[2], zmm_msg.zone_name)
        self.assertEqual(values[3], zmm_msg.expected_serial)
        self.assertEqual(values[4], zmm_msg.actual_serial)

        # serialize the object to the channel -----------------------

        # XXX WRITE HEADER FIRST!

        # DEBUG
        print("DIR (ZMM_MSG): ", end=' ')
        print(dir(zmm_msg))
        # END
        zmm_msg.write_stand_alone(chan)
        chan.flip()

        # deserialize the channel, making a clone of the message ----
        (read_back, nn2) = MsgImpl.read(chan, self.STR_OBJ_MODEL)
        self.assertIsNotNone(read_back)

        # DEBUG
        print("position after mis-match read back is %d" % chan.position)
        # END

        # verify that the messages are identical --------------------
        self.assertTrue(zmm_msg.__eq__(read_back))

        # produce another message from the same values --------------
        zmm_msg2 = ZoneMismatchMsg(values)
        chan2 = Channel(BUFSIZE)
        zmm_msg2.write_stand_alone(chan2)
        chan2.flip()

        (copy2, nn3) = MsgImpl.read(chan2, self.STR_OBJ_MODEL)
        self.assertTrue(zmm_msg.__eq__(copy2))
        self.assertTrue(zmm_msg2.__eq__(copy2))       # GEEP

    def test_corrupt_list_msg(self):
        # -----------------------------------------------------------
        # XXX This code has been crudely hacked from another test
        # module, and so needs careful review
        # -----------------------------------------------------------

        # verify that this adds 1 (msg) + 3 (field count) to the number
        # of entries in getters, writeStandAlones, etc

        msg_spec = self.STR_OBJ_MODEL.msgs[1]          # <------
        msg_name = msg_spec.name
        self.assertEqual('corruptZoneList', msg_name)

        # Create a channel ------------------------------------------
        # its buffer will be used for both serializing # the instance
        # data and, by deserializing it, for creating a second instance.
        chan = Channel(BUFSIZE)
        buf = chan.buffer
        self.assertEqual(BUFSIZE, len(buf))

        # create the CorruptListMsg class ------------------------------
        CorruptListMsg = make_msg_class(self.STR_OBJ_MODEL, msg_name)

        # create a message instance ---------------------------------
        values = self.corrupt_list_fields()        # list of quasi-random values
        cl_msg = CorruptListMsg(values)

        self.assertEqual(msg_spec.name, cl_msg._name)
        # we don't have any nested enums or messages
        self.assertEqual(0, len(cl_msg.enums))
        self.assertEqual(0, len(cl_msg.msgs))

        self.assertEqual(3, len(cl_msg.field_classes))   # <---
        self.assertEqual(3, len(cl_msg))        # number of fields in instance
        self.assertEqual(values[0], cl_msg.timestamp)
        self.assertEqual(values[1], cl_msg.seq_nbr)
        self.assertEqual(values[2], cl_msg.remarks)

        # serialize the object to the channel -----------------------
        cl_msg.write_stand_alone(chan)
        chan.flip()

        # deserialize the channel, making a clone of the message ----
        (read_back, nn4) = MsgImpl.read(chan, self.STR_OBJ_MODEL)
        self.assertIsNotNone(read_back)

        # DEBUG
        print("position after corrupt list read back is %d" % chan.position)
        # END

        # verify that the messages are identical --------------------
        self.assertTrue(cl_msg.__eq__(read_back))

        # produce another message from the same values --------------
        cl_msg2 = CorruptListMsg(values)
        chan2 = Channel(BUFSIZE)
        cl_msg2.write_stand_alone(chan2)
        chan2.flip()

        (copy2, nn4) = MsgImpl.read(chan2, self.STR_OBJ_MODEL)
        self.assertTrue(cl_msg.__eq__(copy2))
        self.assertTrue(cl_msg2.__eq__(copy2))       # GEEP

    def testShutdownMsg(self):
        # -----------------------------------------------------------
        # XXX This code has been crudely hacked from another test
        # module, and so needs careful review
        # -----------------------------------------------------------

        # verify that this adds 1 (msg) + 3 (field count) to the number
        # of entries in getters, writeStandAlones, etc

        msg_spec = self.STR_OBJ_MODEL.msgs[2]          # <------
        msg_name = msg_spec.name
        self.assertEqual('shutdown', msg_name)

        # Create a channel ------------------------------------------
        # its buffer will be used for both serializing # the instance
        # data and, by deserializing it, for creating a second instance.
        chan = Channel(BUFSIZE)
        buf = chan.buffer
        self.assertEqual(BUFSIZE, len(buf))

        # create the CorruptListMsg class ------------------------------
        SHUTDOWN_MSG = make_msg_class(self.STR_OBJ_MODEL, msg_name)

        # create a message instance ---------------------------------
        values = [RNG.next_file_name(8), ]  # list of quasi-random values
        sd_msg = SHUTDOWN_MSG(values)

        self.assertEqual(msg_name, sd_msg._name)
        # we don't have any nested enums or messages
        self.assertEqual(0, len(sd_msg.enums))
        self.assertEqual(0, len(sd_msg.msgs))

        self.assertEqual(1, len(sd_msg.field_classes))   # <---
        self.assertEqual(1, len(sd_msg))        # number of fields in instance
        self.assertEqual(values[0], sd_msg.remarks)

        # serialize the object to the channel -----------------------
        sd_msg.write_stand_alone(chan)
        chan.flip()

        # deserialize the channel, making a clone of the message ----
        (read_back, nn5) = MsgImpl.read(chan, self.STR_OBJ_MODEL)
        self.assertIsNotNone(read_back)

        # DEBUG
        print("position after shutdown read back is %d" % chan.position)
        # END

        # verify that the messages are identical --------------------
        self.assertTrue(sd_msg.__eq__(read_back))

        # produce another message from the same values --------------
        sd_msg2 = SHUTDOWN_MSG(values)
        chan2 = Channel(BUFSIZE)
        sd_msg2.write_stand_alone(chan2)
        chan2.flip()

        (copy2, nn6) = MsgImpl.read(chan2, self.STR_OBJ_MODEL)
        self.assertTrue(sd_msg.__eq__(copy2))
        self.assertTrue(sd_msg2.__eq__(copy2))       # GEEP


if __name__ == '__main__':
    unittest.main()
